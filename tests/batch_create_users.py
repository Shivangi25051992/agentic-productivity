#!/usr/bin/env python3
"""
Batch Create Test Users with Progress Tracking
Creates users in batches and saves progress to file
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

def create_users_batch(start_id: int, end_id: int, batch_size: int = 10):
    """Create users in batches with progress tracking"""
    
    goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
    genders = ['male', 'female']
    
    # Load existing users if any
    users_file = 'tests/test_users.json'
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            users = json.load(f)
    else:
        users = []
    
    existing_ids = {u['user_id'] for u in users}
    
    print(f"\n{'='*80}")
    print(f"🚀 CREATING USERS {start_id} to {end_id}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    created_count = 0
    
    for i in range(start_id, end_id + 1):
        if i in existing_ids:
            print(f"⏭️  User {i} already exists, skipping...")
            continue
        
        goal = goals[(i-1) % 4]  # Distribute evenly across goals
        gender = random.choice(genders)
        age = random.randint(18, 65)
        
        email = f"testuser{i}@simulation.test"
        password = "TestPass123!"
        display_name = f"Test User {i}"
        
        try:
            user_data = create_test_user_with_token(email, password, display_name)
            users.append({
                'user_id': i,
                'email': email,
                'uid': user_data['uid'],
                'goal': goal,
                'age': age,
                'gender': gender,
                'id_token': user_data['id_token'][:50] + '...'  # Truncate for storage
            })
            created_count += 1
            
            # Save progress every 5 users
            if created_count % 5 == 0:
                with open(users_file, 'w') as f:
                    json.dump(users, f, indent=2)
                elapsed = time.time() - start_time
                print(f"✅ Created {created_count}/{end_id - start_id + 1} users ({elapsed:.1f}s elapsed)")
        
        except Exception as e:
            print(f"❌ Error creating user {i}: {e}")
    
    # Final save
    with open(users_file, 'w') as f:
        json.dump(users, f, indent=2)
    
    elapsed = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"✅ BATCH COMPLETE: Created {created_count} new users")
    print(f"⏱️  Time: {elapsed:.1f}s ({elapsed/max(created_count, 1):.2f}s per user)")
    print(f"📊 Total users in database: {len(users)}")
    print(f"💾 Saved to: {users_file}")
    print(f"{'='*80}\n")
    
    return users

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create test users in batches')
    parser.add_argument('--start', type=int, default=1, help='Start user ID')
    parser.add_argument('--end', type=int, default=10, help='End user ID')
    
    args = parser.parse_args()
    
    users = create_users_batch(args.start, args.end)
    
    # Print summary
    goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
    print(f"\n📊 USER DISTRIBUTION:")
    for goal in goals:
        count = sum(1 for u in users if u['goal'] == goal)
        print(f"  {goal}: {count} users")

