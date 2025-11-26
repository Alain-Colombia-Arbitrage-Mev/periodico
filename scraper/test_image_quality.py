#!/usr/bin/env python3
"""
Test script for Image Quality Assessment
Tests the new CV-based image validation system
"""
import asyncio
from pathlib import Path
from src.utils.image_quality_assessor import ImageQualityAssessor
from src.utils.image_handler import ImageHandler
from loguru import logger


async def test_image_quality():
    """Test image quality assessment on sample images"""

    print("\n" + "="*70)
    print("IMAGE QUALITY ASSESSMENT TEST")
    print("="*70 + "\n")

    # Test URLs - mix of good and bad images
    test_images = [
        {
            'url': 'https://www.infobae.com/new-resizer/123.jpg',
            'category': 'politica',
            'expected': 'Should be a real news photo'
        },
        {
            'url': 'https://www.lanacion.com.ar/resizer/v2/logo.png',
            'category': 'economia',
            'expected': 'Should be rejected (logo)'
        },
        {
            'url': 'https://www.clarin.com/img/2024/01/article-image.jpg',
            'category': 'judicial',
            'expected': 'Should be a real news photo'
        }
    ]

    # Initialize image handler
    handler = ImageHandler(
        output_dir="data/test_images",
        max_size=2048,
        quality=85,
        timeout=30
    )

    print("Starting image quality tests...\n")

    results = {
        'accepted': 0,
        'rejected': 0,
        'errors': 0
    }

    for i, test_img in enumerate(test_images, 1):
        print(f"\n{'─'*70}")
        print(f"Test {i}/{len(test_images)}")
        print(f"{'─'*70}")
        print(f"URL: {test_img['url']}")
        print(f"Category: {test_img['category']}")
        print(f"Expected: {test_img['expected']}")
        print()

        try:
            # Download image with quality validation
            result = await handler.download_image(
                url=test_img['url'],
                category=test_img['category']
            )

            if result:
                print(f"✅ ACCEPTED - Image path: {result}")
                results['accepted'] += 1
            else:
                print(f"❌ REJECTED - Image did not pass quality validation")
                results['rejected'] += 1

        except Exception as e:
            print(f"⚠️  ERROR - {e}")
            results['errors'] += 1

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Accepted: {results['accepted']}")
    print(f"❌ Rejected: {results['rejected']}")
    print(f"⚠️  Errors: {results['errors']}")
    print(f"Total: {len(test_images)}")
    print()

    # Test quality assessment on existing images
    print("\n" + "="*70)
    print("TESTING QUALITY ASSESSMENT ON SAMPLE IMAGES")
    print("="*70 + "\n")

    test_dir = Path("data/test_images")
    if test_dir.exists():
        sample_images = list(test_dir.rglob("*.jpg"))[:5]  # First 5 images

        if sample_images:
            print(f"Found {len(sample_images)} sample images to analyze\n")

            for img_path in sample_images:
                print(f"\n{'─'*70}")
                print(f"Analyzing: {img_path.name}")
                print(f"{'─'*70}")

                try:
                    assessment = ImageQualityAssessor.comprehensive_assessment(img_path)

                    print(f"Overall Score: {assessment['overall_score']}/100")
                    print(f"Quality Tier: {assessment['quality_tier'].upper()}")
                    print(f"Acceptable: {'✅ YES' if assessment['is_acceptable'] else '❌ NO'}")

                    if assessment['rejection_reasons']:
                        print(f"\nRejection Reasons:")
                        for reason in assessment['rejection_reasons']:
                            print(f"  • {reason}")

                    print(f"\nDetailed Metrics:")
                    print(f"  Sharpness: {assessment['sharpness']['laplacian_variance']:.1f} "
                          f"({'✅ Sharp' if assessment['sharpness']['is_sharp'] else '❌ Blurry'})")
                    print(f"  Colors: {assessment['color']['unique_colors']} unique "
                          f"({'✅ Diverse' if assessment['color']['is_diverse'] else '❌ Limited'})")
                    print(f"  Edge Density: {assessment['edges']['edge_density']:.2%} "
                          f"({'✅ Complex' if assessment['edges']['is_complex'] else '❌ Simple'})")
                    print(f"  Brightness: {assessment['exposure']['mean_brightness']:.1f} "
                          f"({'✅ Good' if assessment['exposure']['is_well_exposed'] else '❌ Poor'})")
                    print(f"  Contrast: {assessment['exposure']['contrast']:.1f} "
                          f"({'✅ Good' if assessment['exposure']['has_contrast'] else '❌ Low'})")

                except Exception as e:
                    print(f"⚠️  Error analyzing image: {e}")
        else:
            print("No sample images found in test directory")
    else:
        print("Test directory not found")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run tests
    asyncio.run(test_image_quality())
