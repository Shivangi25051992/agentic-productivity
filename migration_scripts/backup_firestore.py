#!/usr/bin/env python3
"""
Backup Firestore collections before migration
"""

import os
import json
from datetime import datetime
from google.cloud import firestore
from google.oauth2 import service_account
from pathlib import Path

# Initialize Firestore with service account
project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "productivityai-mvp")
credentials_path = "/Users/pchintanwar/keys/productivityai-mvp-0017f7241a58.json"

credentials = service_account.Credentials.from_service_account_file(credentials_path)
db = firestore.Client(project=project_id, credentials=credentials)

# Collections to backup
COLLECTIONS = ["users", "tasks", "fitness_logs", "chat_history", "food_database"]

def backup_collection(collection_name: str, output_dir: Path):
    """Backup a single collection to JSON"""
    print(f"📦 Backing up {collection_name}...")
    
    collection_ref = db.collection(collection_name)
    docs = collection_ref.stream()
    
    backup_data = []
    count = 0
    
    for doc in docs:
        data = doc.to_dict()
        data['_id'] = doc.id  # Preserve document ID
        
        # Convert timestamps to ISO strings
        for key, value in data.items():
            if hasattr(value, 'isoformat'):
                data[key] = value.isoformat()
        
        backup_data.append(data)
        count += 1
        
        if count % 100 == 0:
            print(f"  Backed up {count} documents...")
    
    # Write to file
    output_file = output_dir / f"{collection_name}.json"
    with open(output_file, 'w') as f:
        json.dump(backup_data, f, indent=2)
    
    print(f"✅ Backed up {count} documents to {output_file}")
    return count

def main():
    """Main backup function"""
    print("=" * 70)
    print("🔒 FIRESTORE BACKUP - Pre-Migration")
    print("=" * 70)
    print(f"Project: {project_id}")
    print(f"Time: {datetime.now().isoformat()}")
    print()
    
    # Create backup directory
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(f"backups/pre-migration-{timestamp}")
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 Backup directory: {backup_dir}")
    print()
    
    # Backup each collection
    total_docs = 0
    for collection in COLLECTIONS:
        try:
            count = backup_collection(collection, backup_dir)
            total_docs += count
        except Exception as e:
            print(f"❌ Error backing up {collection}: {e}")
    
    # Create metadata file
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "project_id": project_id,
        "collections": COLLECTIONS,
        "total_documents": total_docs,
        "backup_directory": str(backup_dir)
    }
    
    with open(backup_dir / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print()
    print("=" * 70)
    print(f"✅ BACKUP COMPLETE")
    print("=" * 70)
    print(f"Total documents backed up: {total_docs}")
    print(f"Backup location: {backup_dir}")
    print()
    print("⚠️  IMPORTANT: Verify backup before proceeding with migration!")
    print()

if __name__ == "__main__":
    main()

