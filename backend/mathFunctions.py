import random

# Calculer le PGCD de deux nombres a et b
def pgcd(a, b):
    if b == 0:
        return a
    else:
        return pgcd(b, a % b)

# Trouver un nombre coprime à a
def coprime(a):
    b = random.randint(1, a - 1)
    while pgcd(a, b) != 1:
        b = random.randint(1, a - 1)
    return b

# Algorithme d'Euclide étendu pour trouver les coefficients de l'identité de Bézout
def bezout(a, b):
    if b == 0:
        return (1, 0)
    else:
        u, v = bezout(b, a % b)
        return (v, u - (a // b) * v)

x_eu, y_eu = 0, 1

# Algorithme d'Euclide étendu
def pgcd_extended(a, b):
    global x_eu, y_eu

    # Cas de base
    if a == 0:
        x_eu = 0
        y_eu = 1
        return b

    pgcd = pgcd_extended(b % a, a)
    x1 = x_eu
    y1 = y_eu

    x_eu = y1 - (b // a) * x1
    y_eu = x1

    return pgcd

# Algorithme d'Euclide étendu pour trouver l'inverse de a modulo b
def inv_mod(a, b):
    g = pgcd_extended(a, b)
    if g != 1:
        return "Pas d'inverse"
    else:
        res = (x_eu % b + b) % b
        return res

# Algorithme d'Ératosthène pour vérifier si un nombre est premier
def eratosthenes(a):
    if a <= 1:
        return False
    for i in range(2, int(a ** 0.5) + 1):
        if a % i == 0:
            return False
    return True

# Décomposer un entier a en facteurs premiers
def decompose(a):
    result = []
    for i in range(2, a + 1):
        if eratosthenes(i):
            while a % i == 0:
                a //= i
                result.append(i)
        if a == 1:
            break
    return result

# Calculer φ(a) en utilisant la décomposition en facteurs premiers de a
def phi(a):
    result = a
    for i in decompose(a):
        result *= (i - 1) / i
    return int(result)

# Algorithme d'exponentiation rapide pour calculer a^n modulo m
def exp(a, n, m):
    if n == 0:
        return 1
    if n % 2 == 0:
        return exp(a ** 2, n // 2, m) % m
    else:
        return a * exp(a, n - 1, m) % m

# Algorithme d'exponentiation rapide pour trouver l'inverse de a modulo b en utilisant le théorème d'Euler
def inv_mod_with_euler(a, b):
    if pgcd(a, b) != 1:
        return "Pas d'inverse"
    return exp(a, phi(b) - 1, b)

# Algorithme d'exponentiation rapide pour trouver l'inverse de a modulo b en utilisant le théorème de Fermat
def inv_mod_with_fermat(a, b):
    # Vérifier si b est premier
    if not fermat(b):
        return "Pas d'inverse"
    return exp(a, b - 2, b)

# Théorème des restes chinois pour trouver la solution d'un système de congruences
# congruences est une liste de tuples (a, mod) où a est le reste et mod le module. ex : [(1,2),(2,3),(3,5)] signifie x=1 mod 2, x=2 mod 3 et x=3 mod 5
def crt(congruences):
    N = 1
    for _, mod in congruences:
        N *= mod
    result = 0
    for a, mod in congruences:
        N_i = N // mod
        result += a * N_i * inv_mod_with_fermat(N_i, mod)
    return result % N

# Test de primalité de Fermat pour vérifier si un nombre est premier
def fermat(a):
    if a <= 1:
        return False
    for i in range(2, a):
        if exp(i, a - 1, a) != 1:
            return False
    return True

# Test de primalité de Miller-Rabin pour vérifier si un nombre est premier avec une certaine probabilité
def miller_rabin(a, k):
    if a <= 1:
        return False
    if a == 2:
        return True
    if a % 2 == 0:
        return False
    d = a - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(k):
        x = exp(2, d, a)
        if x == 1 or x == a - 1:
            continue
        for _ in range(r - 1):
            x = (x ** 2) % a
            if x == 1:
                return False
            if x == a - 1:
                break
        if x != a - 1:
            return False
    return True

# Générer un nombre pseudo-aléatoire impair entre 2^n-1 et (2^n)-1 pour obtenir un nombre aléatoire de exactement n bits
def pseudo_random_odd_of_n_bits(n):
    rand = random.randint(2 ** (n - 1), 2 ** n - 1)
    if rand % 2 == 0:
        rand += 1
    return rand

# Générer un nombre pseudo-aléatoire impair entre 0 et 2^n-1
def pseudo_random_odd(n):
    rand = random.randint(0, 2 ** n - 1)
    if rand % 2 == 0:
        rand += 1
    return rand

# Petits nombres premiers pour la division d'essai
small_primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
    317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
    503, 509, 521, 523, 541
]

# Témoins fixes pour Miller-Rabin sur des nombres de 1024 bits
miller_rabin_witnesses = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]

# Vérifier si n est divisible par de petits nombres premiers
def is_prime_small_divisors(n):
    if n < 2:
        return False
    for p in small_primes:
        if n % p == 0 and n != p:
            return False
    return True

# Effectuer le test de Miller-Rabin avec des témoins fixes pour optimiser les nombres de 1024 bits
def miller_rabin_optimized(n, witnesses):
    if n < 2:
        return False
    if n in small_primes:
        return True
    # Écrire n-1 comme d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    # Tester contre chaque témoin
    for a in witnesses:
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# Test de primalité combiné utilisant de petits diviseurs et Miller-Rabin pour une vérification plus efficace
def is_prime(n):
    # Vérifier les petits diviseurs
    if not is_prime_small_divisors(n):
        return False
    # Effectuer Miller-Rabin avec des témoins fixes
    return miller_rabin_optimized(n, miller_rabin_witnesses)

# Convertir un entier en octets, en gérant la longueur de manière appropriée
def int_to_bytes(n):
    return n.to_bytes((n.bit_length() + 7) // 8, byteorder='big')

# Convertir de octets en entier
def bytes_to_int(b):
    return int.from_bytes(b, byteorder='big')

# Générer un nombre premier aléatoire de la longueur spécifiée en bits
def generate_prime(length):
    while True:
        n = pseudo_random_odd_of_n_bits(length)
        if is_prime(n):
            return n

# Générer un nombre premier pseudo-aléatoire basé sur une graine dérivée d'un mot de passe
def generate_prime_from_seed(seed, length):
    random.seed(seed)  # Définir la graine pour la reproductibilité
    while True:
        # Générer un candidat aléatoire de la longueur spécifiée en bits
        candidate = random.getrandbits(length)
        candidate |= (1 << length - 1) | 1  # S'assurer qu'il est impair et a la bonne longueur en bits
        if is_prime(candidate):  # Effectuer le test de primalité
            return candidate
        