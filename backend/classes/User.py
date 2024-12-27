import random

class User:
    def __init__(self, name, public_key, private_key):
        self.name = name # public
        self.e, self.n = public_key # public
        self.d, _ = private_key # private
        self.v = pow(self.d, self.e, self.n) # public verification value

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
