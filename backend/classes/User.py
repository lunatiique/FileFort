import random
import os 
import sys
import json
# Ajouter le chemin du dossier parent pour pouvoir importer les modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from classes.CA import CA
from classes.Keys import Keys
from classes.CoffreFort import CoffreFort
from guillouQuisquater import guillou_quisquater_login

# Classe User : représente un utilisateur du coffre fort
# Un utilisateur est caractérisé par son nom, ses clés et une valeur aléatoire r (pour l'authentification ZPK)
class User:
    # Constructeur
    def __init__(self):
        self.name = None
        self.keys = None
        self.r = None

    # Fonction pour créer un utilisateur (nom d'utilisateur, mot de passe)
    def create(self, name, password):
        # Créer un dossier pour l'utilisateur dans le dossier users
        os.mkdir(f"../users/{name}")
        # Ajouter un sous-dossier data pour l'utilisateur
        os.mkdir(f"../users/{name}/data")
        # Récupérer le timestamp de la création du dossier de l'utilisateur (afin de générer un couple de clés unique)
        timestamp = os.stat(f"../users/{name}").st_birthtime  
        # Convertir le timestamp en string
        timestamp = str(timestamp)
        # Générer le couple de clés
        keys = Keys()
        keys.generate_key_pair_from_password(password, timestamp, 1024)
        # Générer la valeur de vérification v de l'utilisateur (pour ZPK)
        keys.v = pow(keys.d, keys.e, keys.n)
        # Enregistrer la clé publique de l'utilisateur dans un fichier .PEM
        keys.write_public_key_to_file("../users/", name)
        # Enregistrer le vérificateur v dans un fichier .PEM
        keys.write_verificator_to_file("../users/", name)
        # Retourner la clé privée de l'utilisateur afin que celui-ci puisse la stocker en lieu sûr
        return keys.d, keys.n

    # Fonction pour qu'un utilisateur se connecte (nom d'utilisateur, mot de passe, clé privée)
    # La clé privée est nécessaire pour l'authentification ZPK (simplification pour le projet, mais non sécurisé)
    def login(self, name, password, privateKey):
        # Vérifier d'abord si le nom de l'utilisateur existe
        if not os.path.exists(f"../users/{name}"):
            return False
        # Obtenir le timestamp du dossier de l'utilisateur sous forme de string
        timestamp = str(os.path.getctime(f"../users/{name}"))
        keys = Keys()
        # Vérifier si le mot de passe entré par l'utilisateur est correct
        check = keys.check_password(name, password, timestamp)
        # Si le check est faux, le mot de passe ne correspond pas
        if not check:
            return False
        # On procède à l'authentification double-sens :
        # 1. Demander le certificat du coffre fort
        # Dans le cadre du projet, le certificat est généré et stocké dans le dossier du coffre fort (users/Filefort/certificate.json)
        cert = json.load(open("../users/Filefort/certificate.json"))
        # 2. Vérifier certificat auprès de l'autorité
        ca = CA()
        verif = ca.verify_certificate(cert)
        if not verif:
            raise ValueError("Certificate verification failed")
        # 3. S'authentifier auprès du coffre-fort (ZPK)
        keys = Keys()
        # Lecture des données publiques : clé publique et vérificateur
        keys.read_key(f"../users/{name}/public_key.pem")
        keys.read_verificator_from_file(f"../users/{name}/verificator.pem")
        # SIMPLIFICATION POUR LE PROJET : On récupère la clé privée pour réaliser l'authentification ZPK
        keys.d = privateKey.d
        # Assosier les clés à l'utilisateur
        self.keys = keys
        # Créer un objet CoffreFort
        cf = CoffreFort()
        # Authentification ZPK
        zpk = guillou_quisquater_login(self, cf)
        # Si l'authentification ZPK échoue, on retourne False
        if not zpk:
            return False
        return True

    # Envoyer commitment en utilisant une valeur aléatoire r
    def send_commitment(self):
        # Générer une valeur aléatoire r entre 0 et n-1, copremier avec n
        self.r = random.randint(0, self.keys.n-1)
        while self.r % self.keys.n == 0:
            self.r = random.randint(0, self.keys.n-1)
        # Calculer le commitment x = r^e mod n
        x = pow(self.r, self.keys.e, self.keys.n)
        return x

    # Répondre au challenge reçu par le coffre fort
    def respond_challenge(self, c):
        # Calculer la réponse y = r*d^c mod n
        y = (self.r * pow(self.keys.d, c, self.keys.n)) % self.keys.n
        return y

# Pour réaliser des tests sur la classe User
if __name__ == "__main__":
    user = User()
    keys = Keys()
    keys.read_verificator_from_file("../users/caca2/verificator.pem")

