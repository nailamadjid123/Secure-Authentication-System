import hashlib
import time
import random
import os
import sys

class AuthenticationSystem:
    def __init__(self):
        self.password_file = "password.txt"
        self.failed_attempts = {}
        self.lock_times = {}
        self.banished_accounts = set()
        self.initialize_password_file()
        
    def initialize_password_file(self):
        if not os.path.exists(self.password_file):
            with open(self.password_file, 'w') as f:
                pass
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    # ---------------------------------------------------------
    #       COMPTE À REBOURS SUR UNE SEULE LIGNE
    # ---------------------------------------------------------
    def display_countdown(self, seconds, message):
        print(f"\n⏰ {message}")
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r⏳ Blocage ({seconds}s) : {i} ")
            sys.stdout.flush()
            time.sleep(1)
        sys.stdout.write("\r✅ Blocage terminé !                      \n")

    # ---------------------------------------------------------
    #       HASH + SALT
    # ---------------------------------------------------------
    def hash_password(self, password, salt):
        return hashlib.sha256((password + salt).encode()).hexdigest()
    
    def generate_salt(self):
        return ''.join(random.choices('0123456789', k=5))

    # ---------------------------------------------------------
    #       VALIDATIONS
    # ---------------------------------------------------------
    def validate_username(self, username):
        if len(username) != 5:
            print("❌ Le username doit avoir exactement 5 caractères")
            return False
        if not username.islower() or not username.isalpha():
            print("❌ Le username doit contenir 5 lettres minuscules")
            return False
        return True
    
    def validate_password(self, password):
        if len(password) != 8:
            print("❌ Le password doit avoir exactement 8 caractères")
            return False
        
        if not any(c.islower() for c in password):
            print("❌ Le password doit contenir au moins une minuscule")
            return False
        if not any(c.isupper() for c in password):
            print("❌ Le password doit contenir au moins une majuscule")
            return False
        if not any(c.isdigit() for c in password):
            print("❌ Le password doit contenir au moins un chiffre")
            return False
        
        return True

    # ---------------------------------------------------------
    #       LOCK / BAN / TIMER
    # ---------------------------------------------------------
    def is_account_locked(self, username):
        if username in self.banished_accounts:
            return True, "🚫 COMPTE BANNI DÉFINITIVEMENT"

        if username in self.lock_times:
            remaining = self.lock_times[username] - time.time()
            if remaining > 0:
                return True, f"Compte verrouillé ({int(remaining)} secondes restantes)"
            else:
                del self.lock_times[username]
                # 🔥 Correction : ON NE RÉINITIALISE PLUS LES TENTATIVES !
        
        return False, ""

    def update_lock_time(self, username):
        attempts = self.failed_attempts.get(username, 0)

        lock_time = 0
        if attempts == 3:
            lock_time = 5
        elif attempts == 6:
            lock_time = 10
        elif attempts == 9:
            lock_time = 20

        elif attempts >= 10:
            print("🚫 Trop d'échecs. COMPTE BANNI DÉFINITIVEMENT.")
            self.banished_accounts.add(username)
            return
        
        if lock_time > 0:
            self.lock_times[username] = time.time() + lock_time
            print(f"🔒 Trop d'échecs. Verrouillage {lock_time} secondes.")
            self.display_countdown(lock_time, f"Verrouillage du compte '{username}'")

    # ---------------------------------------------------------
    #       SIGN UP
    # ---------------------------------------------------------
    def signup(self):
        print("\n" + "="*50)
        print("📝 INSCRIPTION")
        print("="*50)
        
        while True:
            username = input("Username (5 lettres minuscules): ").strip()
            if not self.validate_username(username):
                continue
            if self.user_exists(username):
                print("❌ Username déjà utilisé")
                continue
            break
        
        while True:
            print("\nExemple valide : Abc12345")
            password = input("Password : ").strip()
            if self.validate_password(password):
                break
        
        salt = self.generate_salt()
        hashed_password = self.hash_password(password, salt)

        with open(self.password_file, 'a') as f:
            f.write(f"{username}:{hashed_password}:{salt}\n")
        
        print("✅ Inscription réussie !")

    def user_exists(self, username):
        with open(self.password_file, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
                if len(parts) == 3 and parts[0] == username:
                    return True
        return False

    # ---------------------------------------------------------
    #       SIGN IN
    # ---------------------------------------------------------
    def signin(self):
        print("\n" + "="*50)
        print("🔑 CONNEXION")
        print("="*50)

        username = input("Username : ").strip()

        locked, msg = self.is_account_locked(username)
        if locked:
            print("⛔", msg)
            return

        user_data = self.get_user_data(username)
        if not user_data:
            print("❌ Utilisateur introuvable")
            return
        
        stored_username, stored_hash, salt = user_data

        password = input("Password : ").strip()

        if self.hash_password(password, salt) == stored_hash:
            print("✅ Connexion réussie ! Bienvenue.")
            if username in self.failed_attempts:
                del self.failed_attempts[username]
        else:
            print("❌ Mot de passe incorrect")
            self.failed_attempts[username] = self.failed_attempts.get(username, 0) + 1
            print(f"⚠️ Tentative échouée n°{self.failed_attempts[username]}")
            self.update_lock_time(username)

    def get_user_data(self, username):
        with open(self.password_file, 'r') as f:
            for line in f:
                parts = line.strip().split(':')
            if len(parts) == 3 and parts[0] == username:
                return parts
        return None

    # ---------------------------------------------------------
    #       CLEAN FILE
    # ---------------------------------------------------------
    def clean_password_file(self):
        if not os.path.exists(self.password_file):
            return
        
        with open(self.password_file, 'r') as f:
            lines = f.readlines()

        valid = [l.strip() for l in lines if l.count(':') == 2]

        with open(self.password_file, 'w') as f:
            for l in valid:
                f.write(l + '\n')

        print("🧹 Fichier nettoyé.")

    # ---------------------------------------------------------
    #       MENU
    # ---------------------------------------------------------
    def exit_app(self):
        print("\n🙏 Merci d'avoir utilisé le système.")
        print("👋 Au revoir !")
        return True
    
    def display_menu(self):
        print("\n" + "="*50)
        print("🔐 SYSTÈME D'AUTHENTIFICATION")
        print("="*50)
        print("1. 📝 S'inscrire")
        print("2. 🔑 Se connecter")
        print("3. 🧹 Nettoyer le fichier")
        print("4. 🚪 Quitter")
        print("="*50)
    
    def run(self):
        self.clear_screen()
        while True:
            self.display_menu()
            choice = input("🎯 Choisissez une option : ").strip()

            if choice == '1':
                self.signup()
            elif choice == '2':
                self.signin()
            elif choice == '3':
                self.clean_password_file()
            elif choice == '4':
                if self.exit_app():
                    break
            else:
                print("❌ Option invalide.")

            input("\n⏎ Appuyez sur Entrée pour continuer...")
            self.clear_screen()

# ---------------------------------------------------------
#       LANCEMENT
# ---------------------------------------------------------
if __name__ == "__main__":
    app = AuthenticationSystem()
    app.run()
