#!/usr/bin/env python3
"""
Audit Firestore collections to identify field naming patterns.
This script checks actual field names in the database to guide our fix strategy.
"""

import os
import sys
from google.cloud import firestore
from dotenv import load_dotenv

# Load environment
load_dotenv()
load_dotenv('.env.local', override=True)

def audit_collection(db, collection_name, limit=5):
    """Audit a Firestore collection and report field names"""
    print(f"\n{'='*80}")
    print(f"📊 AUDITING: {collection_name}")
    print(f"{'='*80}\n")
    
    try:
        docs = db.collection(collection_name).limit(limit).stream()
        doc_count = 0
        
        for doc in docs:
            doc_count += 1
            data = doc.to_dict()
            
            print(f"Document {doc_count}: {doc.id}")
            print(f"{'─'*80}")
            
            # Print all field names and their types
            for field_name, value in sorted(data.items()):
                value_type = type(value).__name__
                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  • {field_name:30} ({value_type:15}) = {value_preview}")
            
            print()
        
        if doc_count == 0:
            print(f"⚠️  No documents found in {collection_name}")
        else:
            print(f"✅ Audited {doc_count} documents in {collection_name}\n")
    
    except Exception as e:
        print(f"❌ Error auditing {collection_name}: {e}\n")

def check_field_naming_pattern(db, collection_name):
    """Check if collection uses snake_case or camelCase"""
    print(f"\n🔍 Checking naming pattern for {collection_name}...")
    
    try:
        docs = db.collection(collection_name).limit(10).stream()
        
        snake_case_fields = set()
        camel_case_fields = set()
        
        for doc in docs:
            data = doc.to_dict()
            for field_name in data.keys():
                if '_' in field_name:
                    snake_case_fields.add(field_name)
                elif any(c.isupper() for c in field_name):
                    camel_case_fields.add(field_name)
        
        print(f"\n  Snake_case fields: {sorted(snake_case_fields)}")
        print(f"  CamelCase fields: {sorted(camel_case_fields)}")
        
        if snake_case_fields and not camel_case_fields:
            print(f"  ✅ Result: {collection_name} uses snake_case consistently")
        elif camel_case_fields and not snake_case_fields:
            print(f"  ⚠️  Result: {collection_name} uses camelCase")
        elif snake_case_fields and camel_case_fields:
            print(f"  ❌ Result: {collection_name} has MIXED naming conventions!")
        else:
            print(f"  ℹ️  Result: {collection_name} has no multi-word fields")
    
    except Exception as e:
        print(f"  ❌ Error: {e}")

def generate_migration_script(db):
    """Generate a migration script based on findings"""
    print(f"\n{'='*80}")
    print(f"📝 MIGRATION RECOMMENDATIONS")
    print(f"{'='*80}\n")
    
    collections = ['tasks', 'fitness_logs', 'user_profiles']
    
    for collection_name in collections:
        try:
            # Check first document
            docs = list(db.collection(collection_name).limit(1).stream())
            if not docs:
                print(f"⚠️  {collection_name}: No documents to analyze")
                continue
            
            data = docs[0].to_dict()
            fields = list(data.keys())
            
            # Check for problematic fields
            problematic = []
            if 'dueDate' in fields:
                problematic.append("'dueDate' → should be 'due_date'")
            if 'userId' in fields:
                problematic.append("'userId' → should be 'user_id'")
            if 'logType' in fields:
                problematic.append("'logType' → should be 'log_type'")
            if 'createdAt' in fields:
                problematic.append("'createdAt' → should be 'created_at'")
            if 'updatedAt' in fields:
                problematic.append("'updatedAt' → should be 'updated_at'")
            
            if problematic:
                print(f"❌ {collection_name}: NEEDS MIGRATION")
                for issue in problematic:
                    print(f"   • {issue}")
            else:
                print(f"✅ {collection_name}: Field names look good")
        
        except Exception as e:
            print(f"❌ {collection_name}: Error - {e}")
    
    print(f"\n{'='*80}\n")

def main():
    """Main audit function"""
    print(f"\n{'#'*80}")
    print(f"# FIRESTORE FIELD NAMING AUDIT")
    print(f"{'#'*80}\n")
    
    # Initialize Firestore
    project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'productivityai-mvp')
    print(f"🔗 Connecting to project: {project_id}\n")
    
    try:
        db = firestore.Client(project=project_id)
        print("✅ Connected to Firestore\n")
    except Exception as e:
        print(f"❌ Failed to connect to Firestore: {e}")
        sys.exit(1)
    
    # Audit each collection
    collections = [
        'tasks',
        'fitness_logs', 
        'user_profiles',
        'users',  # Check if this exists
    ]
    
    for collection in collections:
        audit_collection(db, collection, limit=3)
        check_field_naming_pattern(db, collection)
    
    # Generate recommendations
    generate_migration_script(db)
    
    print(f"\n{'#'*80}")
    print(f"# AUDIT COMPLETE")
    print(f"{'#'*80}\n")
    print("Next steps:")
    print("1. Review the field names above")
    print("2. Check FIELD_NAMING_AUDIT.md for fix plan")
    print("3. Update models and queries to match actual field names")
    print("4. Deploy updated Firestore indexes")
    print("5. Test complete flow\n")

if __name__ == '__main__':
    main()
