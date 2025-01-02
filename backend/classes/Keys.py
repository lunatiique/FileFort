import sys
import os
import base64
import struct
# Ajouter le chemin du dossier parent pour pouvoir importer les modules hash et mathFunctions
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from hash import sponge_hash
from mathFunctions import inv_mod, coprime, generate_prime, generate_prime_from_seed, bytes_to_int, int_to_bytes

# Classe Keys pour la gestion des clés RSA
class Keys:

    # Constructeur de la classe Keys
    def __init__(self):
        self.e = None
        self.n = None
        self.d = None
        self.v = None

    # Générer une paire de clés RSA (utilisé principalement pour la création de CA et du coffre-fort)
    def generate_key_pair(self, key_size):
        # Générer deux nombres premiers p et q
        p = generate_prime(key_size // 2)
        q = generate_prime(key_size // 2)
        
        # Vérifier que p et q sont distincts
        while p == q:
            q = generate_prime(key_size // 2)
        
        # Calculer n et phi(n)
        self.n = p*q
        phi = (p-1)*(q-1)
        self.e = coprime(phi)
        self.d = inv_mod(self.e, phi)
        # Vérifier que la clé privée est valide
        assert self.e * self.d % phi == 1

    # Générer une paire de clés RSA à partir d'un mot de passe (utilisé pour la création/connexion d'un l'utilisateur)
    def generate_key_pair_from_password(self, password, timestamp, key_size):
        # Dérivation d'une clé à partir du mot de passe et du timestamp
        derived_key = sponge_hash(password + timestamp, key_size // 8)
        # Utilisation de la clé dérivée pour générer p et q
        seed_int = bytes_to_int(derived_key)
        p = generate_prime_from_seed(seed_int, key_size // 2)
        q = generate_prime_from_seed(seed_int + 1, key_size // 2)  # Modifier légèrement le seed pour obtenir un nombre premier différent

        # S'assurer que p et q sont distincts
        while p == q:
            seed_int += 1
            q = generate_prime_from_seed(seed_int, key_size // 2)

        # Calculer n et phi(n)
        self.n = p*q
        phi = (p-1)*(q-1)
        # Choisir un exposant e qui est premier avec phi(n)
        self.e = coprime(phi)
        # Calculer l'exposant d tel que e*d = 1 mod phi(n)
        self.d = inv_mod(self.e, phi)
        # Vérifier que la clé privée est valide
        assert self.e * self.d % phi == 1

    # Lire une clé stockée dans un fichier .PEM
    def read_key(self,path):
        # Ouverture du fichier
        with open(path, "r") as key_file:
            # Lecture du contenu du fichier
            key_data = key_file.read()
            # Identifier le type de clé (publique ou privée)
            if "PUBLIC" in key_data:
                type = "PUBLIC"
            elif "PRIVATE" in key_data:
                type = "PRIVATE"
            else:
                raise ValueError("Invalid key file")

            # Supprimer les en-têtes et pieds du fichier
            key_data = key_data.replace("-----BEGIN PUBLIC KEY-----\n", "").replace("-----END PUBLIC KEY-----\n", "")
            key_data = key_data.replace("-----BEGIN PRIVATE KEY-----\n", "").replace("-----END PRIVATE KEY-----\n", "")
            
            # Nettoyer les données Base64 (supprimer les sauts de ligne)
            key_data = key_data.replace("\n", "").replace("\r", "")
            
            # Ajourter du padding si nécessaire
            if len(key_data) % 4:
                key_data += '=' * (4 - len(key_data) % 4)
            
            # Décoder le contenu Base64
            try:
                key_data = base64.b64decode(key_data)
            except Exception as e:
                print("Error decoding base64:", e)
                return None
            
            # Extraire la longueur de e
            e_length = struct.unpack(">I", key_data[:4])[0]
            # Extraire e et n de la clé
            e = int.from_bytes(key_data[4:4+e_length], byteorder='big')
            n = int.from_bytes(key_data[4+e_length:], byteorder='big')

            # Assigner les valeurs de la clé en fonction du type
            if type == "PUBLIC":
                self.e = e
                self.n = n
            elif type == "PRIVATE":
                self.d = e
                self.n = n
            else:
                raise ValueError("Invalid key file")
    
    # Décoder une clé stockée dans une variable
    def decode_key(self, key_data):
        # Identifier le type de clé (publique ou privé)
        if "-----BEGIN PRIVATE KEY-----" in key_data:
            key_type = "PRIVATE"
        elif "-----BEGIN PUBLIC KEY-----" in key_data:
            key_type = "PUBLIC"
        else:
            raise ValueError("Invalid key file format")

        # Extraire les en-têtes et pieds du fichier
        key_data = key_data.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "")
        key_data = key_data.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "")
        # Supprimer les sauts de ligne, les retours chariots et remplacer les espaces par des +
        key_data = key_data.strip().replace("\n", "").replace("\r", "").replace(" ", "+")

        # Ajouter du padding si nécessaire
        if len(key_data) % 4:
            key_data += "=" * (4 - len(key_data) % 4)

        # Décoder le contenu Base64
        try:
            decoded_key = base64.b64decode(key_data, validate=True)
        except base64.binascii.Error as e:
            raise ValueError(f"Error decoding Base64 content: {e}")

        # Extraire la longueur de e puis e et n de la clé
        try:
            e_length = struct.unpack(">I", decoded_key[:4])[0]
            e = int.from_bytes(decoded_key[4:4 + e_length], byteorder='big')
            n = int.from_bytes(decoded_key[4 + e_length:], byteorder='big')
        except Exception as e:
            raise ValueError(f"Error parsing key components: {e}")

        # Assigner les valeurs de la clé en fonction du type
        if key_type == "PUBLIC":
            self.e = e
            self.n = n
        elif key_type == "PRIVATE":
            self.d = e
            self.n = n

            
    # Vérifier si un mot de passe correspond à une clé stockée
    def check_password(self, name, password, timestamp):
        # Générer un couple de clés à partir du mot de passe et du timestamp
        self.generate_key_pair_from_password(password, timestamp, 1024)
        # Lire les clés stockées dans une deuxième instance de Keys
        new_keys = Keys()
        new_keys.read_key(f"../users/{name}/public_key.pem")
        # Compare les clés générées et les clés stockées (si elles sont identiques, le mot de passe est correct)
        if self.e == new_keys.e and self.n == new_keys.n :
            return True
        else:
            return False

    # Ecriture de la clé publique dans un fichier .PEM dans le dossier de l'utilisateur en format base64
    def write_public_key_to_file(self, path, name):
        # Encodage de la clé publique en bytes
        pub_key_bytes = struct.pack(">I", len(int_to_bytes(self.e))) + int_to_bytes(self.e) + int_to_bytes(self.n)
        # Encodage en base64
        pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
        
        # Ecriture de la clé publique dans un fichier .PEM avec la bonne structure
        public_pem = (
            "-----BEGIN PUBLIC KEY-----\n" +
            pub_key_base64 +
            "-----END PUBLIC KEY-----\n"
        )

        # Ouvrir le fichier et écrire la variable public_pem dedans
        with open(f"{path}/{name}/public_key.pem", "w") as pub_file:
            pub_file.write(public_pem)

    # Ecriture du vérificateur v dans un fichier .PEM dans le dossier de l'utilisateur en format base64
    def write_verificator_to_file(self, path, name):
        # Encodage du vérificateur en bytes
        verificator_bytes = struct.pack(">I", len(int_to_bytes(self.v))) + int_to_bytes(self.v)
        # Encodage en base64
        verificator_base64 = base64.encodebytes(verificator_bytes).decode('ascii')

        # Ecriture du vérificateur dans un fichier .PEM avec la bonne structure
        verificator_pem = (
            "-----BEGIN VERIFICATOR-----\n" +
            verificator_base64 +
            "-----END VERIFICATOR-----\n"
        )

        # Ouvrir le fichier et écrire la variable verificator_pem dedans
        with open(f"{path}/{name}/verificator.pem", "w") as ver_file:
            ver_file.write(verificator_pem)
    
    # Lecture du vérificateur v à partir d'un fichier .PEM
    def read_verificator_from_file(self, path):
        # Ouvrir le fichier
        with open(path, "r") as ver_file:
            # Lire le contenu du fichier
            ver_data = ver_file.read()
            # Supprimer les en-têtes et pieds du fichier
            ver_data = ver_data.replace("-----BEGIN VERIFICATOR-----\n", "").replace("-----END VERIFICATOR-----\n", "")
            # Nettoyer les données Base64 (supprimer les sauts de ligne et les retours chariots)
            ver_data = ver_data.replace("\n", "").replace("\r", "")
            # Ajouter du padding si nécessaire
            if len(ver_data) % 4:
                ver_data += '=' * (4 - len(ver_data) % 4)
            # Décode le contenu Base64
            try:
                ver_data = base64.b64decode(ver_data)
            except Exception as e:
                print("Error decoding base64:", e)
                return None
            # Extraire la longueur de v et la valeur de v
            v_length = struct.unpack(">I", ver_data[:4])[0]
            v = int.from_bytes(ver_data[4:4+v_length], byteorder='big')
            self.v = v

# Pour réaliser des tests sur la classe Keys
if __name__ == "__main__":
    keys = Keys()
    timestamp = str(os.stat(f"../users/luna").st_birthtime)
    print(keys.check_password("luna", "blabla13", timestamp))