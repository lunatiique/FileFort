import json 
import time
import sys
import os
import struct
import base64
# Ajouter le chemin du dossier parent pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mathFunctions import int_to_bytes
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
        # On encode la clé publique du coffre fort en bytes
        pub_key_bytes = struct.pack(">I", len(int_to_bytes(self.keys.e))) + int_to_bytes(self.keys.e) + int_to_bytes(self.keys.n)
        # On la convertit en base64
        pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
        # On retourne le contenu du certificat
        return {
            "name": "FileFort",
            "contact": "Luna Schenk",
            "organization": "FileFort&Co",
            "domain name": "filefort.com",
            "public_key": pub_key_base64,
            "issued": time.time(),
            "expiration": time.time() + 31536000 # Valide pour un an
        }

    # Fonction pour créer un certificat signé par le CA
    def create_certificate(content):
        keys = Keys()
        # On récupère la clé privée du CA
        keys.read_key("users/CA/private_key.pem")
        # On récupère le contenu du certificat
        content_dump = json.dumps(content)
        # On signe le contenu du certificat avec la clé privée du CA
        signature = sign_message(content_dump, (keys.d, keys.n))
        # On retourne une structure JSON contenant le contenu du certificat et la signature
        return {
            "content" : content,
            "signature" : signature
        }

    # Vérifier un certificat signé par le CA
    def verify_certificate(self, cert):
        # On récupère le contenu et la signature du certificat
        content = cert["content"]
        signature = cert["signature"]
        # On récupère la clé publique du coffre fort
        key_data = (self.keys.e, self.keys.n)
        # On convertit le contenu en JSON
        content_dump = json.dumps(content)
        return verify_signature(content_dump, signature, key_data)

    # Créer un certificat pour le coffre fort
    def create_safe_certificate(self):
        # On crée le contenu du certificat
        content = self.create_content_certificate_safe()
        # On crée le certificat en signant le contenu
        certificate = self.create_certificate(content)
        # On écrit le certificat JSON à la localisation suivante : users/Filefort/certificate.json
        with open("users/Filefort/certificate.json", "w") as file:
            json.dump(certificate, file, indent=4)
            return certificate

