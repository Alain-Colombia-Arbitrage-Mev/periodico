"""
Quick test script for the pipeline components
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from models.article import Article
from services.llm_rewriter import LLMRewriter
from services.supabase_sync import SupabaseSync
from utils.logger import setup_logger
from datetime import datetime


async def test_llm_rewriter():
    """Test LLM rewriting"""
    print("\n" + "="*60)
    print("Testing LLM Rewriter")
    print("="*60)

    api_key = input("Enter your OpenRouter API key: ").strip()

    if not api_key:
        print("❌ API key required")
        return False

    rewriter = LLMRewriter(api_key=api_key)

    # Create test article
    test_article = Article(
        source="Test Source",
        source_url="https://example.com/test",
        title="Dólar blue alcanza los $1.445 en Argentina",
        subtitle="El mercado cambiario muestra estabilidad",
        excerpt="El dólar paralelo se mantiene estable en las últimas jornadas.",
        content="""El dólar blue cerró en $1.445 para la venta, manteniéndose estable
        en las últimas jornadas. Los analistas económicos destacan la intervención
        del Banco Central y proyectan estabilidad para los próximos meses.""",
        category="Economía",
        category_slug="economia",
        author="Test Author",
        published_at=datetime.now()
    )

    print("\n📝 Original article:")
    print(f"Title: {test_article.title}")
    print(f"Content: {test_article.content[:100]}...")

    print("\n🤖 Rewriting with LLM...")
    rewritten = await rewriter.rewrite_article(test_article)

    if rewritten:
        print("\n✅ Rewritten successfully!")
        print(f"New Title: {rewritten.title}")
        print(f"New Content: {rewritten.content[:100]}...")
        return True
    else:
        print("\n❌ Rewriting failed")
        return False


async def test_supabase_sync():
    """Test Supabase synchronization"""
    print("\n" + "="*60)
    print("Testing Supabase Sync")
    print("="*60)

    url = input("Enter your Supabase URL: ").strip()
    key = input("Enter your Supabase Key: ").strip()

    if not url or not key:
        print("❌ Both URL and Key are required")
        return False

    sync = SupabaseSync(supabase_url=url, supabase_key=key)

    # Create test article
    test_article = Article(
        id="test_001",
        slug="test-article",
        source="Test Source",
        source_url="https://example.com/test-001",
        title="Test Article Title",
        subtitle="Test Subtitle",
        excerpt="This is a test article for Supabase sync.",
        content="Full content of the test article goes here.",
        category="Economía",
        category_slug="economia",
        author="Test Author",
        published_at=datetime.now()
    )

    print("\n📤 Syncing test article to Supabase...")
    success = await sync.sync_article(test_article)

    if success:
        print("\n✅ Sync successful!")

        # Get stats
        print("\n📊 Getting Supabase stats...")
        stats = await sync.get_stats()
        print(f"Total articles in Supabase: {stats.get('total_articles', 0)}")

        return True
    else:
        print("\n❌ Sync failed")
        return False


async def main():
    """Main test runner"""
    setup_logger(log_level="INFO")

    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║          Pipeline Components Test Suite                 ║")
    print("╚══════════════════════════════════════════════════════════╝")

    print("\nWhat do you want to test?")
    print("1. LLM Rewriter (OpenRouter)")
    print("2. Supabase Sync")
    print("3. Both")
    print("0. Exit")

    choice = input("\nEnter your choice (0-3): ").strip()

    if choice == "1":
        await test_llm_rewriter()
    elif choice == "2":
        await test_supabase_sync()
    elif choice == "3":
        llm_ok = await test_llm_rewriter()
        if llm_ok:
            await test_supabase_sync()
    elif choice == "0":
        print("Exiting...")
    else:
        print("Invalid choice")

    print("\n✨ Test complete!")


if __name__ == "__main__":
    asyncio.run(main())
