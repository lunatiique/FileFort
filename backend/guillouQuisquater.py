
# Fonction qui implémente le protocole Guillou-Quisquater pour l'authentification ZPK
# Entrées : un utilisateur et un coffre fort
def guillou_quisquater_login(user,coffreFort):
    # L'utilisateur envoie son commitment
    commitment = user.send_commitment()
    # Le coffre fort envoie un challenge
    challenge = coffreFort.send_challenge(user)
    # L'utilisateur répond au challenge
    response = user.respond_challenge(challenge)
    # Le coffre fort vérifie la réponse
    return coffreFort.verify_challenge(user, response, commitment, challenge)
