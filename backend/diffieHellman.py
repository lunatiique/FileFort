import random
from generateKeyPair import generate_prime

def compute_secret_value(p, g, a):
    # Compute the public key
    A = pow(g, a, p)
    return A

def compute_shared_secret(p, B, a):
    # Compute the shared secret
    s = pow(B, a, p)
    return s


def simulate_diffie_hellman():
    # Generate a random prime number p and a random number g smaller than p together
    p = generate_prime(32)
    g = random.randint(1, p - 1)
    #Alice secretely chooses a random number a
    a = random.randint(1, p - 1)
    #Bob secretely chooses a random number b
    b = random.randint(1, p - 1)
    # Compute secret value for Alice
    A = compute_secret_value(p, g, a)
    # Compute secret value for Bob
    B = compute_secret_value(p, g, b)
    # Compute shared secret for Alice
    secret_alice = compute_shared_secret(p, B, a)
    # Compute shared secret for Bob
    secret_bob = compute_shared_secret(p, A, b)
    # Check if the shared secret is the same
    print(secret_alice)
    print(secret_alice == secret_bob)


if __name__ == '__main__':
    simulate_diffie_hellman()
