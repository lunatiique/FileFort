import random
from classes.Keys import Keys
# Classe représentant le coffre fort
class CoffreFort:
    # Constructeur
    def __init__(self):
        self.name = "FileFort"
        self.keys = Keys()
        self.keys.read_key("../users/Filefort/public_key.pem")
        self.keys.read_key("../users/Filefort/private_key.pem")
        self.shared_secret = None

    # Envoi d'un challenge à l'utilisateur (dans le cadre de l'authentification ZPK Guillou-Quisquater)
    def send_challenge(self,user):
        # Générer un challenge aléatoire entre 0 et n-1
        return random.randint(0, user.keys.n-1)
    
    # Vérification du challenge envoyé par l'utilisateur
    def verify_challenge(self, user, result_challenge, commitment, challenge):
        # Calculer la valeur val1 = (result_challenge^e * v^-challenge) mod n
        val1 = (pow(result_challenge, user.keys.e, user.keys.n) * pow(user.keys.v, -challenge, user.keys.n)) % user.keys.n
        # Retourner le résultat de la comparaison entre val1 et le commitment (qui sont censés être égaux si l'utilisateur a bien répondu au challenge)
        return val1 == commitment
