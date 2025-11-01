#!/usr/bin/env python3
"""
Seed Database Script
Seeds the food_macros collection with top 100 foods
"""

import asyncio
import os
import sys

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    print("=" * 70)
    print("🌱 SEEDING FOOD MACROS DATABASE")
    print("=" * 70)
    print()
    
    # Import after path is set
    from app.services.seed_food_macros import seed_food_macros_database
    
    try:
        await seed_food_macros_database()
        print()
        print("=" * 70)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 70)
        return 0
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ ERROR: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)




