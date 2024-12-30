import random
import os 
import sys
import json
# Add the parent folder (where classes is located) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from classes.CA import CA
from classes.Keys import Keys

class User:
    def __init__(self, name):
        self.name = name # public
        self.e = None
        self.n = None
        self.v = None

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
        v = pow(keys.d, keys.e, keys.n)
        # TODO : pas fini ici oh
        keys.write_keys_to_file("../users/", name)

    # Fonction pour qu'un utilisateur se connecte
    def login(self, name, password):
        # Vérifier d'abord si le nom de l'utilisateur existe
        if not os.path.exists(f"../users/{name}"):
            return False
        # Vérifier si le mot de passe entré par l'utilisateur est correct
        # Obtenir le timestamp du dossier de l'utilisateur sous forme de string
        timestamp = str(os.path.getctime(f"../users/{name}"))
        keys = Keys()
        check = keys.check_password(name, password, timestamp)
        # Si check est faux, le mot de passe ne correspond pas
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
        keys.read_key(f"../users/{name}/public_key.pem")
        # TODO : gestion de la clé privée ?? lien avec simulateCommunication
        keys.read_key(f"../users/{name}/private_key.pem")
        self.e = keys.e
        self.n = keys.n
        self.d = keys.d
        self.v = pow(self.d, self.e, self.n)
        #échanger clé de session

        

        return True

    # Send commitment using a fresh random value r.
    def send_commitment(self):
        # Generate a random value r coprime to n
        self.r = random.randint(0, self.n-1)
        while self.r % self.n == 0:
            self.r = random.randint(0, self.n-1)
        # Calculate commitment x = r^e mod n
        x = pow(self.r, self.e, self.n)
        return x

    # Respond to the challenge using the secret and r.
    def respond_challenge(self, c):
        # Compute response y = r * d^c mod n
        y = (self.r * pow(self.d, c, self.n)) % self.n
        return y


if __name__ == "__main__":
    #test
    user = User("luna")
    user.login("luna", "blabla13")
