import json 
import time
import sys
import os
# Add the parent folder (where classes is located) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mathFunctions import int_to_bytes
import struct
import base64
from signature import sign_message, verify_signature
from classes.Keys import Keys

# Fonction pour crééer une autorité de certification (CA) dans la base des utilisateurs et générer clé publique/privée
# Dans le cadre de ce projet, toutes les informations du CA sont stockées dans la base des utilisateurs mais en pratique, le CA est une entité externe
def create_certificate_authority():
    keys = Keys()
    keys.generate_key_pair(1024)
    keys.write_keys_to_file("users", "CA")

# Classe pour l'autorité de certification
class CA:
    # Initialisation de l'autorité de certification (on récupère les clés publique et privée du CA)
    def __init__(self):
        self.keys = Keys()
        self.keys.read_key("../users/CA/public_key.pem")
        self.keys.read_key("../users/CA/private_key.pem")

    # Fonction pour créer le contenu du certificat du coffre fort
    def create_content_certificate_safe(self):
        pub_key_bytes = struct.pack(">I", len(int_to_bytes(self.keys.e))) + int_to_bytes(self.keys.e) + int_to_bytes(self.keys.n)
        pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
        return {
            "name": "FileFort",
            "contact": "Luna Schenk",
            "organization": "FileFort&Co",
            "domain name": "filefort.com",
            "public_key": pub_key_base64,
            "issued": time.time(),
            "expiration": time.time() + 31536000
        }

    # Fonction pour créer un certificat signé par le CA
    def create_certificate(content):
        keys = Keys()
        keys.read_key("users/CA/private_key.pem")
        content_dump = json.dumps(content)
        signature = sign_message(content_dump, (keys.d, keys.n))
        return {
            "content" : content,
            "signature" : signature
        }

    # Vérifier un certificat signé par le CA
    def verify_certificate(self, cert):
        content = cert["content"]
        signature = cert["signature"]
        key_data = (self.keys.e, self.keys.n)
        content_dump = json.dumps(content)
        return verify_signature(content_dump, signature, key_data)

    # Créer un certificat pour le coffre fort
    def create_safe_certificate(self):
        content = self.create_content_certificate_safe()
        certificate = self.create_certificate(content)
        # write the JSON certificate to a file in users/Filefort/certificate.json
        with open("users/Filefort/certificate.json", "w") as file:
            json.dump(certificate, file, indent=4)
            return certificate

