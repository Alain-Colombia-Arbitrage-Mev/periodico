#!/usr/bin/env python3
"""
Quick run script for the complete news pipeline
Usage: python3 run_pipeline.py
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Load environment variables from .env if exists
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    print(f"📝 Loading environment from {env_file}")
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value.strip()

# Import and run
from pipeline_complete import main
import asyncio

if __name__ == '__main__':
    print("🚀 Starting News Pipeline...")
    print("=" * 80)
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
