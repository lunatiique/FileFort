import random
from mathFunctions import generate_prime

# Calculer la valeur secrète pour un utilisateur (p et g sont publics, a est privé)
def compute_secret_value(p, g, a):
    # Calculer la valeur secrète
    A = pow(g, a, p)
    return A

# Calculer le secret partagé entre deux utilisateurs (p est public, B est la valeur secrète de l'autre utilisateur, a est privé)
def compute_shared_secret(p, B, a, user):
    # Compute the shared secret
    user.shared_secret = pow(B, a, p)


# Fonction pour simuler Diffie-Hellman entre deux utilisateurs (Alice et Bob)
def simulate_diffie_hellman():
    # Générer un nombre premier p et un générateur g (public)
    p = generate_prime(32)
    g = random.randint(1, p - 1)
    # Alice choisit secrètement un nombre aléatoire a
    a = random.randint(1, p - 1)
    #Bob choisit secrètement un nombre aléatoire b
    b = random.randint(1, p - 1)
    # Calculer la valeur secrète pour Alice
    A = compute_secret_value(p, g, a)
    # Calculer la valeur secrète pour Bob
    B = compute_secret_value(p, g, b)
    # Calculer le secret partagé pour Alice
    secret_alice = compute_shared_secret(p, B, a)
    # Calculer le secret partagé pour Bob
    secret_bob = compute_shared_secret(p, A, b)
    # Vérifier si les secrets partagés sont identiques
    print(secret_alice)
    print(secret_alice == secret_bob)

# Tester la simulation Diffie-Hellman
if __name__ == '__main__':
    simulate_diffie_hellman()
