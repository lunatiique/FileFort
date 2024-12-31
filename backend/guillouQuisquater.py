
# Guillou-Quisquater protocol implementation (Zero-Knowledge Proof of Identity)
def guillou_quisquater_login(user,coffreFort):
    commitment = user.send_commitment()
    challenge = coffreFort.send_challenge(user)
    response = user.respond_challenge(challenge)
    return coffreFort.verify_challenge(user, response, commitment, challenge)
