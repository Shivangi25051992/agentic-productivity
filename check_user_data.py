import os
from google.cloud import firestore

os.environ['GOOGLE_CLOUD_PROJECT'] = 'productivityai-mvp'
db = firestore.Client()

# Find user by email
users = db.collection('users').where('email', '==', 'test@test.com').limit(1).stream()
user_data = None
user_id = None

for user in users:
    user_id = user.id
    user_data = user.to_dict()
    print(f"✅ Found user: {user_id}")
    print(f"Email: {user_data.get('email')}")
    print(f"Created: {user_data.get('created_at')}")
    break

if not user_id:
    print("❌ User not found with email test@test.com")
    print("\nTrying tets@teste.com...")
    users = db.collection('users').where('email', '==', 'tets@teste.com').limit(1).stream()
    for user in users:
        user_id = user.id
        user_data = user.to_dict()
        print(f"✅ Found user: {user_id}")
        print(f"Email: {user_data.get('email')}")
        break

if user_id:
    # Check profile
    print("\n" + "="*60)
    print("USER PROFILE:")
    print("="*60)
    profile = db.collection('user_profiles').document(user_id).get()
    if profile.exists:
        profile_data = profile.to_dict()
        print(f"Name: {profile_data.get('name')}")
        print(f"Timezone: {profile_data.get('timezone', 'NOT SET ❌')}")
        print(f"Units: {profile_data.get('units', 'NOT SET')}")
        print(f"Goal: {profile_data.get('fitness_goal')}")
        print(f"Activity Level: {profile_data.get('activity_level')}")
    else:
        print("❌ Profile not found")
    
    # Check recent fitness logs
    print("\n" + "="*60)
    print("RECENT FITNESS LOGS (Last 5):")
    print("="*60)
    logs = db.collection('users').document(user_id).collection('fitness_logs').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
    log_count = 0
    for log in logs:
        log_count += 1
        log_data = log.to_dict()
        print(f"\nLog {log_count}:")
        print(f"  ID: {log.id}")
        print(f"  Category: {log_data.get('category')}")
        print(f"  Item: {log_data.get('item', 'N/A')}")
        print(f"  Meal Type: {log_data.get('meal_type', 'N/A')}")
        print(f"  Calories: {log_data.get('calories', 0)}")
        print(f"  Timestamp: {log_data.get('timestamp')}")
        print(f"  Summary: {log_data.get('summary', 'N/A')}")
    
    if log_count == 0:
        print("❌ No fitness logs found")
    
    # Check chat history
    print("\n" + "="*60)
    print("RECENT CHAT MESSAGES (Last 5):")
    print("="*60)
    
    # Try new structure first
    sessions = db.collection('users').document(user_id).collection('chat_sessions').limit(1).stream()
    session_found = False
    for session in sessions:
        session_found = True
        messages = db.collection('users').document(user_id).collection('chat_sessions').document(session.id).collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
        msg_count = 0
        for msg in messages:
            msg_count += 1
            msg_data = msg.to_dict()
            print(f"\nMessage {msg_count}:")
            print(f"  Role: {msg_data.get('role')}")
            print(f"  Content: {msg_data.get('content', '')[:100]}")
            print(f"  Timestamp: {msg_data.get('timestamp')}")
        if msg_count == 0:
            print("❌ No messages in session")
        break
    
    if not session_found:
        print("❌ No chat sessions found")
        print("\nTrying old structure...")
        old_msgs = db.collection('chat_history').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5).stream()
        old_count = 0
        for msg in old_msgs:
            old_count += 1
            msg_data = msg.to_dict()
            print(f"\nMessage {old_count}:")
            print(f"  Role: {msg_data.get('role')}")
            print(f"  Content: {msg_data.get('content', '')[:100]}")
        if old_count == 0:
            print("❌ No old chat history found")

else:
    print("\n❌ Could not find user")

