"""
Image Quality Assessment using Computer Vision
Filters out logos, blurry images, and low-quality content images
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class ImageQualityAssessor:
    """
    Advanced Computer Vision-based image quality assessment
    Detects and filters out:
    - Blurry images (Laplacian variance)
    - Logos and icons (limited color palette)
    - Low-contrast images
    - Small/low-quality images
    """

    # Thresholds
    BLUR_THRESHOLD = 100.0  # Laplacian variance - images below are blurry
    MIN_COLOR_DIVERSITY = 1000  # Unique colors - images below are likely logos
    MIN_EDGE_DENSITY = 0.05  # Edge density - photos have >5% edge pixels
    MIN_BRIGHTNESS = 40  # Too dark
    MAX_BRIGHTNESS = 220  # Too bright/washed out
    MIN_CONTRAST = 30  # Standard deviation of brightness

    @staticmethod
    def assess_sharpness(image_path: Path) -> Dict:
        """
        Detect blurry images using Laplacian variance

        Laplacian operator detects edges and rapid intensity changes.
        Blurry images have low variance (fewer sharp edges).

        Returns:
            dict: {
                'laplacian_variance': float,
                'is_sharp': bool,
                'sharpness_score': float (0-1)
            }
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                logger.warning(f"Could not read image for sharpness: {image_path}")
                return {
                    'laplacian_variance': 0,
                    'is_sharp': False,
                    'sharpness_score': 0.0
                }

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Calculate Laplacian variance (measures image sharpness)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            return {
                'laplacian_variance': laplacian_var,
                'is_sharp': laplacian_var >= ImageQualityAssessor.BLUR_THRESHOLD,
                'sharpness_score': min(laplacian_var / 200.0, 1.0)  # Normalize to 0-1
            }
        except Exception as e:
            logger.error(f"Error assessing sharpness: {e}")
            return {
                'laplacian_variance': 0,
                'is_sharp': False,
                'sharpness_score': 0.0
            }

    @staticmethod
    def assess_color_diversity(image_path: Path) -> Dict:
        """
        Detect logos and icons by analyzing color palette

        Logos typically have:
        - Limited color palette (<1000 unique colors)
        - One dominant color (>40% of pixels)
        - Flat appearance

        Returns:
            dict: {
                'unique_colors': int,
                'dominant_color_ratio': float,
                'is_diverse': bool,
                'is_likely_logo': bool
            }
        """
        try:
            img = Image.open(image_path)

            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Count unique colors
            colors = img.getcolors(maxcolors=10000)

            if colors is None:
                # More than 10000 colors - definitely a photo
                return {
                    'unique_colors': 10000,
                    'dominant_color_ratio': 0.0,
                    'is_diverse': True,
                    'is_likely_logo': False
                }

            unique_colors = len(colors)

            # Calculate dominant color ratio
            total_pixels = img.width * img.height
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)
            dominant_color_ratio = sorted_colors[0][0] / total_pixels if sorted_colors else 0

            return {
                'unique_colors': unique_colors,
                'dominant_color_ratio': dominant_color_ratio,
                'is_diverse': unique_colors >= ImageQualityAssessor.MIN_COLOR_DIVERSITY,
                'is_likely_logo': unique_colors < 500 or dominant_color_ratio > 0.4
            }
        except Exception as e:
            logger.error(f"Error assessing color diversity: {e}")
            return {
                'unique_colors': 0,
                'dominant_color_ratio': 1.0,
                'is_diverse': False,
                'is_likely_logo': True
            }

    @staticmethod
    def detect_edges(image_path: Path) -> Dict:
        """
        Measure edge complexity

        Photos have complex scenes with many edges (>5% edge density)
        Simple graphics, logos, and UI elements have few edges (<2%)

        Returns:
            dict: {
                'edge_density': float,
                'is_complex': bool,
                'edge_score': float (0-1)
            }
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {
                    'edge_density': 0.0,
                    'is_complex': False,
                    'edge_score': 0.0
                }

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Canny edge detection
            edges = cv2.Canny(gray, 100, 200)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

            return {
                'edge_density': edge_density,
                'is_complex': edge_density > ImageQualityAssessor.MIN_EDGE_DENSITY,
                'edge_score': min(edge_density / 0.15, 1.0)  # Normalize
            }
        except Exception as e:
            logger.error(f"Error detecting edges: {e}")
            return {
                'edge_density': 0.0,
                'is_complex': False,
                'edge_score': 0.0
            }

    @staticmethod
    def assess_brightness_contrast(image_path: Path) -> Dict:
        """
        Detect washed out or too dark images

        Well-exposed images have:
        - Mean brightness: 40-220 (out of 255)
        - Good contrast: std deviation >30

        Returns:
            dict: {
                'mean_brightness': float,
                'contrast': float,
                'is_well_exposed': bool,
                'has_contrast': bool
            }
        """
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {
                    'mean_brightness': 0,
                    'contrast': 0,
                    'is_well_exposed': False,
                    'has_contrast': False
                }

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            mean_brightness = np.mean(gray)
            std_brightness = np.std(gray)

            return {
                'mean_brightness': mean_brightness,
                'contrast': std_brightness,
                'is_well_exposed': ImageQualityAssessor.MIN_BRIGHTNESS < mean_brightness < ImageQualityAssessor.MAX_BRIGHTNESS,
                'has_contrast': std_brightness > ImageQualityAssessor.MIN_CONTRAST
            }
        except Exception as e:
            logger.error(f"Error assessing brightness/contrast: {e}")
            return {
                'mean_brightness': 0,
                'contrast': 0,
                'is_well_exposed': False,
                'has_contrast': False
            }

    @classmethod
    def comprehensive_assessment(cls, image_path: Path) -> Dict:
        """
        Full quality check combining all metrics

        Composite score (0-100):
        - Sharpness: 30% weight
        - Color diversity: 25% weight
        - Edge complexity: 25% weight
        - Exposure quality: 20% weight

        Args:
            image_path: Path to image file

        Returns:
            dict: {
                'overall_score': float (0-100),
                'is_acceptable': bool (score >= 50),
                'quality_tier': str ('high', 'medium', 'low'),
                'rejection_reasons': list[str],
                'sharpness': dict,
                'color': dict,
                'edges': dict,
                'exposure': dict
            }
        """
        logger.debug(f"Assessing image quality: {image_path.name}")

        # Run all assessments
        sharpness = cls.assess_sharpness(image_path)
        color = cls.assess_color_diversity(image_path)
        edges = cls.detect_edges(image_path)
        exposure = cls.assess_brightness_contrast(image_path)

        # Calculate composite score (0-100)
        score = (
            sharpness['sharpness_score'] * 30 +  # 30% weight
            (1.0 if color['is_diverse'] else 0.0) * 25 +  # 25% weight
            edges['edge_score'] * 25 +  # 25% weight
            (1.0 if exposure['is_well_exposed'] and exposure['has_contrast'] else 0.5) * 20  # 20% weight
        )

        # Determine quality tier
        if score >= 75:
            quality_tier = 'high'
        elif score >= 50:
            quality_tier = 'medium'
        else:
            quality_tier = 'low'

        # Collect rejection reasons
        rejection_reasons = []

        if not sharpness['is_sharp']:
            rejection_reasons.append(f"Blurry (Laplacian: {sharpness['laplacian_variance']:.1f})")

        if color['is_likely_logo']:
            rejection_reasons.append(f"Likely logo ({color['unique_colors']} colors, {color['dominant_color_ratio']:.1%} dominant)")

        if not edges['is_complex']:
            rejection_reasons.append(f"Low complexity (edge density: {edges['edge_density']:.2%})")

        if not exposure['is_well_exposed']:
            rejection_reasons.append(f"Poor exposure (brightness: {exposure['mean_brightness']:.1f})")

        if not exposure['has_contrast']:
            rejection_reasons.append(f"Low contrast (std: {exposure['contrast']:.1f})")

        is_acceptable = score >= 50.0 and not color['is_likely_logo']

        result = {
            'overall_score': round(score, 2),
            'is_acceptable': is_acceptable,
            'quality_tier': quality_tier,
            'rejection_reasons': rejection_reasons,
            'sharpness': sharpness,
            'color': color,
            'edges': edges,
            'exposure': exposure
        }

        # Log result
        if is_acceptable:
            logger.info(f"✓ Image ACCEPTED - Score: {score:.1f} ({quality_tier}) - {image_path.name}")
        else:
            logger.warning(f"✗ Image REJECTED - Score: {score:.1f} - Reasons: {', '.join(rejection_reasons)} - {image_path.name}")

        return result

    @staticmethod
    def is_likely_logo(image_path: Path, url: str = "") -> float:
        """
        Calculate probability (0.0-1.0) that image is a logo

        Combines URL patterns and image analysis

        Args:
            image_path: Path to image file
            url: Original image URL (optional)

        Returns:
            float: Probability 0.0-1.0 (1.0 = definitely logo)
        """
        indicators_triggered = 0
        total_indicators = 6

        # URL-based indicators
        if url:
            logo_keywords = ['logo', 'icon', 'brand', 'emblem', 'sprite']
            if any(keyword in url.lower() for keyword in logo_keywords):
                indicators_triggered += 2  # Strong signal

            if '.svg' in url.lower():
                return 1.0  # SVG = almost certainly logo

        try:
            img = Image.open(image_path)
            w, h = img.size

            # Square aspect ratio + small size
            aspect_ratio = w / h
            if 0.9 <= aspect_ratio <= 1.1 and (w < 600 or h < 600):
                indicators_triggered += 2

            # Limited colors
            colors = img.getcolors(maxcolors=10000)
            if colors and len(colors) < 500:
                indicators_triggered += 1

            # Transparency (common in logos)
            if img.mode in ['RGBA', 'LA', 'P']:
                indicators_triggered += 1

            return indicators_triggered / total_indicators

        except Exception as e:
            logger.error(f"Error in logo detection: {e}")
            return 0.5  # Unknown
