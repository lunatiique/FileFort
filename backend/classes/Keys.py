import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import base64
from hash import sponge_hash
from mathFunctions import inv_mod, coprime, generate_prime, generate_prime_from_seed, bytes_to_int, int_to_bytes
import struct

class Keys:
    def __init__(self):
        self.e = None
        self.n = None
        self.d = None

    # Generate a key pair using the RSA algorithm (for Certificate Authority mainly)
    def generate_key_pair(self, key_size):
        # Generate two random prime numbers
        p = generate_prime(key_size // 2)
        q = generate_prime(key_size // 2)
        
        # Ensure p and q are distinct
        while p == q:
            q = generate_prime(key_size // 2)
        
        # Calculate n and phi(n)
        self.n = p*q
        phi = (p-1)*(q-1)
        self.e = coprime(phi)
        self.d = inv_mod(self.e, phi)
        assert self.e * self.d % phi == 1

    # Generate a key pair from a password using KDF
    def generate_key_pair_from_password(self, password, timestamp, key_size):
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
        self.n = p*q
        phi = (p-1)*(q-1)
        self.e = coprime(phi)
        self.d = inv_mod(self.e, phi)
        # Ensure the private key is valid
        assert self.e * self.d % phi == 1

    # Lire une clé stockée dans un fichier .PEM
    def read_key(self,path):
        with open(path, "r") as key_file:
            key_data = key_file.read()
            print("2")
            print(key_data)
            # Identifier le type de clé (publique ou privée)
            if "PUBLIC" in key_data:
                type = "PUBLIC"
            elif "PRIVATE" in key_data:
                type = "PRIVATE"
            else:
                raise ValueError("Invalid key file")

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

            if type == "PUBLIC":
                self.e = e
                self.n = n
            elif type == "PRIVATE":
                self.d = e
                self.n = n
            else:
                raise ValueError("Invalid key file")
            
    def decode_key(self, key_data):
        # Identify the key type
        if "-----BEGIN PRIVATE KEY-----" in key_data:
            key_type = "PRIVATE"
        elif "-----BEGIN PUBLIC KEY-----" in key_data:
            key_type = "PUBLIC"
        else:
            raise ValueError("Invalid key file format")

        # Extract Base64 content between the header and footer
        key_data = key_data.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        key_data = key_data.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")
        print(key_data)
        # Remove any whitespace or newline characters
        key_data = key_data.strip().replace("\n", "").replace("\r", "").replace(" ", "+")

        # Add padding if necessary
        if len(key_data) % 4:
            key_data += "=" * (4 - len(key_data) % 4)

        # Decode Base64
        try:
            decoded_key = base64.b64decode(key_data, validate=True)
        except base64.binascii.Error as e:
            raise ValueError(f"Error decoding Base64 content: {e}")

        # Extract e and n
        try:
            e_length = struct.unpack(">I", decoded_key[:4])[0]
            e = int.from_bytes(decoded_key[4:4 + e_length], byteorder='big')
            n = int.from_bytes(decoded_key[4 + e_length:], byteorder='big')
        except Exception as e:
            raise ValueError(f"Error parsing key components: {e}")

        # Assign key values
        if key_type == "PUBLIC":
            self.e = e
            self.n = n
        elif key_type == "PRIVATE":
            self.d = e
            self.n = n

            
    # When user wants to login, check if the password is correct by generating the keys and comparing them to the stored keys
    def check_password(self, name, password, timestamp):
        # Generate the keys
        self.generate_key_pair_from_password(password, timestamp, 1024)
        # Read the stored keys in another key instance
        new_keys = Keys()
        new_keys.read_key(f"../users/{name}/public_key.pem")
        # Compare the generated keys to the stored keys
        if self.e == new_keys.e and self.n == new_keys.n :
            return True
        else:
            return False

    def write_public_key_to_file(self, path, name):
        pub_key_bytes = struct.pack(">I", len(int_to_bytes(self.e))) + int_to_bytes(self.e) + int_to_bytes(self.n)
        pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
        
        public_pem = (
            "-----BEGIN PUBLIC KEY-----\n" +
            pub_key_base64 +
            "-----END PUBLIC KEY-----\n"
        )

        with open(f"{path}/{name}/public_key.pem", "w") as pub_file:
            pub_file.write(public_pem)

    # Ecriture de la clé privée dans un fichier .PEM dans le dossier de l'utilisateur en format base64 (dans un but de test)
    def write_private_key_to_file(self, path, name):
        priv_key_bytes = struct.pack(">I", len(int_to_bytes(self.d))) + int_to_bytes(self.d) + int_to_bytes(self.n)
        priv_key_base64 = base64.encodebytes(priv_key_bytes).decode('ascii')
        
        private_pem = (
            "-----BEGIN PRIVATE KEY-----\n" +
            priv_key_base64 +
            "-----END PRIVATE KEY-----\n"
        )

        with open(f"{path}/{name}/private_key.pem", "w") as priv_file:
            priv_file.write(private_pem)

    # Write the keys to a .PEM file in the user's folder in base64 format
    def write_keys_to_file(self, path, name):
        self.write_private_key_to_file(path, name)
        self.write_public_key_to_file(path, name)
        print("Keys written to file!")

if __name__ == "__main__":
    keys = Keys()
    timestamp = str(os.stat(f"../users/luna").st_birthtime)
    print(keys.check_password("luna", "blabla13", timestamp))