import random
from classes.User import User
from classes.CoffreFort import CoffreFort
from classes.CA import CA
from classes.Keys import Keys
from diffieHellman import compute_secret_value, compute_shared_secret
from mathFunctions import generate_prime
from cobra.cobra import encode_text, decode_text
from hashmac import hmac, normalize_key
from guillouQuisquater import guillou_quisquater_login
from hash import sponge_hash
import json

# Fichier de simulation de communication sécurisée entre un utilisateur et un coffre fort

# Etape 1: Vérifier le certificat du coffre fort
def verify_safe_certificate(ca):
    print("Step 1: Verifying Safe Certificate...")
    # 1. Demander le certificat du coffre fort
    # Dans le cadre du projet, le certificat est généré et stocké dans le dossier du coffre fort (users/Filefort/certificate.json)
    cert = json.load(open("../users/Filefort/certificate.json"))
    # 2. Vérifier certificat auprès de l'autorité
    certificate_valid = ca.verify_certificate(cert)
    if certificate_valid:
        print("Certificate is valid.")
    else:
        print("Certificate is invalid. Aborting communication.")
        exit(1)
    
# Étape 2: Authentifier l'utilisateur auprès du coffre fort
def authenticate_user_to_safe(user, safe):
    print("Étape 2: Authentification de l'utilisateur...")
    if guillou_quisquater_login(user, safe):
        print("Utilisateur authentifié avec succès.")
    else:
        print("Échec de l'authentification de l'utilisateur. Abandon de la communication.")
        exit(1)

# Étape 3: Échange de clés
def perform_key_exchange(user, safe):
    print("Étape 3: Échange de clés...")

    # Générer un nombre premier et un générateur
    p = generate_prime(32)
    g = random.randint(1, p - 1)

    # L'utilisateur génère une valeur secrète
    user_private = random.randint(1, p - 1)
    user_public = compute_secret_value(p, g, user_private)

    # Le coffre fort génère une valeur secrète
    safe_private = random.randint(1, p - 1)
    safe_public = compute_secret_value(p, g, safe_private)

    # Échanger les valeurs publiques et calculer le secret partagé
    compute_shared_secret(p, safe_public, user_private, user)
    compute_shared_secret(p, user_public, safe_private, safe)

    if user.shared_secret != safe.shared_secret:
        print("Échec de l'échange de clés : les secrets partagés ne correspondent pas. Abandon.")
        exit(1)

    print(f"Secret partagé établi : {user.shared_secret}")

# Étape 4: Communication sécurisée
def secure_communication(user, safe):
    print("Étape 4: Communication sécurisée...")

    # Passer la clé de session par le KDF
    shared_secret_kdf = sponge_hash(str(safe.shared_secret), 32)
    # Convertir en octets et normaliser à la longueur correcte
    session_key = normalize_key(shared_secret_kdf)
            
    # Simuler un message de l'utilisateur au coffre fort
    user_message = "Bonjour, Coffre Fort!"
    encrypted_message = encode_text(user_message, session_key)
    mac = hmac(session_key, user_message.encode('utf-8'))

    print(f"L'utilisateur envoie un message chiffré : {encrypted_message}")
    print(f"L'utilisateur envoie un HMAC : {mac}")

     # Le coffre fort déchiffre et vérifie le HMAC
    decrypted_message = decode_text(encrypted_message, session_key)
    safe_mac = hmac(session_key, decrypted_message.encode('utf-8'))

    if safe_mac != mac:
        print("Échec de la vérification du HMAC au coffre fort. Communication compromise.")
        exit(1)

    print(f"Le coffre fort a reçu le message : {decrypted_message}")

    # Simuler un message du coffre fort à l'utilisateur
    safe_message = "Bonjour, Utilisateur!"
    encrypted_safe_message = encode_text(safe_message, session_key)
    safe_mac = hmac(session_key, safe_message.encode('utf-8'))

    print(f"Le coffre fort envoie un message chiffré : {encrypted_safe_message}")
    print(f"Le coffre fort envoie un HMAC : {safe_mac}")

    # L'utilisateur déchiffre et vérifie le HMAC
    decrypted_safe_message = decode_text(encrypted_safe_message, session_key)
    user_mac = hmac(session_key, decrypted_safe_message.encode('utf-8'))

    if user_mac != safe_mac:
        print("Échec de la vérification du HMAC chez l'utilisateur. Communication compromise.")
        exit(1)

    print(f"L'utilisateur a reçu le message : {decrypted_safe_message}")

# Simulation principale
if __name__ == "__main__":
    # Initialiser CA, Utilisateur et Coffre Fort
    ca = CA()
    user = User()
    private_key = Keys()
    private_key.read_key("../users/luna/luna_private_key.pem")
    user.login("luna", "blabla13", private_key)
    safe = CoffreFort()

    # Étape 1: Vérifier le certificat du coffre fort
    verify_safe_certificate(ca)

    # Étape 2: Authentifier l'utilisateur auprès du coffre fort
    authenticate_user_to_safe(user, safe)

    # Étape 3: Échange de clés
    perform_key_exchange(user, safe)

    # Étape 4: Communication sécurisée
    secure_communication(user, safe)
