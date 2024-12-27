from classes.User import User
from classes.CoffreFort import CoffreFort
from generateKeyPair import read_key

user = User("blabla", read_key("users/blabla/public_key.pem"), read_key("users/blabla/private_key.pem"))
file = CoffreFort()

# Guillou-Quisquater protocol implementation (Zero-Knowledge Proof of Identity)
def guillou_quisquater_login(user,file):
    commitment = user.send_commitment()
    challenge = file.send_challenge(user)
    response = user.respond_challenge(challenge)
    return file.verify_challenge(user, response, commitment, challenge)

if __name__ == "__main__":
    print(guillou_quisquater_login(user,file))