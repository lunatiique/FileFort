from classes.User import User
from classes.CoffreFort import CoffreFort

# Guillou-Quisquater protocol implementation (Zero-Knowledge Proof of Identity)
def guillou_quisquater_login(user,file):
    print("user : ", user.n)
    commitment = user.send_commitment()
    challenge = file.send_challenge(user)
    response = user.respond_challenge(challenge)
    return file.verify_challenge(user, response, commitment, challenge)

if __name__ == "__main__":

    user = User()
    file = CoffreFort()
    print(guillou_quisquater_login(user,file))