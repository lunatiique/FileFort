from hash import merkle_damgard_hash
from classes.Keys import Keys

# Fonction pour signer un message à l'aide d'une clé privée
def sign_message(message, private_key):
    d, n = private_key
    # Hasher le message
    h = merkle_damgard_hash(message)
    # Convertir la chaîne hexadécimale h en entier
    h = int(h, 16)
    # Signature : h^d mod n
    signature = pow(h, d, n)
    return signature

# Fonction pour vérifier une signature à l'aide d'une clé publique
def verify_signature(message, signature, public_key):
    e, n = public_key
    # Hasher le message
    h = merkle_damgard_hash(message)
    # Convertir la chaîne hexadécimale h en entier
    h = int(h, 16)
    # Vérifier la signature : signature^e mod n == h
    h_from_signature = pow(signature, e, n)
    return h == h_from_signature

# Exemple d'utilisation
if __name__ == "__main__":
    # Génerer clés RSA
    keys = Keys()
    keys.generate_key_pair(1024)

    # Message
    message = "123"

    # Signer le message
    signature = sign_message(message, (keys.d, keys.n))
    print("Signature:", signature)

    # Verifier la signature
    valid = verify_signature(message, signature, (keys.e, keys.n))
    print("Signature valide:", valid)
