import random
from classes.User import User
from classes.CoffreFort import CoffreFort
from classes.CA import CA
from diffieHellman import compute_secret_value, compute_shared_secret
from mathFunctions import generate_prime
from cobra.cobra import encode_text, decode_text
from hashmac import hmac, normalize_key
from guillouQuisquater import guillou_quisquater_login
from hash import sponge_hash
import json

# Step 1: Verify Safe Certificate
def verify_safe_certificate(ca, user):
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

# Step 2: Authenticate User to Safe
def authenticate_user_to_safe(user, safe):
    print("Step 2: Authenticating User...")
    if guillou_quisquater_login(user, safe):
        print("User authenticated successfully.")
    else:
        print("User authentication failed. Aborting communication.")
        exit(1)

# Step 3: Perform Key Exchange
def perform_key_exchange():
    print("Step 3: Performing Key Exchange...")
    # Generate prime and generator
    p = generate_prime(32)
    g = random.randint(1, p - 1)

    # User generates secret value
    user_private = random.randint(1, p - 1)
    user_public = compute_secret_value(p, g, user_private)

    # Safe generates secret value
    safe_private = random.randint(1, p - 1)
    safe_public = compute_secret_value(p, g, safe_private)

    # Exchange public values and compute shared secret
    user_shared = compute_shared_secret(p, safe_public, user_private)
    safe_shared = compute_shared_secret(p, user_public, safe_private)

    if user_shared != safe_shared:
        print("Key exchange failed: Shared secrets do not match. Aborting.")
        exit(1)

    print(f"Shared secret established: {user_shared}")
    return user_shared

# Step 4: Secure Communication
def secure_communication(shared_secret, user, safe):
    print("Step 4: Secure Communication...")

    # Pass session key through KDF
    shared_secret_kdf = sponge_hash(str(shared_secret), 32)
    # Convert to bytes and normalize to the correct length
    session_key = normalize_key(shared_secret_kdf)
    
    # Simulate message from user to safe
    user_message = "Hello, Safe!"
    encrypted_message = encode_text(user_message, session_key)
    mac = hmac(session_key, user_message.encode('utf-8'))

    print(f"User sends encrypted message: {encrypted_message}")
    print(f"User sends HMAC: {mac}")

    # Safe decrypts and verifies HMAC
    decrypted_message = decode_text(encrypted_message, session_key)
    safe_mac = hmac(session_key, decrypted_message.encode('utf-8'))

    if safe_mac != mac:
        print("HMAC verification failed at safe. Communication compromised.")
        exit(1)

    print(f"Safe received message: {decrypted_message}")

    # Simulate message from safe to user
    safe_message = "Hello, User!"
    encrypted_safe_message = encode_text(safe_message, session_key)
    safe_mac = hmac(session_key, safe_message.encode('utf-8'))

    print(f"Safe sends encrypted message: {encrypted_safe_message}")
    print(f"Safe sends HMAC: {safe_mac}")

    # User decrypts and verifies HMAC
    decrypted_safe_message = decode_text(encrypted_safe_message, session_key)
    user_mac = hmac(session_key, decrypted_safe_message.encode('utf-8'))

    if user_mac != safe_mac:
        print("HMAC verification failed at user. Communication compromised.")
        exit(1)

    print(f"User received message: {decrypted_safe_message}")

# Main Simulation
if __name__ == "__main__":
    # Initialize CA, User, and Safe
    ca = CA()
    user = User("luna")
    user.login("luna", "blabla13")
    safe = CoffreFort()

    # Step 1: Verify the Safe's Certificate
    verify_safe_certificate(ca, user)

    # Step 2: Authenticate User to Safe
    authenticate_user_to_safe(user, safe)

    # Step 3: Key Exchange
    shared_secret = perform_key_exchange()

    # Step 4: Secure Communication
    secure_communication(shared_secret, user, safe)
