import random

class CoffreFort:
    def __init__(self):
        self.name = "FileFort"

    # Send a challenge to the user
    def send_challenge(self,user):
        # Generate a random challenge in [0, n-1]
        return random.randint(0, user.n-1)
    
    # Verify the challenge response
    def verify_challenge(self, user, result_challenge, commitment, challenge):
        # Compute the value val1 = (result_challenge^e * v^-challenge) mod n
        val1 = (pow(result_challenge, user.e, user.n) * pow(user.v, -challenge, user.n)) % user.n
        # Check if val1 is equal to the commitment
        return val1 == commitment
