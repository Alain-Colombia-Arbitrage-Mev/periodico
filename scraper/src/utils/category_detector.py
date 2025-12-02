"""
Category detection utility
Detects article category from URL, content, and metadata
"""
import re
from typing import Optional
from bs4 import BeautifulSoup
from loguru import logger


class CategoryDetector:
    """Detect article category automatically"""

    # Palabras clave que indican contenido relacionado con Argentina
    ARGENTINA_KEYWORDS = [
        "argentina", "argentino", "argentinos", "argentinas", "buenos aires",
        "caba", "rosario", "córdoba", "cordoba", "mendoza", "la plata",
        "milei", "cristina", "kirchner", "macri", "bullrich", "massa",
        "afa", "selección argentina", "river", "boca", "racing", "independiente",
        "casa rosada", "congreso nacional", "bcra", "ypf", "aerolineas argentinas",
        "patagonia", "pampa", "litoral", "cuyo", "noa", "nea"
    ]

    # Mapeo de palabras clave a categorías
    CATEGORY_KEYWORDS = {
        "economia": [
            "economía", "economia", "dólar", "dolar", "peso", "inflación", "inflacion",
            "bcra", "banco central", "mercado", "finanzas", "empresas", "negocios",
            "exportación", "exportacion", "importación", "importacion", "comercio",
            "trabajo", "empleo", "salario", "precio", "costo", "tarifa", "impuesto"
        ],
        "politica": [
            "política", "politica", "gobierno", "presidente", "ministro", "congreso",
            "diputado", "senador", "elección", "eleccion", "votación", "votacion",
            "partido", "candidato", "campaña", "campana", "ley", "proyecto", "decreto",
            "militar", "fuerza", "seguridad", "defensa", "poder", "estado"
        ],
        "judicial": [
            "judicial", "juez", "tribunal", "corte", "fiscal", "abogado", "juicio",
            "sentencia", "causa", "proceso", "delito", "crimen", "criminal", "penal",
            "prisión", "prision", "cárcel", "carcel", "detención", "detencion",
            "acusación", "acusacion", "imputado", "víctima", "victima"
        ],
        "internacional": [
            "internacional", "mundo", "global", "país", "pais", "nación", "nacion",
            "extranjero", "exterior", "diplomacia", "embajada", "consulado",
            "organización", "organizacion", "onu", "naciones unidas", "ue", "europa",
            "eeuu", "estados unidos", "china", "brasil", "chile", "uruguay"
        ],
        "sociedad": [
            "sociedad", "social", "comunidad", "población", "poblacion", "ciudadano",
            "ciudadana", "derecho", "derechos", "salud", "educación", "educacion",
            "cultura", "arte", "música", "musica", "deporte", "deportes", "tecnología",
            "tecnologia", "ciencia", "medio ambiente", "medioambiente", "clima",
            "transporte", "tránsito", "transito", "vial", "accidente"
        ]
    }
    
    # Mapeo de URLs a categorías
    URL_PATTERNS = {
        "economia": [
            r"/economia", r"/economy", r"/finanzas", r"/finances", r"/negocios",
            r"/mercado", r"/dolar", r"/dólar"
        ],
        "politica": [
            r"/politica", r"/politics", r"/gobierno", r"/government", r"/congreso",
            r"/elecciones", r"/elections"
        ],
        "judicial": [
            r"/judicial", r"/justicia", r"/justice", r"/corte", r"/tribunal",
            r"/juicio", r"/trial"
        ],
        "internacional": [
            r"/internacional", r"/internacionales", r"/mundo", r"/world",
            r"/america", r"/américa", r"/exterior"
        ],
        "sociedad": [
            r"/sociedad", r"/society", r"/salud", r"/health", r"/educacion",
            r"/educación", r"/cultura", r"/deportes", r"/deportes"
        ]
    }
    
    @classmethod
    def detect_from_url(cls, url: str) -> Optional[str]:
        """Detect category from URL"""
        url_lower = url.lower()
        
        for category, patterns in cls.URL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    logger.debug(f"Category detected from URL: {category}")
                    return category
        
        return None
    
    @classmethod
    def detect_from_content(cls, title: str, content: str, excerpt: str = "") -> Optional[str]:
        """Detect category from article content"""
        text = f"{title} {excerpt} {content}".lower()
        
        # Contar coincidencias por categoría
        category_scores = {}
        
        for category, keywords in cls.CATEGORY_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                # Buscar palabra completa (no como parte de otra palabra)
                pattern = r'\b' + re.escape(keyword) + r'\b'
                matches = len(re.findall(pattern, text, re.IGNORECASE))
                score += matches
            
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            # Retornar categoría con mayor score
            detected = max(category_scores.items(), key=lambda x: x[1])
            logger.debug(f"Category detected from content: {detected[0]} (score: {detected[1]})")
            return detected[0]
        
        return None
    
    @classmethod
    def detect_from_metadata(cls, soup: BeautifulSoup) -> Optional[str]:
        """Detect category from HTML metadata"""
        # Buscar en meta tags
        meta_category = soup.find('meta', property='article:section') or \
                       soup.find('meta', attrs={'name': 'category'}) or \
                       soup.find('meta', attrs={'name': 'news_keywords'})
        
        if meta_category:
            content = meta_category.get('content', '').lower()
            for category in cls.CATEGORY_KEYWORDS.keys():
                if category in content:
                    logger.debug(f"Category detected from metadata: {category}")
                    return category
        
        # Buscar en breadcrumbs o navigation
        breadcrumbs = soup.find('nav', class_=re.compile('breadcrumb', re.I)) or \
                     soup.find('ol', class_=re.compile('breadcrumb', re.I))
        
        if breadcrumbs:
            breadcrumb_text = breadcrumbs.get_text().lower()
            for category in cls.CATEGORY_KEYWORDS.keys():
                if category in breadcrumb_text:
                    logger.debug(f"Category detected from breadcrumbs: {category}")
                    return category
        
        return None
    
    @classmethod
    def is_about_argentina(cls, title: str, content: str, excerpt: str = "") -> bool:
        """
        Detecta si el artículo está relacionado con Argentina

        Returns:
            True si el artículo menciona Argentina o términos relacionados
        """
        text = f"{title} {excerpt} {content}".lower()

        # Buscar referencias a Argentina
        for keyword in cls.ARGENTINA_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Article is about Argentina (keyword: {keyword})")
                return True

        logger.debug("Article is NOT about Argentina - will be categorized as internacional")
        return False

    @classmethod
    def detect_category(
        cls,
        url: str,
        title: str,
        content: str,
        excerpt: str = "",
        soup: Optional[BeautifulSoup] = None
    ) -> str:
        """
        Detect category using multiple methods

        Returns:
            Category slug (default: "politica")
        """
        # Prioridad: URL > Metadata > Content
        category = cls.detect_from_url(url)

        if not category and soup:
            category = cls.detect_from_metadata(soup)

        if not category:
            category = cls.detect_from_content(title, content, excerpt)

        # Si no se detectó categoría, default a "politica"
        if not category:
            category = "politica"

        # Si el artículo NO es sobre Argentina y no es ya "internacional",
        # forzar categoría "internacional"
        if category != "internacional" and not cls.is_about_argentina(title, content, excerpt):
            logger.info(f"Article reclassified from '{category}' to 'internacional' (not about Argentina)")
            category = "internacional"

        return category









