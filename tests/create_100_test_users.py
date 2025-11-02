#!/usr/bin/env python3
"""
Create 100 Test Users in Bulk
Pre-creates users so simulation can run faster
"""

import sys
import os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.firebase_test_helper import create_test_user_with_token
import random

def create_100_users():
    """Create 100 test users with different personas"""
    
    goals = ['lose_weight', 'gain_muscle', 'maintain', 'improve_fitness']
    genders = ['male', 'female']
    
    users = []
    
    print(f"\n{'='*80}")
    print(f"🚀 CREATING 100 TEST USERS")
    print(f"{'='*80}\n")
    
    for i in range(1, 101):
        goal = goals[(i-1) % 4]  # Distribute evenly across goals
        gender = random.choice(genders)
        age = random.randint(18, 65)
        
        email = f"testuser{i}@simulation.test"
        password = "TestPass123!"
        display_name = f"Test User {i} ({goal}, {age}y, {gender})"
        
        try:
            user_data = create_test_user_with_token(email, password, display_name)
            users.append({
                'user_id': i,
                'email': email,
                'uid': user_data['uid'],
                'goal': goal,
                'age': age,
                'gender': gender,
                'id_token': user_data['id_token']
            })
            
            if i % 10 == 0:
                print(f"✅ Created {i}/100 users...")
        
        except Exception as e:
            print(f"❌ Error creating user {i}: {e}")
    
    print(f"\n{'='*80}")
    print(f"✅ CREATED {len(users)} USERS")
    print(f"{'='*80}\n")
    
    # Save user data for simulation
    import json
    with open('tests/test_users.json', 'w') as f:
        json.dump(users, f, indent=2)
    
    print(f"💾 User data saved to: tests/test_users.json")
    
    # Print summary
    print(f"\n📊 USER DISTRIBUTION:")
    for goal in goals:
        count = sum(1 for u in users if u['goal'] == goal)
        print(f"  {goal}: {count} users")
    
    return users

if __name__ == "__main__":
    users = create_100_users()


