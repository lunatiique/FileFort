import random

# Classe représentant le coffre fort
class CoffreFort:
    # Constructeur
    def __init__(self):
        self.name = "FileFort"

    # Envoi d'un challenge à l'utilisateur
    def send_challenge(self,user):
        # Générer un challenge aléatoire entre 0 et n-1
        return random.randint(0, user.keys.n-1)
    
    # Verify the challenge response
    def verify_challenge(self, user, result_challenge, commitment, challenge):
        # Compute the value val1 = (result_challenge^e * v^-challenge) mod n
        val1 = (pow(result_challenge, user.keys.e, user.keys.n) * pow(user.keys.v, -challenge, user.keys.n)) % user.keys.n
        # Check if val1 is equal to the commitment
        return val1 == commitment
