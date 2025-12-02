"""
Text cleaning utility
Removes references to source websites (Clarín, Infobae, etc.)
"""
import re
from typing import Optional
from loguru import logger


class TextCleaner:
    """Clean text by removing source references"""
    
    # Patrones a eliminar (case-insensitive)
    SOURCE_PATTERNS = [
        # Clarín
        r'\bclarin\b',
        r'\bclarín\b',
        r'\bclarín\.com\b',
        r'\bclarin\.com\b',
        r'\bwww\.clarin\.com\b',
        r'\bwww\.clarín\.com\b',
        r'fuente:\s*clarin',
        r'fuente:\s*clarín',
        r'según\s+clarin',
        r'según\s+clarín',
        r'según\s+clarin\.com',
        r'según\s+clarín\.com',
        r'por\s+clarin',
        r'por\s+clarín',

        # Infobae
        r'\binfobae\b',
        r'\binfobae\.com\b',
        r'\bwww\.infobae\.com\b',
        r'fuente:\s*infobae',
        r'según\s+infobae',
        r'según\s+infobae\.com',
        r'por\s+infobae',

        # La Nación
        r'\blanacion\b',
        r'\bla\s+naci[oó]n\b',
        r'\blanacion\.com\.ar\b',
        r'\bwww\.lanacion\.com\.ar\b',
        r'fuente:\s*lanacion',
        r'fuente:\s*la\s+naci[oó]n',
        r'según\s+lanacion',
        r'según\s+la\s+naci[oó]n',
        r'por\s+lanacion',
        r'por\s+la\s+naci[oó]n',

        # Patrones de autoría (escrito por, por, etc.)
        r'escrito\s+por\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3}',
        r'por\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3}\s*[-|]',
        r'^por\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(\s+[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+){0,3}\s*$',
        r'autor:\s*[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+',
        r'redacci[oó]n\s+de\s+[A-ZÁÉÍÓÚÑ]',

        # Patrones genéricos de fuentes
        r'fuente:\s*[a-z]+\.com',
        r'leer\s+más\s+en\s+[a-z]+\.com',
        r'ver\s+más\s+en\s+[a-z]+\.com',
        r'continuar\s+leyendo\s+en\s+[a-z]+\.com',
        r'más\s+información\s+en\s+[a-z]+\.com',
        r'nota\s+completa\s+en\s+[a-z]+\.com',

        # Patrones de redes sociales y compartir
        r'segu[ií]\s*nos\s+en\s+(twitter|facebook|instagram)',
        r'compartir\s+en\s+(twitter|facebook|instagram)',
        r'@[a-z0-9_]+',  # Menciones de Twitter
    ]
    
    @classmethod
    def clean_text(cls, text: Optional[str]) -> Optional[str]:
        """
        Clean text by removing source references
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text or None if input is None
        """
        if not text:
            return text
        
        cleaned = text
        
        # Aplicar cada patrón
        for pattern in cls.SOURCE_PATTERNS:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Limpiar espacios múltiples
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Limpiar espacios al inicio y final
        cleaned = cleaned.strip()
        
        # Limpiar puntos y comas múltiples
        cleaned = re.sub(r'[.,]{2,}', '.', cleaned)
        
        # Limpiar espacios antes de puntuación
        cleaned = re.sub(r'\s+([.,;:!?])', r'\1', cleaned)
        
        return cleaned if cleaned else text  # Retornar original si queda vacío
    
    @classmethod
    def clean_content(cls, content: Optional[str]) -> Optional[str]:
        """Clean article content (more aggressive cleaning)"""
        if not content:
            return content
        
        cleaned = cls.clean_text(content)
        
        # Eliminar líneas que solo contienen referencias
        lines = cleaned.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Si la línea es muy corta y contiene solo referencias, omitirla
            if len(line_stripped) < 20:
                # Verificar si contiene solo referencias
                if any(re.search(pattern, line_stripped, re.IGNORECASE) 
                       for pattern in cls.SOURCE_PATTERNS[:10]):  # Solo los primeros patrones
                    continue
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines).strip()
    
    @classmethod
    def clean_title(cls, title: Optional[str]) -> Optional[str]:
        """Clean article title"""
        if not title:
            return title
        
        cleaned = cls.clean_text(title)
        
        # Eliminar sufijos comunes como " - Clarín" o " | Infobae"
        cleaned = re.sub(r'\s*[-|]\s*(clarin|clarín|infobae|lanacion|la\s+naci[oó]n)', 
                        '', cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()









