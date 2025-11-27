"""
Image Quality Assessment using PIL only (no OpenCV required)
Lightweight version for serverless/Railway deployment
"""
from PIL import Image, ImageFilter, ImageStat
from pathlib import Path
from typing import Dict, Optional
from loguru import logger


class ImageQualityAssessor:
    """
    Lightweight image quality assessment using PIL only
    Detects and filters out:
    - Logos and icons (limited color palette)
    - Small/low-quality images
    - Low-contrast images
    """

    # Thresholds
    MIN_COLOR_DIVERSITY = 1000  # Unique colors - images below are likely logos
    MIN_WIDTH = 300
    MIN_HEIGHT = 200
    MIN_CONTRAST = 30

    @staticmethod
    def assess_sharpness(image_path: Path) -> Dict:
        """
        Detect blurry images using edge detection with PIL
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'L':
                img = img.convert('L')

            # Use edge filter to detect sharpness
            edges = img.filter(ImageFilter.FIND_EDGES)
            stat = ImageStat.Stat(edges)
            edge_mean = stat.mean[0]

            # Higher edge mean = sharper image
            is_sharp = edge_mean > 10

            return {
                'edge_mean': edge_mean,
                'is_sharp': is_sharp,
                'sharpness_score': min(edge_mean / 30.0, 1.0)
            }
        except Exception as e:
            logger.error(f"Error assessing sharpness: {e}")
            return {
                'edge_mean': 0,
                'is_sharp': False,
                'sharpness_score': 0.0
            }

    @staticmethod
    def assess_color_diversity(image_path: Path) -> Dict:
        """
        Detect logos and icons by analyzing color palette
        """
        try:
            img = Image.open(image_path)

            if img.mode != 'RGB':
                img = img.convert('RGB')

            colors = img.getcolors(maxcolors=10000)

            if colors is None:
                return {
                    'unique_colors': 10000,
                    'dominant_color_ratio': 0.0,
                    'is_diverse': True,
                    'is_likely_logo': False
                }

            unique_colors = len(colors)
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
    def assess_brightness_contrast(image_path: Path) -> Dict:
        """
        Detect washed out or too dark images using PIL
        """
        try:
            img = Image.open(image_path)
            if img.mode != 'L':
                gray = img.convert('L')
            else:
                gray = img

            stat = ImageStat.Stat(gray)
            mean_brightness = stat.mean[0]
            std_brightness = stat.stddev[0]

            return {
                'mean_brightness': mean_brightness,
                'contrast': std_brightness,
                'is_well_exposed': 40 < mean_brightness < 220,
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

    @staticmethod
    def check_dimensions(image_path: Path) -> Dict:
        """Check if image meets minimum size requirements"""
        try:
            img = Image.open(image_path)
            width, height = img.size

            return {
                'width': width,
                'height': height,
                'meets_min_size': width >= ImageQualityAssessor.MIN_WIDTH and height >= ImageQualityAssessor.MIN_HEIGHT,
                'is_square': 0.9 <= (width / height) <= 1.1
            }
        except Exception as e:
            logger.error(f"Error checking dimensions: {e}")
            return {
                'width': 0,
                'height': 0,
                'meets_min_size': False,
                'is_square': False
            }

    @classmethod
    def comprehensive_assessment(cls, image_path: Path) -> Dict:
        """
        Full quality check combining all metrics
        """
        logger.debug(f"Assessing image quality: {image_path.name}")

        sharpness = cls.assess_sharpness(image_path)
        color = cls.assess_color_diversity(image_path)
        exposure = cls.assess_brightness_contrast(image_path)
        dimensions = cls.check_dimensions(image_path)

        # Calculate composite score (0-100)
        score = (
            sharpness['sharpness_score'] * 30 +
            (1.0 if color['is_diverse'] else 0.0) * 25 +
            (1.0 if dimensions['meets_min_size'] else 0.0) * 25 +
            (1.0 if exposure['is_well_exposed'] and exposure['has_contrast'] else 0.5) * 20
        )

        if score >= 75:
            quality_tier = 'high'
        elif score >= 50:
            quality_tier = 'medium'
        else:
            quality_tier = 'low'

        rejection_reasons = []

        if not sharpness['is_sharp']:
            rejection_reasons.append(f"Blurry (edge: {sharpness['edge_mean']:.1f})")

        if color['is_likely_logo']:
            rejection_reasons.append(f"Likely logo ({color['unique_colors']} colors)")

        if not dimensions['meets_min_size']:
            rejection_reasons.append(f"Too small ({dimensions['width']}x{dimensions['height']})")

        if not exposure['is_well_exposed']:
            rejection_reasons.append(f"Poor exposure (brightness: {exposure['mean_brightness']:.1f})")

        is_acceptable = score >= 50.0 and not color['is_likely_logo'] and dimensions['meets_min_size']

        result = {
            'overall_score': round(score, 2),
            'is_acceptable': is_acceptable,
            'quality_tier': quality_tier,
            'rejection_reasons': rejection_reasons,
            'sharpness': sharpness,
            'color': color,
            'dimensions': dimensions,
            'exposure': exposure
        }

        if is_acceptable:
            logger.info(f"✓ Image ACCEPTED - Score: {score:.1f} ({quality_tier}) - {image_path.name}")
        else:
            logger.warning(f"✗ Image REJECTED - Score: {score:.1f} - {', '.join(rejection_reasons)} - {image_path.name}")

        return result

    @staticmethod
    def is_likely_logo(image_path: Path, url: str = "") -> float:
        """
        Calculate probability (0.0-1.0) that image is a logo
        """
        indicators_triggered = 0
        total_indicators = 6

        if url:
            logo_keywords = ['logo', 'icon', 'brand', 'emblem', 'sprite']
            if any(keyword in url.lower() for keyword in logo_keywords):
                indicators_triggered += 2

            if '.svg' in url.lower():
                return 1.0

        try:
            img = Image.open(image_path)
            w, h = img.size

            aspect_ratio = w / h
            if 0.9 <= aspect_ratio <= 1.1 and (w < 600 or h < 600):
                indicators_triggered += 2

            colors = img.getcolors(maxcolors=10000)
            if colors and len(colors) < 500:
                indicators_triggered += 1

            if img.mode in ['RGBA', 'LA', 'P']:
                indicators_triggered += 1

            return indicators_triggered / total_indicators

        except Exception as e:
            logger.error(f"Error in logo detection: {e}")
            return 0.5
