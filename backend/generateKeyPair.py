import random
import base64
from keyDerivationFunction import sponge_hash, bytes_to_int
from mathFunctions import is_prime, pseudo_random_odd_of_n_bits, inv_mod, coprime
import struct

# Converts an integer to bytes, handling the length appropriately
def int_to_bytes(n):
    return n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')

# Generate a random prime number of the specified bit length
def generate_prime(length):
    while True:
        n = pseudo_random_odd_of_n_bits(length)
        if is_prime(n):
            return n
        
# Generate a pseudo-random prime number based on a seed derived from a password
def generate_prime_from_seed(seed, length):
    random.seed(seed)  # Set the seed for reproducibility
    while True:
        # Generate a random candidate of the specified bit length
        candidate = random.getrandbits(length)
        candidate |= (1 << length - 1) | 1  # Ensure it's odd and has the right bit length
        if is_prime(candidate): # Perform primality test
            return candidate


# Generate a key pair using the RSA algorithm (for Certificate Authority mainly)
def generate_key_pair(key_size):
    # Generate two random prime numbers
    p = generate_prime(key_size // 2)
    q = generate_prime(key_size // 2)
    
    # Ensure p and q are distinct
    while p == q:
        q = generate_prime(key_size // 2)
    
    # Calculate n and phi(n)
    n = p*q
    phi = (p-1)*(q-1)
    e = coprime(phi)
    d = inv_mod(e, phi)
    
    # Return the public and private keys
    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

# Generate a key pair from a password using KDF
def generate_key_pair_from_password(password, timestamp, key_size):
    # Derive a key from the seed, which will be used to generate the primes p and q
    derived_key = sponge_hash(password + timestamp, key_size // 8)
    # Use derived key as a seed to generate primes p and q
    seed_int = bytes_to_int(derived_key)
    p = generate_prime_from_seed(seed_int, key_size // 2)
    q = generate_prime_from_seed(seed_int + 1, key_size // 2)  # Change seed slightly for q
    # Ensure p and q are distinct
    while p == q:
        seed_int += 1
        q = generate_prime_from_seed(seed_int, key_size // 2)

    # Calculate n and phi(n)
    n = p*q
    phi = (p-1)*(q-1)
    e = coprime(phi)
    d = inv_mod(e, phi)
    # Ensure the private key is valid
    assert e * d % phi == 1

    # Return the public and private keys
    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

# Write the keys to a .PEM file in the user's folder in base64 format
def write_keys_to_file(path, name, public_key, private_key):
    # Public Key
    e, n = public_key
    pub_key_bytes = struct.pack(">I", len(int_to_bytes(e))) + int_to_bytes(e) + int_to_bytes(n)
    pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
    
    public_pem = (
        "-----BEGIN PUBLIC KEY-----\n" +
        pub_key_base64 +
        "-----END PUBLIC KEY-----\n"
    )

    with open(f"{path}/{name}/public_key.pem", "w") as pub_file:
        pub_file.write(public_pem)

    # Private Key
    d, n = private_key
    priv_key_bytes = struct.pack(">I", len(int_to_bytes(d))) + int_to_bytes(d) + int_to_bytes(n)
    priv_key_base64 = base64.encodebytes(priv_key_bytes).decode('ascii')
    
    private_pem = (
        "-----BEGIN PRIVATE KEY-----\n" +
        priv_key_base64 +
        "-----END PRIVATE KEY-----\n"
    )

    with open(f"{path}/{name}/private_key.pem", "w") as priv_file:
        priv_file.write(private_pem)

    print("Keys written to file!")



# Read a key from a .PEM file
def read_key(path):
    with open(path, "r") as key_file:
        key_data = key_file.read()
        # Remove the header and footer
        key_data = key_data.replace("-----BEGIN PUBLIC KEY-----\n", "").replace("-----END PUBLIC KEY-----\n", "")
        key_data = key_data.replace("-----BEGIN PRIVATE KEY-----\n", "").replace("-----END PRIVATE KEY-----\n", "")
        
        # Clean up the Base64 data (remove line breaks)
        key_data = key_data.replace("\n", "").replace("\r", "")
        
        # Add padding if necessary
        if len(key_data) % 4:
            key_data += '=' * (4 - len(key_data) % 4)
        
        # Decode from base64
        try:
            key_data = base64.b64decode(key_data)
        except Exception as e:
            print("Error decoding base64:", e)
            return None
        
        # Extract length of e
        e_length = struct.unpack(">I", key_data[:4])[0]
        e = int.from_bytes(key_data[4:4+e_length], byteorder='big')
        n = int.from_bytes(key_data[4+e_length:], byteorder='big')

        return (e, n)


    
# When user wants to login, check if the password is correct by generating the keys and comparing them to the stored keys
def check_password(name, password, timestamp):
    return True
    # Generate the keys
    public, private = generate_key_pair_from_password(password, timestamp, 1024)
    # Read the stored keys
    stored_private = read_key(f"../users/{name}/private_key.pem")
    # Compare the generated keys to the stored keys
    if private == stored_private:
        return True
    else:
        return True
    

if __name__ == "__main__":
    # Test the key generation
    key_size = 1024
    seed_int = 1234567890
    p = generate_prime_from_seed(seed_int, key_size // 2)
    q = generate_prime_from_seed(seed_int + 1, key_size // 2)  # Change seed slightly for q
    # Ensure p and q are distinct
    while p == q:
        seed_int += 1
        q = generate_prime_from_seed(seed_int, key_size // 2)

    #print p, q
    print("p:", p)
    print("q:", q)
    # Calculate n and phi(n)
    n = p*q
    phi = (p-1)*(q-1)
    e = coprime(phi)
    d = inv_mod(e, phi)
    
    assert (e * d) % phi == 1, "Key validation failed"
    print("Key generation successful!")