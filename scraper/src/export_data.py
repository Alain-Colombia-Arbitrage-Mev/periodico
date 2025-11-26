"""
Export scraped data to various formats
"""
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from storage.database import Database
from utils.logger import setup_logger, get_logger

setup_logger(log_level="INFO")
logger = get_logger(__name__)


def export_to_json(articles: list[dict], output_file: str):
    """Export articles to JSON"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, ensure_ascii=False, indent=2, default=str)

    logger.info(f"Exported {len(articles)} articles to {output_file}")


def export_to_csv(articles: list[dict], output_file: str):
    """Export articles to CSV"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if not articles:
        logger.warning("No articles to export")
        return

    # Flatten nested fields
    flattened = []
    for article in articles:
        flat = article.copy()
        flat['tags'] = ','.join(article.get('tags', []))
        flat['keywords'] = ','.join(article.get('keywords', []))
        flat['images'] = ','.join(article.get('images', []))
        flattened.append(flat)

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=flattened[0].keys())
        writer.writeheader()
        writer.writerows(flattened)

    logger.info(f"Exported {len(articles)} articles to {output_file}")


def export_typescript_types(articles: list[dict], output_file: str):
    """Export as TypeScript types for Next.js"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ts_content = """// Auto-generated from scraper
// Last updated: {timestamp}

export interface Noticia {{
  id: string;
  slug: string;
  title: string;
  subtitle?: string;
  category: string;
  categorySlug: string;
  excerpt: string;
  content?: string;
  imageUrl?: string;
  author: string;
  publishedAt: Date;
  views: number;
  isBreaking?: boolean;
  tags?: string[];
  source: string;
  sourceUrl: string;
}}

""".format(timestamp=datetime.now().isoformat())

    # Group by category
    by_category = {}
    for article in articles:
        category = article.get('category_slug', 'general')
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(article)

    # Export each category
    for category, cat_articles in by_category.items():
        var_name = f"noticias{category.capitalize()}"
        ts_content += f"\nexport const {var_name}: Noticia[] = [\n"

        for article in cat_articles:
            ts_content += "  {\n"
            ts_content += f"    id: '{article['id']}',\n"
            ts_content += f"    slug: '{article['slug']}',\n"
            ts_content += f"    title: {json.dumps(article['title'])},\n"

            if article.get('subtitle'):
                ts_content += f"    subtitle: {json.dumps(article['subtitle'])},\n"

            ts_content += f"    category: '{article['category']}',\n"
            ts_content += f"    categorySlug: '{article['category_slug']}',\n"
            ts_content += f"    excerpt: {json.dumps(article['excerpt'])},\n"

            if article.get('content'):
                content = article['content'][:500] + "..." if len(article['content']) > 500 else article['content']
                ts_content += f"    content: {json.dumps(content)},\n"

            image_url = article.get('local_image_path') or article.get('image_url') or '/images/default.jpg'
            ts_content += f"    imageUrl: '/images/{image_url}',\n"

            ts_content += f"    author: '{article['author']}',\n"
            ts_content += f"    publishedAt: new Date('{article['published_at']}'),\n"
            ts_content += f"    views: {article.get('views', 0)},\n"

            if article.get('is_breaking'):
                ts_content += f"    isBreaking: true,\n"

            if article.get('tags'):
                tags_str = json.dumps(article['tags'][:5])
                ts_content += f"    tags: {tags_str},\n"

            ts_content += f"    source: '{article['source']}',\n"
            ts_content += f"    sourceUrl: '{article['source_url']}',\n"

            ts_content += "  },\n"

        ts_content += "];\n"

    # Export all articles
    ts_content += "\nexport const todasLasNoticias: Noticia[] = [\n"
    for category in by_category.keys():
        var_name = f"noticias{category.capitalize()}"
        ts_content += f"  ...{var_name},\n"
    ts_content += "];\n"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ts_content)

    logger.info(f"Exported {len(articles)} articles to TypeScript: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Export scraped data')
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'typescript'],
        default='json',
        help='Export format'
    )
    parser.add_argument(
        '--output',
        default=None,
        help='Output file path'
    )
    parser.add_argument(
        '--category',
        default=None,
        help='Filter by category'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=1000,
        help='Maximum number of articles'
    )
    parser.add_argument(
        '--database-url',
        default='postgresql://scraper:scraper_password_2024@localhost:5432/scraper_db',
        help='Database URL'
    )

    args = parser.parse_args()

    # Connect to database
    db = Database(args.database_url)

    # Fetch articles
    if args.category:
        articles = db.get_articles_by_category(args.category, limit=args.limit)
        logger.info(f"Fetched {len(articles)} articles from category: {args.category}")
    else:
        articles = db.get_recent_articles(limit=args.limit)
        logger.info(f"Fetched {len(articles)} recent articles")

    if not articles:
        logger.warning("No articles found")
        return

    # Determine output file
    if args.output:
        output_file = args.output
    else:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ext = 'ts' if args.format == 'typescript' else args.format
        output_file = f"data/processed/export_{timestamp}.{ext}"

    # Export
    if args.format == 'json':
        export_to_json(articles, output_file)
    elif args.format == 'csv':
        export_to_csv(articles, output_file)
    elif args.format == 'typescript':
        export_typescript_types(articles, output_file)


if __name__ == '__main__':
    main()
