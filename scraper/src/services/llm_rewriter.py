"""
LLM-based article rewriter using OpenRouter
"""
import httpx
import json
from typing import Optional, Dict
from loguru import logger

# Flexible import for Article model
try:
    from ..models.article import Article
except ImportError:
    try:
        from models.article import Article
    except ImportError:
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from models.article import Article


class LLMRewriter:
    """Rewrite articles using LLM via OpenRouter"""

    def __init__(
        self,
        api_key: str,
        model: str = "deepseek/deepseek-v3.2-exp",  # Mejor relación calidad/precio
        base_url: str = "https://openrouter.ai/api/v1"
    ):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.timeout = 120  # 2 minutes timeout for LLM

    async def rewrite_article(
        self,
        article: Article,
        preserve_style: bool = True
    ) -> Optional[Article]:
        """
        Rewrite article content using LLM

        Args:
            article: Original article
            preserve_style: Whether to preserve journalistic style

        Returns:
            Rewritten article or None if failed
        """
        try:
            logger.info(f"Rewriting article: {article.title[:50]}...")

            # Build prompt
            prompt = self._build_rewrite_prompt(article, preserve_style)

            # Call OpenRouter API
            response_data = await self._call_openrouter(prompt)

            if not response_data:
                logger.error("No response from OpenRouter")
                return None

            # Parse response
            rewritten = self._parse_llm_response(response_data, article)

            if rewritten:
                logger.success(f"Successfully rewrote: {article.title[:50]}...")
                return rewritten

            return None

        except Exception as e:
            logger.error(f"Error rewriting article: {e}")
            return None

    def _build_rewrite_prompt(self, article: Article, preserve_style: bool) -> str:
        """Build prompt for LLM - Optimized for better rewrites"""
        style_instruction = """
ESTILO PERIODÍSTICO ARGENTINO:
- Lenguaje claro, directo y profesional
- Objetividad periodística sin opiniones
- Vocabulario neutro y preciso
- Estructura: pirámide invertida (lo más importante primero)
- Tono formal pero accesible al público general
""" if preserve_style else "Reescribe de forma natural y fluida."

        prompt = f"""Eres un editor senior de noticias argentinas con 20 años de experiencia.

TAREA: Reescribir esta noticia completamente, creando un artículo ORIGINAL, COMPLETO y ÚNICO que preserve todos los hechos.

{style_instruction}

REGLAS ESTRICTAS:
✓ REESCRIBE completamente - NO copies ninguna frase textual
✓ REESTRUCTURA el contenido con tu propia narrativa
✓ PRESERVA todos los datos: nombres, fechas, cifras, lugares, declaraciones
✓ MANTÉN el mismo nivel de profundidad informativa
✓ USA sinónimos y estructuras gramaticales diferentes
✓ MEJORA la claridad si el original es confuso
✓ EXPANDE el contenido con contexto relevante y detalles
✗ NO agregues información nueva no presente en el original
✗ NO cambies el sentido ni interpretes los hechos
✗ NO omitas información relevante

NOTICIA ORIGINAL:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Título: {article.title}
{f"Subtítulo: {article.subtitle}" if article.subtitle else ""}
Categoría: {article.category}

{article.content or article.excerpt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FORMATO DE SALIDA (JSON estricto):
{{
  "title": "Título reescrito atractivo y claro (80-100 caracteres)",
  "subtitle": "Subtítulo opcional que complemente el título (hasta 150 caracteres)",
  "excerpt": "Lead periodístico con lo esencial de la noticia (180-220 caracteres)",
  "content": "Cuerpo completo de la noticia en HTML bien formateado. IMPORTANTE:
  - Usa etiquetas <p> para cada párrafo
  - Escribe 6-10 párrafos sustanciales
  - Cada párrafo debe tener 4-6 oraciones
  - Incluye TODOS los detalles del original expandidos y bien explicados
  - Agrega contexto y antecedentes cuando sea relevante
  - Formato: <p>Primer párrafo...</p><p>Segundo párrafo...</p> etc.
  - NO uses saltos de línea dobles, solo etiquetas <p>
  - Mantén un flujo narrativo coherente y completo"
}}

Responde ÚNICAMENTE con el JSON, sin texto adicional antes ni después."""

        return prompt

    async def _call_openrouter(self, prompt: str) -> Optional[Dict]:
        """Call OpenRouter API"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://periodico-argentino.vercel.app",
                        "X-Title": "Periodico Argentino Scraper"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 3500
                    }
                )

                response.raise_for_status()
                data = response.json()

                # Extract content
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0]["message"]["content"]
                    return {"content": content}

                logger.error("Unexpected API response format")
                return None

        except httpx.HTTPError as e:
            logger.error(f"HTTP error calling OpenRouter: {e}")
            return None
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {e}")
            return None

    def _parse_llm_response(
        self,
        response_data: Dict,
        original_article: Article
    ) -> Optional[Article]:
        """Parse LLM response and create rewritten article"""
        try:
            content = response_data.get("content", "")

            # Try to extract JSON from response
            # LLM might wrap it in markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            # Parse JSON
            rewritten_data = json.loads(content.strip())

            # Validate required fields
            if not rewritten_data.get("title") or not rewritten_data.get("content"):
                logger.error("LLM response missing required fields")
                return None

            # Create new article with rewritten content
            rewritten_article = Article(
                # Keep original metadata
                source=f"{original_article.source} (Reescrito)",
                source_url=original_article.source_url,
                category=original_article.category,
                category_slug=original_article.category_slug,
                published_at=original_article.published_at,

                # Use rewritten content
                title=rewritten_data["title"],
                subtitle=rewritten_data.get("subtitle"),
                excerpt=rewritten_data["excerpt"],
                content=rewritten_data["content"],

                # Keep original media
                image_url=original_article.image_url,
                local_image_path=original_article.local_image_path,
                images=original_article.images,

                # Update author
                author=f"{original_article.author} (Adaptado)",

                # Keep tags
                tags=original_article.tags,
                keywords=original_article.keywords
            )

            return rewritten_article

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"Response content: {response_data.get('content', '')[:200]}")
            return None
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return None

    async def rewrite_multiple(
        self,
        articles: list[Article],
        max_concurrent: int = 3
    ) -> list[Article]:
        """
        Rewrite multiple articles with concurrency control

        Args:
            articles: List of articles to rewrite
            max_concurrent: Maximum concurrent LLM calls

        Returns:
            List of successfully rewritten articles
        """
        import asyncio

        semaphore = asyncio.Semaphore(max_concurrent)
        rewritten = []

        async def rewrite_with_semaphore(article: Article) -> Optional[Article]:
            async with semaphore:
                result = await self.rewrite_article(article)
                # Add delay between requests to avoid rate limiting
                await asyncio.sleep(2)
                return result

        tasks = [rewrite_with_semaphore(article) for article in articles]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Article):
                rewritten.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error in concurrent rewrite: {result}")

        logger.info(f"Successfully rewrote {len(rewritten)}/{len(articles)} articles")
        return rewritten

    def estimate_cost(self, articles: list[Article]) -> Dict[str, float]:
        """
        Estimate LLM API cost

        Args:
            articles: List of articles

        Returns:
            Dictionary with cost estimates
        """
        # Rough estimates for Claude 3.5 Sonnet via OpenRouter
        # Input: ~$3 per million tokens
        # Output: ~$15 per million tokens

        total_input_tokens = 0
        total_output_tokens = 0

        for article in articles:
            # Estimate input tokens (prompt + article content)
            content_length = len(article.content or article.excerpt)
            input_estimate = (len(self._build_rewrite_prompt(article, True)) + content_length) / 4
            total_input_tokens += input_estimate

            # Estimate output tokens (~500-1000 per article)
            total_output_tokens += 750

        input_cost = (total_input_tokens / 1_000_000) * 3.0
        output_cost = (total_output_tokens / 1_000_000) * 15.0
        total_cost = input_cost + output_cost

        return {
            "articles": len(articles),
            "estimated_input_tokens": int(total_input_tokens),
            "estimated_output_tokens": int(total_output_tokens),
            "estimated_input_cost_usd": round(input_cost, 4),
            "estimated_output_cost_usd": round(output_cost, 4),
            "estimated_total_cost_usd": round(total_cost, 4)
        }
