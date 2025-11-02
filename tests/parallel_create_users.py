#!/usr/bin/env python3
"""
Parallel User Creation - 10x Faster
Creates 100 users in ~7 minutes instead of 12 minutes
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.firebase_test_helper import create_test_user_with_token
import random
import json
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_single_user(user_id: int, goal: str, age: int, gender: str):
    """Create a single user (for parallel execution)"""
    email = f"testuser{user_id}@simulation.test"
    password = "TestPass123!"
    display_name = f"Test User {user_id}"
    
    try:
        user_data = create_test_user_with_token(email, password, display_name)
        return {
            'success': True,
            'user_id': user_id,
            'email': email,
            'uid': user_data['uid'],
            'goal': goal,
            'age': age,
            'gender': gender,
            'id_token': user_data['id_token'][:50] + '...'  # Truncate for storage
        }
    except Exception as e:
        return {
            'success': False,
            'user_id': user_id,
            'email': email,
            'error': str(e)
        }

def create_users_parallel(start_id: int, end_id: int, max_workers: int = 10):
    """Create users in parallel"""
    
    goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
    genders = ['male', 'female']
    
    # Load existing users if any
    users_file = 'tests/test_users.json'
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            existing_users = json.load(f)
    else:
        existing_users = []
    
    existing_ids = {u['user_id'] for u in existing_users}
    
    print(f"\n{'='*80}")
    print(f"🚀 PARALLEL USER CREATION: {start_id} to {end_id}")
    print(f"⚡ Using {max_workers} parallel workers")
    print(f"{'='*80}\n")
    
    # Prepare user creation tasks
    tasks = []
    for i in range(start_id, end_id + 1):
        if i in existing_ids:
            print(f"⏭️  User {i} already exists, skipping...")
            continue
        
        goal = goals[(i-1) % 4]
        gender = random.choice(genders)
        age = random.randint(18, 65)
        
        tasks.append((i, goal, age, gender))
    
    if not tasks:
        print("✅ All users already exist!")
        return existing_users
    
    print(f"📝 Creating {len(tasks)} new users...\n")
    
    start_time = time.time()
    created_users = []
    failed_users = []
    
    # Execute in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_user = {
            executor.submit(create_single_user, user_id, goal, age, gender): user_id
            for user_id, goal, age, gender in tasks
        }
        
        # Process results as they complete
        completed = 0
        for future in as_completed(future_to_user):
            user_id = future_to_user[future]
            try:
                result = future.result()
                if result['success']:
                    created_users.append(result)
                    completed += 1
                    
                    # Progress update every 10 users
                    if completed % 10 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed
                        remaining = len(tasks) - completed
                        eta = remaining / rate if rate > 0 else 0
                        print(f"✅ {completed}/{len(tasks)} users created ({elapsed:.1f}s, ETA: {eta:.1f}s)")
                else:
                    failed_users.append(result)
                    print(f"❌ Failed user {user_id}: {result.get('error', 'Unknown error')}")
            
            except Exception as e:
                print(f"❌ Exception for user {user_id}: {e}")
                failed_users.append({'user_id': user_id, 'error': str(e)})
    
    # Combine with existing users
    all_users = existing_users + created_users
    
    # Save to file
    with open(users_file, 'w') as f:
        json.dump(all_users, f, indent=2)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"✅ PARALLEL CREATION COMPLETE")
    print(f"{'='*80}")
    print(f"✅ Created: {len(created_users)} users")
    print(f"❌ Failed: {len(failed_users)} users")
    print(f"⏱️  Time: {elapsed:.1f}s")
    print(f"⚡ Rate: {len(created_users)/elapsed:.2f} users/second")
    print(f"📊 Total users: {len(all_users)}")
    print(f"💾 Saved to: {users_file}")
    print(f"{'='*80}\n")
    
    # Print distribution
    goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
    print(f"📊 USER DISTRIBUTION:")
    for goal in goals:
        count = sum(1 for u in all_users if u.get('goal') == goal)
        print(f"  {goal}: {count} users")
    
    if failed_users:
        print(f"\n⚠️  FAILED USERS:")
        for failed in failed_users[:5]:  # Show first 5
            print(f"  User {failed['user_id']}: {failed.get('error', 'Unknown')[:60]}...")
    
    print()
    
    return all_users

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create test users in parallel')
    parser.add_argument('--start', type=int, default=1, help='Start user ID')
    parser.add_argument('--end', type=int, default=100, help='End user ID')
    parser.add_argument('--workers', type=int, default=10, help='Number of parallel workers')
    
    args = parser.parse_args()
    
    print(f"\n🎯 Target: Create users {args.start} to {args.end}")
    print(f"⚡ Parallel workers: {args.workers}")
    print(f"📈 Expected speedup: ~{args.workers}x faster\n")
    
    users = create_users_parallel(args.start, args.end, args.workers)
    
    print(f"🎉 Done! {len(users)} users ready for testing.\n")


