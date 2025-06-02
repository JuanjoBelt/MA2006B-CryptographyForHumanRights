import os
import sys
import json
import shutil

USERS_DIR = './certs/users'
REVOKED_USERS_PATH = './certs/revoked.json'

def revoke_user(email: str):
    user_dir = os.path.join(USERS_DIR, email)

    if not os.path.isdir(user_dir):
        print(f"[X] No certificate directory found for user '{email}'.")
        return

    # Delete the directory with cert and key
    shutil.rmtree(user_dir)
    print(f"Removed user certificate files: {user_dir}")

    # Add to revoked list (optional)
    if os.path.exists(REVOKED_USERS_PATH):
        with open(REVOKED_USERS_PATH, 'r') as f:
            revoked_list = json.load(f)
    else:
        revoked_list = []

    if email not in revoked_list:
        revoked_list.append(email)
        with open(REVOKED_USERS_PATH, 'w') as f:
            json.dump(revoked_list, f, indent=2)
        print(f"📜 User '{email}' added to revoked list.")

    print("Revocation complete.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python revoke_user.py <user_email>")
        sys.exit(1)

    user_email = sys.argv[1]
    revoke_user(user_email)