"""
Advanced Image Quality Assessment using Computer Vision
Enhanced detection for logos, watermarks, blurry images, and low-quality content
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, Optional, Tuple, List
from loguru import logger
import hashlib
import re


class ImageQualityAssessor:
    """
    Ultra-Advanced Computer Vision-based image quality assessment
    Detects and filters out:
    - Blurry images (multi-method detection)
    - Logos and icons (color + shape analysis)
    - Watermarks and overlays
    - Low-contrast/poorly exposed images
    - Small/low-quality images
    - Social media icons and UI elements
    - Stock photo watermarks
    - Advertisement banners
    """

    # Enhanced thresholds - Stricter for better quality
    BLUR_THRESHOLD = 150.0  # Increased from 100
    BLUR_THRESHOLD_STRICT = 200.0  # Increased from 150
    MIN_COLOR_DIVERSITY = 1500  # Increased from 1000
    MIN_EDGE_DENSITY = 0.06  # Increased from 0.05
    MIN_BRIGHTNESS = 35  # Increased from 30
    MAX_BRIGHTNESS = 220  # Decreased from 225
    MIN_CONTRAST = 30  # Increased from 25
    MIN_IMAGE_WIDTH = 600  # Increased from 300 - Higher quality images
    MIN_IMAGE_HEIGHT = 400  # Increased from 200 - Higher quality images
    MIN_ASPECT_RATIO = 0.4  # Increased from 0.3
    MAX_ASPECT_RATIO = 3.0  # Decreased from 4.0

    # Patterns for detecting unwanted images
    LOGO_URL_KEYWORDS = [
        'logo', 'icon', 'brand', 'emblem', 'sprite', 'favicon',
        'avatar', 'badge', 'symbol', 'stamp', 'watermark', 'banner-ad',
        'advertisement', 'sponsor', 'promo', 'btn', 'button', 'arrow',
        'social', 'share', 'twitter', 'facebook', 'instagram', 'linkedin',
        'youtube', 'tiktok', 'whatsapp', 'telegram', 'pinterest',
        'play-button', 'loading', 'spinner', 'preloader', 'placeholder',
        'default', 'blank', 'empty', 'null', '1x1', 'pixel', 'spacer',
    ]

    STOCK_WATERMARK_KEYWORDS = [
        'shutterstock', 'gettyimages', 'istock', 'adobestock',
        'depositphotos', 'dreamstime', 'alamy', '123rf', 'fotolia',
        'preview', 'sample', 'watermark', 'comp', 'thumbnail',
    ]

    EXCLUDE_EXTENSIONS = ['.svg', '.gif', '.ico', '.webp']

    @classmethod
    def quick_filter(cls, url: str, width: int = 0, height: int = 0) -> Tuple[bool, str]:
        """
        Quick pre-download filter based on URL and dimensions
        Returns (should_download, reason)
        """
        url_lower = url.lower()

        # Check file extension
        for ext in cls.EXCLUDE_EXTENSIONS:
            if ext in url_lower:
                return False, f"Excluded extension: {ext}"

        # Check URL keywords
        for keyword in cls.LOGO_URL_KEYWORDS:
            if keyword in url_lower:
                return False, f"Logo keyword in URL: {keyword}"

        # Check stock watermarks
        for keyword in cls.STOCK_WATERMARK_KEYWORDS:
            if keyword in url_lower:
                return False, f"Stock watermark keyword: {keyword}"

        # Check dimensions if provided
        if width > 0 and height > 0:
            if width < cls.MIN_IMAGE_WIDTH or height < cls.MIN_IMAGE_HEIGHT:
                return False, f"Too small: {width}x{height}"

            aspect = width / height
            if aspect < cls.MIN_ASPECT_RATIO or aspect > cls.MAX_ASPECT_RATIO:
                return False, f"Bad aspect ratio: {aspect:.2f}"

        # Check for tracking pixels
        if re.search(r'/\d+x\d+/', url_lower) or '1x1' in url_lower:
            return False, "Tracking pixel pattern"

        # Check for base64 encoded tiny images
        if 'data:image' in url_lower and len(url) < 500:
            return False, "Base64 tiny image"

        return True, "OK"

    @staticmethod
    def assess_sharpness(image_path: Path) -> Dict:
        """Multi-method blur detection for robustness"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {
                    'laplacian_variance': 0,
                    'brenner_score': 0,
                    'is_sharp': False,
                    'sharpness_score': 0.0,
                    'blur_type': 'unreadable'
                }

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Method 1: Laplacian variance (standard)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Method 2: Brenner gradient (better for motion blur)
            def brenner_focus(img_gray):
                rows, cols = img_gray.shape
                brenner = 0
                for i in range(rows):
                    for j in range(cols - 2):
                        diff = int(img_gray[i, j + 2]) - int(img_gray[i, j])
                        brenner += diff * diff
                return brenner / (rows * (cols - 2))

            # Optimized Brenner using numpy
            shifted = np.roll(gray, -2, axis=1)[:, :-2].astype(np.int32)
            original = gray[:, :-2].astype(np.int32)
            brenner_score = np.mean((shifted - original) ** 2)

            # Method 3: Sobel gradient magnitude
            sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
            sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
            sobel_mag = np.sqrt(sobelx**2 + sobely**2).mean()

            # Determine blur type
            blur_type = None
            if laplacian_var < ImageQualityAssessor.BLUR_THRESHOLD:
                if brenner_score < 100:
                    blur_type = 'motion_blur'
                elif sobel_mag < 10:
                    blur_type = 'gaussian_blur'
                else:
                    blur_type = 'out_of_focus'

            # Combined score (weighted average)
            normalized_laplacian = min(laplacian_var / 200.0, 1.0)
            normalized_brenner = min(brenner_score / 200.0, 1.0)
            normalized_sobel = min(sobel_mag / 50.0, 1.0)

            combined_score = (
                normalized_laplacian * 0.5 +
                normalized_brenner * 0.3 +
                normalized_sobel * 0.2
            )

            return {
                'laplacian_variance': laplacian_var,
                'brenner_score': brenner_score,
                'sobel_magnitude': sobel_mag,
                'is_sharp': laplacian_var >= ImageQualityAssessor.BLUR_THRESHOLD,
                'sharpness_score': combined_score,
                'blur_type': blur_type
            }
        except Exception as e:
            logger.error(f"Error assessing sharpness: {e}")
            return {
                'laplacian_variance': 0,
                'brenner_score': 0,
                'is_sharp': False,
                'sharpness_score': 0.0,
                'blur_type': 'error'
            }

    @staticmethod
    def assess_color_diversity(image_path: Path) -> Dict:
        """Enhanced logo/icon detection using color analysis"""
        try:
            img = Image.open(image_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Get color statistics
            colors = img.getcolors(maxcolors=50000)
            total_pixels = img.width * img.height

            if colors is None:
                # Very complex image - definitely not a logo
                return {
                    'unique_colors': 50000,
                    'dominant_color_ratio': 0.0,
                    'color_entropy': 1.0,
                    'is_diverse': True,
                    'is_likely_logo': False,
                    'is_solid_color': False
                }

            unique_colors = len(colors)
            sorted_colors = sorted(colors, key=lambda x: x[0], reverse=True)

            # Calculate dominant color ratio
            dominant_color_ratio = sorted_colors[0][0] / total_pixels if sorted_colors else 0

            # Top 3 colors ratio (logos often have few dominant colors)
            top3_ratio = sum(c[0] for c in sorted_colors[:3]) / total_pixels if len(sorted_colors) >= 3 else 1.0

            # Calculate color entropy (diversity measure)
            probabilities = [c[0] / total_pixels for c in colors]
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            max_entropy = np.log2(len(colors)) if len(colors) > 1 else 1
            normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

            # Check for solid color backgrounds
            is_solid = dominant_color_ratio > 0.8

            # Logo detection heuristics
            is_likely_logo = (
                unique_colors < 500 or
                dominant_color_ratio > 0.4 or
                top3_ratio > 0.85 or
                normalized_entropy < 0.3
            )

            return {
                'unique_colors': unique_colors,
                'dominant_color_ratio': dominant_color_ratio,
                'top3_ratio': top3_ratio,
                'color_entropy': normalized_entropy,
                'is_diverse': unique_colors >= ImageQualityAssessor.MIN_COLOR_DIVERSITY,
                'is_likely_logo': is_likely_logo,
                'is_solid_color': is_solid
            }
        except Exception as e:
            logger.error(f"Error assessing color diversity: {e}")
            return {
                'unique_colors': 0,
                'dominant_color_ratio': 1.0,
                'color_entropy': 0.0,
                'is_diverse': False,
                'is_likely_logo': True,
                'is_solid_color': True
            }

    @staticmethod
    def detect_edges(image_path: Path) -> Dict:
        """Enhanced edge detection for content complexity analysis"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {'edge_density': 0.0, 'is_complex': False, 'edge_score': 0.0}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Multi-scale edge detection
            edges_tight = cv2.Canny(gray, 100, 200)
            edges_loose = cv2.Canny(gray, 50, 150)

            edge_density_tight = np.sum(edges_tight > 0) / edges_tight.size
            edge_density_loose = np.sum(edges_loose > 0) / edges_loose.size

            # Calculate edge coherence (organized vs random edges)
            # High coherence = likely text/logo, low = natural image
            kernel = np.ones((5, 5), np.uint8)
            dilated = cv2.dilate(edges_tight, kernel, iterations=1)
            coherence = np.sum(dilated > 0) / (np.sum(edges_tight > 0) + 1)

            edge_score = min(edge_density_tight / 0.15, 1.0)

            return {
                'edge_density': edge_density_tight,
                'edge_density_loose': edge_density_loose,
                'edge_coherence': coherence,
                'is_complex': edge_density_tight > ImageQualityAssessor.MIN_EDGE_DENSITY,
                'edge_score': edge_score,
                'is_likely_text': coherence > 3.0 and edge_density_tight > 0.1
            }
        except Exception as e:
            logger.error(f"Error detecting edges: {e}")
            return {'edge_density': 0.0, 'is_complex': False, 'edge_score': 0.0}

    @staticmethod
    def assess_brightness_contrast(image_path: Path) -> Dict:
        """Enhanced exposure analysis with histogram evaluation"""
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

            # Histogram analysis
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten() / hist.sum()

            # Check for clipping (overexposed/underexposed)
            dark_pixels = hist[:20].sum()
            bright_pixels = hist[235:].sum()

            is_clipped = dark_pixels > 0.3 or bright_pixels > 0.3

            # Dynamic range
            non_zero = np.where(hist > 0.001)[0]
            dynamic_range = (non_zero[-1] - non_zero[0]) / 255 if len(non_zero) > 1 else 0

            return {
                'mean_brightness': mean_brightness,
                'contrast': std_brightness,
                'dynamic_range': dynamic_range,
                'dark_pixels_ratio': dark_pixels,
                'bright_pixels_ratio': bright_pixels,
                'is_well_exposed': (
                    ImageQualityAssessor.MIN_BRIGHTNESS < mean_brightness < ImageQualityAssessor.MAX_BRIGHTNESS
                    and not is_clipped
                ),
                'has_contrast': std_brightness > ImageQualityAssessor.MIN_CONTRAST,
                'is_clipped': is_clipped
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
    def detect_watermark(image_path: Path) -> Dict:
        """Detect watermarks and overlays"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {'has_watermark': False, 'watermark_confidence': 0.0}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape

            # Check corners for watermarks (common placement)
            corners = [
                gray[0:h//4, 0:w//4],           # Top-left
                gray[0:h//4, 3*w//4:],          # Top-right
                gray[3*h//4:, 0:w//4],          # Bottom-left
                gray[3*h//4:, 3*w//4:],         # Bottom-right
            ]

            # Check center for watermarks (stock photos)
            center = gray[h//3:2*h//3, w//3:2*w//3]

            watermark_indicators = 0

            # Detect semi-transparent overlays (characteristic of watermarks)
            for corner in corners:
                # High contrast edges in corners suggest watermark
                edges = cv2.Canny(corner, 100, 200)
                if np.sum(edges > 0) / edges.size > 0.15:
                    watermark_indicators += 1

            # Check center for diagonal patterns (stock watermarks)
            center_edges = cv2.Canny(center, 50, 150)
            lines = cv2.HoughLinesP(center_edges, 1, np.pi/180, 50, minLineLength=50, maxLineGap=10)
            if lines is not None and len(lines) > 10:
                watermark_indicators += 2

            confidence = min(watermark_indicators / 4.0, 1.0)

            return {
                'has_watermark': watermark_indicators >= 2,
                'watermark_confidence': confidence,
                'corner_indicators': watermark_indicators
            }
        except Exception as e:
            logger.error(f"Error detecting watermark: {e}")
            return {'has_watermark': False, 'watermark_confidence': 0.0}

    @staticmethod
    def detect_faces_content(image_path: Path) -> Dict:
        """Detect if image contains meaningful content (faces, objects)"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return {'has_faces': False, 'face_count': 0, 'content_score': 0.0}

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Use Haar cascades for face detection
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )

            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )

            has_faces = len(faces) > 0

            # Calculate content interest score based on variance in different regions
            h, w = gray.shape
            regions = [
                gray[0:h//2, 0:w//2],
                gray[0:h//2, w//2:],
                gray[h//2:, 0:w//2],
                gray[h//2:, w//2:],
            ]

            region_variances = [np.var(r) for r in regions]
            content_score = np.mean(region_variances) / 1000.0  # Normalize

            return {
                'has_faces': has_faces,
                'face_count': len(faces),
                'content_score': min(content_score, 1.0),
                'is_interesting': has_faces or content_score > 0.5
            }
        except Exception as e:
            logger.debug(f"Face detection skipped: {e}")
            return {'has_faces': False, 'face_count': 0, 'content_score': 0.5}

    @classmethod
    def comprehensive_assessment(cls, image_path: Path, url: str = "") -> Dict:
        """Full quality check combining all metrics"""
        logger.debug(f"Assessing image quality: {image_path.name}")

        # Quick URL filter first
        if url:
            should_process, reason = cls.quick_filter(url)
            if not should_process:
                logger.warning(f"✗ Image REJECTED (URL filter) - {reason} - {url}")
                return {
                    'overall_score': 0,
                    'is_acceptable': False,
                    'quality_tier': 'rejected',
                    'rejection_reasons': [f"URL filter: {reason}"],
                    'quick_rejected': True
                }

        # Check file exists and basic properties
        if not image_path.exists():
            return {
                'overall_score': 0,
                'is_acceptable': False,
                'quality_tier': 'rejected',
                'rejection_reasons': ['File not found'],
                'quick_rejected': True
            }

        # Get image dimensions
        try:
            with Image.open(image_path) as img:
                width, height = img.size
        except Exception as e:
            logger.error(f"Cannot open image: {e}")
            return {
                'overall_score': 0,
                'is_acceptable': False,
                'quality_tier': 'rejected',
                'rejection_reasons': ['Cannot open image'],
                'quick_rejected': True
            }

        # Dimension check
        if width < cls.MIN_IMAGE_WIDTH or height < cls.MIN_IMAGE_HEIGHT:
            logger.warning(f"✗ Image REJECTED - Too small ({width}x{height}) - {image_path.name}")
            return {
                'overall_score': 10,
                'is_acceptable': False,
                'quality_tier': 'rejected',
                'rejection_reasons': [f"Too small: {width}x{height}"],
                'dimensions': {'width': width, 'height': height}
            }

        # Run all assessments
        sharpness = cls.assess_sharpness(image_path)
        color = cls.assess_color_diversity(image_path)
        edges = cls.detect_edges(image_path)
        exposure = cls.assess_brightness_contrast(image_path)
        watermark = cls.detect_watermark(image_path)
        content = cls.detect_faces_content(image_path)

        # Calculate weighted score
        score = (
            sharpness['sharpness_score'] * 25 +
            (1.0 if color['is_diverse'] else 0.0) * 20 +
            (0.0 if color['is_likely_logo'] else 1.0) * 15 +
            edges['edge_score'] * 15 +
            (1.0 if exposure['is_well_exposed'] and exposure['has_contrast'] else 0.5) * 15 +
            (0.0 if watermark['has_watermark'] else 1.0) * 5 +
            content['content_score'] * 5
        )

        # Determine quality tier
        if score >= 75:
            quality_tier = 'high'
        elif score >= 50:
            quality_tier = 'medium'
        elif score >= 30:
            quality_tier = 'low'
        else:
            quality_tier = 'rejected'

        # Collect rejection reasons
        rejection_reasons = []
        if not sharpness['is_sharp']:
            blur_type = sharpness.get('blur_type', 'unknown')
            rejection_reasons.append(f"Blurry ({blur_type}, Laplacian: {sharpness['laplacian_variance']:.1f})")
        if color['is_likely_logo']:
            rejection_reasons.append(f"Likely logo/icon ({color['unique_colors']} colors, entropy: {color.get('color_entropy', 0):.2f})")
        if color['is_solid_color']:
            rejection_reasons.append("Solid color background")
        if not edges['is_complex']:
            rejection_reasons.append(f"Low complexity (edge: {edges['edge_density']:.2%})")
        if edges.get('is_likely_text'):
            rejection_reasons.append("Likely text/infographic")
        if not exposure['is_well_exposed']:
            rejection_reasons.append(f"Poor exposure ({exposure['mean_brightness']:.1f})")
        if exposure.get('is_clipped'):
            rejection_reasons.append("Clipped highlights/shadows")
        if watermark['has_watermark']:
            rejection_reasons.append(f"Watermark detected ({watermark['watermark_confidence']:.0%})")

        # Final acceptance decision - Stricter threshold for better quality
        is_acceptable = (
            score >= 55.0 and  # Increased from 45 for higher quality
            not color['is_likely_logo'] and
            not watermark['has_watermark'] and
            not color['is_solid_color'] and
            sharpness['is_sharp']  # Must be sharp
        )

        result = {
            'overall_score': round(score, 2),
            'is_acceptable': is_acceptable,
            'quality_tier': quality_tier,
            'rejection_reasons': rejection_reasons,
            'dimensions': {'width': width, 'height': height},
            'sharpness': sharpness,
            'color': color,
            'edges': edges,
            'exposure': exposure,
            'watermark': watermark,
            'content': content
        }

        if is_acceptable:
            logger.info(f"✓ Image ACCEPTED - Score: {score:.1f} ({quality_tier}) - {image_path.name}")
        else:
            logger.warning(f"✗ Image REJECTED - Score: {score:.1f} - {', '.join(rejection_reasons[:3])} - {image_path.name}")

        return result

    @classmethod
    def is_likely_logo(cls, image_path: Path, url: str = "") -> float:
        """Calculate probability (0.0-1.0) that image is a logo"""
        indicators_triggered = 0
        total_indicators = 10

        # URL analysis
        if url:
            url_lower = url.lower()
            for keyword in cls.LOGO_URL_KEYWORDS:
                if keyword in url_lower:
                    indicators_triggered += 2
                    break

            if '.svg' in url_lower:
                return 1.0

            # Tiny image indicator
            if any(f'/{dim}/' in url_lower or f'_{dim}.' in url_lower
                   for dim in ['16', '24', '32', '48', '64', '72', '96']):
                indicators_triggered += 2

        try:
            img = Image.open(image_path)
            w, h = img.size

            # Square ratio with small size = likely icon
            aspect_ratio = w / h
            if 0.9 <= aspect_ratio <= 1.1 and (w < 400 or h < 400):
                indicators_triggered += 2

            # Very few colors = likely logo
            colors = img.getcolors(maxcolors=10000)
            if colors and len(colors) < 300:
                indicators_triggered += 2
            elif colors and len(colors) < 1000:
                indicators_triggered += 1

            # Transparency = often logo
            if img.mode in ['RGBA', 'LA', 'P']:
                if img.mode == 'RGBA':
                    alpha = img.split()[-1]
                    transparent_pixels = sum(1 for p in alpha.getdata() if p < 250)
                    if transparent_pixels > 0.1 * w * h:
                        indicators_triggered += 2

            return min(indicators_triggered / total_indicators, 1.0)
        except Exception as e:
            logger.error(f"Error in logo detection: {e}")
            return 0.5

    @classmethod
    def batch_filter(cls, image_urls: List[str]) -> List[Tuple[str, bool, str]]:
        """Quick filter a batch of URLs without downloading"""
        results = []
        for url in image_urls:
            should_process, reason = cls.quick_filter(url)
            results.append((url, should_process, reason))
        return results

    @classmethod
    def get_best_image(cls, image_paths: List[Path], urls: List[str] = None) -> Optional[Path]:
        """Select the best quality image from a list"""
        if not image_paths:
            return None

        best_path = None
        best_score = -1

        for i, path in enumerate(image_paths):
            url = urls[i] if urls and i < len(urls) else ""
            result = cls.comprehensive_assessment(path, url)

            if result['is_acceptable'] and result['overall_score'] > best_score:
                best_score = result['overall_score']
                best_path = path

        return best_path
