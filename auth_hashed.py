import hashlib
import os
import time
import re
import random

PASSWORD_FILE = "password.txt"


# =======================================================
#  UTILITAIRES
# =======================================================

def generate_salt():
    """Génère un salt de 5 chiffres."""
    return ''.join(str(random.randint(0, 9)) for _ in range(5))


def hash_password(password, salt):
    """Retourne SHA-256(password + salt)."""
    data = password + salt
    return hashlib.sha256(data.encode()).hexdigest()


def username_exists(username):
    """Vérifie si un username existe déjà dans le fichier."""
    if not os.path.exists(PASSWORD_FILE):
        return False

    with open(PASSWORD_FILE, "r") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3 and parts[0] == username:
                return True
    return False


def save_user(username, salt, hashcode):
    """Enregistre un nouvel utilisateur."""
    with open(PASSWORD_FILE, "a") as f:
        f.write(f"{username}|{salt}|{hashcode}\n")


def load_users():
    """Charge les utilisateurs dans une dict : {username: (salt, hash)}"""
    users = {}
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, "r") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) == 3:
                    users[parts[0]] = (parts[1], parts[2])
    return users


# =======================================================
#  SIGN UP
# =======================================================

def signup():
    print("\n===== SIGN UP =====")

    # Username validation
    while True:
        username = input("Enter username (5 lowercase letters) : ")
        if re.fullmatch(r"[a-z]{5}", username):
            if username_exists(username):
                print("⚠️ Username already exists, choose another.")
            else:
                break
        else:
            print("❌ Username must contain EXACTLY 5 lowercase letters.")

    # Password validation
    while True:
        password = input("Enter password (8 chars: a-z A-Z 0-9): ")
        if re.fullmatch(r"[A-Za-z0-9]{8}", password):
            break
        else:
            print("❌ Password must be 8 characters (letters + digits).")

    # Salt + hash
    salt = generate_salt()
    hashcode = hash_password(password, salt)

    # Save to file
    save_user(username, salt, hashcode)
    print("✔️ User registered successfully!\n")


# =======================================================
#  SIGN IN
# =======================================================

def signin():
    print("\n===== SIGN IN =====")

    users = load_users()

    username = input("Username: ")

    if username not in users:
        print("❌ User does not exist.\n")
        return

    salt, correct_hash = users[username]

    attempt_count = 0
    block_steps = [5, 10, 15, 20]  # seconds
    block_index = 0

    while True:
        password = input("Password: ")
        hashcode = hash_password(password, salt)

        if hashcode == correct_hash:
            print("✔️ Login successful!\n")
            return

        # Wrong password
        attempt_count += 1
        print("❌ Wrong password.")

        if attempt_count % 3 == 0:
            if block_index < len(block_steps):
                delay = block_steps[block_index]
                block_index += 1
                print(f"⛔ Too many attempts. Blocked for {delay} seconds...")
                time.sleep(delay)
            else:
                print("🚫 Account permanently banned.\n")
                return


# =======================================================
#  MAIN MENU
# =======================================================

def main():
    while True:
        print("===== MENU =====")
        print("1. Sign up")
        print("2. Sign in")
        print("3. Exit")

        choice = input("Your choice: ")

        if choice == "1":
            signup()
        elif choice == "2":
            signin()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":
    main()
