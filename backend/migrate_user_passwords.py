"""Migrate existing user passwords to new bcrypt format.

This script will prompt you to reset passwords for existing users
since we can't decrypt the old hashes.
"""
import sys
sys.path.insert(0, '.')

from app.db.base import initialize_firestore, Collections
from app.services.auth import get_password_hash

# Initialize Firestore
db = initialize_firestore()
print("✅ Firestore initialized\n")

# Get all users
users_ref = db.collection(Collections.USERS)
users = users_ref.stream()

user_list = []
for user_doc in users:
    user_data = user_doc.to_dict()
    user_list.append({
        'id': user_doc.id,
        'email': user_data.get('email'),
        'current_hash': user_data.get('hashed_password', '')
    })

if not user_list:
    print("No users found in database.")
    sys.exit(0)

print(f"Found {len(user_list)} user(s):\n")
for i, user in enumerate(user_list, 1):
    print(f"{i}. {user['email']} (ID: {user['id']})")

print("\n" + "="*60)
print("PASSWORD RESET REQUIRED")
print("="*60)
print("\nThe authentication system has been updated.")
print("You need to set new passwords for existing users.\n")

for user in user_list:
    print(f"\nUser: {user['email']}")
    print("-" * 40)
    
    # Prompt for new password
    new_password = input("Enter new password (or 'skip' to skip): ").strip()
    
    if new_password.lower() == 'skip':
        print("⏭️  Skipped")
        continue
    
    if len(new_password) < 8:
        print("❌ Password must be at least 8 characters. Skipping...")
        continue
    
    # Hash the new password
    new_hash = get_password_hash(new_password)
    
    # Update in Firestore
    db.collection(Collections.USERS).document(user['id']).update({
        'hashed_password': new_hash
    })
    
    print(f"✅ Password updated for {user['email']}")

print("\n✅ Migration complete!")
