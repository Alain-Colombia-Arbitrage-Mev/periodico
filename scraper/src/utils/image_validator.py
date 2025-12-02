"""
Image validator - Detecta y filtra imágenes inválidas (logos, placeholders, etc.)
"""
import re
from typing import Optional
from urllib.parse import urlparse
from loguru import logger


class ImageValidator:
    """Valida que las URLs de imágenes sean apropiadas para artículos de noticias"""

    # Patrones de URLs que NO son imágenes de artículos
    INVALID_PATTERNS = [
        r'logo',
        r'placeholder',
        r'default',
        r'avatar',
        r'icon',
        r'sprite',
        r'banner',
        r'header',
        r'footer',
        r'navbar',
        r'sidebar',
        r'widget',
        r'/static/',
        r'/assets/logo',
        r'/assets/icon',
        r'favicon',
        r'apple-touch-icon',
        r'og-image',
        r'share-image',
        r'social-media',
        # Dimensiones muy pequeñas típicas de logos
        r'100x100',
        r'50x50',
        r'32x32',
        r'64x64',
    ]

    # Sitios específicos con patrones conocidos de logos
    SITE_SPECIFIC_INVALID = {
        'infobae.com': [
            r'/logo',
            r'/brand',
            r'infobae-logo',
            r'logo-infobae',
        ],
        'lanacion.com.ar': [
            r'/logo',
            r'ln-logo',
            r'logo-ln',
        ],
        'clarin.com': [
            r'/logo',
            r'clarin-logo',
            r'logo-clarin',
        ],
    }

    # Extensiones válidas de imagen
    VALID_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']

    # Tamaño mínimo esperado (en la URL si está disponible)
    MIN_WIDTH = 400
    MIN_HEIGHT = 300

    @classmethod
    def is_valid_article_image(cls, image_url: str, source_domain: str = '') -> bool:
        """
        Verifica si una URL de imagen es válida para un artículo de noticias

        Args:
            image_url: URL de la imagen a validar
            source_domain: Dominio de la fuente (ej: 'infobae.com')

        Returns:
            True si es válida, False si es logo/placeholder/etc
        """
        if not image_url:
            return False

        # Convertir a minúsculas para comparación
        url_lower = image_url.lower()

        # 1. Verificar patrones generales inválidos
        for pattern in cls.INVALID_PATTERNS:
            if re.search(pattern, url_lower):
                logger.debug(f"Imagen rechazada por patrón '{pattern}': {image_url[:80]}")
                return False

        # 2. Verificar patrones específicos del sitio
        for domain, patterns in cls.SITE_SPECIFIC_INVALID.items():
            if domain in source_domain.lower():
                for pattern in patterns:
                    if re.search(pattern, url_lower):
                        logger.debug(f"Imagen rechazada por patrón de {domain}: {image_url[:80]}")
                        return False

        # 3. Verificar extensión
        parsed = urlparse(image_url)
        path = parsed.path.lower()
        has_valid_ext = any(path.endswith(ext) for ext in cls.VALID_EXTENSIONS)

        # Permitir URLs sin extensión si tienen parámetros (pueden ser CDN dinámicos)
        has_params = bool(parsed.query)

        if not has_valid_ext and not has_params:
            logger.debug(f"Imagen rechazada por extensión inválida: {image_url[:80]}")
            return False

        # 4. Verificar dimensiones en la URL (si están presentes)
        width_match = re.search(r'w[=_]?(\d+)', url_lower)
        height_match = re.search(r'h[=_]?(\d+)', url_lower)

        if width_match:
            width = int(width_match.group(1))
            if width < cls.MIN_WIDTH:
                logger.debug(f"Imagen rechazada por ancho {width}px: {image_url[:80]}")
                return False

        if height_match:
            height = int(height_match.group(1))
            if height < cls.MIN_HEIGHT:
                logger.debug(f"Imagen rechazada por alto {height}px: {image_url[:80]}")
                return False

        # 5. URLs muy cortas suelen ser íconos
        if len(parsed.path) < 10:
            logger.debug(f"Imagen rechazada por path muy corto: {image_url[:80]}")
            return False

        logger.debug(f"Imagen VÁLIDA: {image_url[:80]}")
        return True

    @classmethod
    def get_best_image(cls, image_urls: list[str], source_domain: str = '') -> Optional[str]:
        """
        De una lista de URLs, retorna la mejor imagen para el artículo

        Args:
            image_urls: Lista de URLs de imágenes candidatas
            source_domain: Dominio de la fuente

        Returns:
            URL de la mejor imagen o None
        """
        valid_images = [
            url for url in image_urls
            if cls.is_valid_article_image(url, source_domain)
        ]

        if not valid_images:
            logger.warning("No se encontraron imágenes válidas")
            return None

        # Priorizar imágenes más grandes (si la dimensión está en la URL)
        def get_image_score(url: str) -> int:
            """Score basado en dimensiones en la URL"""
            score = 0

            # Buscar ancho
            width_match = re.search(r'w[=_]?(\d+)', url.lower())
            if width_match:
                score += int(width_match.group(1))

            # Buscar alto
            height_match = re.search(r'h[=_]?(\d+)', url.lower())
            if height_match:
                score += int(height_match.group(1))

            # Preferir JPG sobre PNG (generalmente fotos vs gráficos)
            if '.jpg' in url.lower() or '.jpeg' in url.lower():
                score += 1000

            return score

        # Ordenar por score y retornar la mejor
        valid_images.sort(key=get_image_score, reverse=True)
        best_image = valid_images[0]

        logger.info(f"Mejor imagen seleccionada: {best_image[:80]}")
        return best_image
