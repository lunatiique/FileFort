# This files contains the functions to sign and verify a message using RSA signature scheme.

from hash import merkle_damgard_hash
from generateKeyPair import generate_key_pair

# Signing
def sign_message(message, private_key):
    d, n = private_key
    # hash the message
    h = merkle_damgard_hash(message)
    # convert hex string h to int
    h = int(h, 16)
    # sign : h^d mod n
    signature = pow(h, d, n)
    return signature

# Verification
def verify_signature(message, signature, public_key):
    e, n = public_key
    # hash the message
    h = merkle_damgard_hash(message)
    # convert hex string h to int
    h = int(h, 16)
    # verify : signature^e mod n == h
    h_from_signature = pow(signature, e, n)
    return h == h_from_signature

# Example usage
if __name__ == "__main__":
    # Generate RSA keys
    public_key, private_key = generate_key_pair(1024)

    # Message
    message = "123"

    # Sign the message
    signature = sign_message(message, private_key)
    print("Signature:", signature)

    # Verify the signature
    valid = verify_signature(message, signature, public_key)
    print("Signature valid:", valid)
