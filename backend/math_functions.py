#euclide algorithm to find the gcd of two numbers
import random

#compute the gcd of two numbers a and b
def pgcd(a,b):
    if b==0:
        return a
    else:
        return pgcd(b,a%b)
    
#find coprime number to a
def coprime(a):
    b=random.randint(1,a-1)
    while pgcd(a,b)!=1:
        b=random.randint(1,a-1)
    return b

#extended euclide algorithm to find coefficients of Bezout's identity
def bezout(a,b):
    if b==0:
        return (1,0)
    else:
        u,v=bezout(b,a%b)
        return (v,u-(a//b)*v)
    

#extended euclide algorithm to find the inverse of a modulo b
def inv_mod(a,b):
    u,v=bezout(a,b)
    if pgcd(a,b)==1:
        return u%b
    else:
        return "no inverse"

#eratosthenes algorithm to check if a number is prime
def eratosthenes(a):
    if a<=1:
        return False
    for i in range(2,int(a**0.5)+1):
        if a%i==0:
            return False
    return True

#decompose an integer a into prime factors
def decompose(a):
    result=[]
    for i in range(2,a+1):
        if eratosthenes(i):
            while a%i==0:
                a//=i
                result.append(i)
        if a==1:
            break
    return result

# calculate φ(a) using the prime factor decomposition of a
def phi(a):
    result=a
    for i in decompose(a):
        result*=(i-1)/i
    return int(result)

#fast exponentiation algorithm to compute a^n modulo m
def exp(a,n, m):
    if n==0:
        return 1
    if n%2==0:
        return exp(a**2,n//2, m) % m
    else:
        return a*exp(a,n-1, m) % m

#fast exponentiation algorithm to find the inverse of a modulo b using euler's theorem
def inv_mod_with_euler(a,b):
    if pgcd(a,b)!=1:
        return "no inverse"
    return exp(a,phi(b)-1,b)

#fast exponentiation algorithm to find the inverse of a modulo b using fermat's theorem
def inv_mod_with_fermat(a,b):
    #check if b is prime
    if not fermat(b):
        return "no inverse"
    return exp(a,b-2,b)

#chinese remainder theorem to find the solution of a system of congruences
#congruences is a list of tuples (a,mod) where a is the remainder and mod the modulus. ex : [(1,2),(2,3),(3,5)] means x=1 mod 2, x=2 mod 3 and x=3 mod 5
def crt(congruences):
    N=1
    for _, mod in congruences:
        N*=mod
    result=0
    for a,mod in congruences:
        N_i=N//mod
        result+=a*N_i*inv_mod_with_fermat(N_i,mod)
    return result%N

#fermat primality test to check if a number is prime
def fermat(a):
    if a<=1:
        return False
    for i in range(2,a):
        if exp(i,a-1, a)!=1:
            return False
    return True

#miller-rabin primality test to check if a number is prime with a certain probability
def miller_rabin(a,k):
    if a<=1:
        return False
    if a==2:
        return True
    if a%2==0:
        return False
    d=a-1
    r=0
    while d%2==0:
        d//=2
        r+=1
    for _ in range(k):
        x=exp(2,d,a)
        if x==1 or x==a-1:
            continue
        for _ in range(r-1):
            x=(x**2)%a
            if x==1:
                return False
            if x==a-1:
                break
        if x!=a-1:
            return False
    return True

#generate an odd pseudo-random number between 2^n-1 and (2^n)-1 to obtain a random number of exactly n bits
def pseudo_random_odd_of_n_bits(n):
    rand = random.randint(2**(n-1),2**n-1)
    if rand%2==0:
        rand+=1
    return rand

#generate a pseudo-random odd number between 0 a 2^n-1
def pseudo_random_odd(n):
    rand = random.randint(0,2**n-1)
    if rand%2==0:
        rand+=1
    return rand

# Small prime numbers for trial division
small_primes = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113, 127, 131, 137, 139, 149,
    151, 157, 163, 167, 173, 179, 181, 191, 193, 197, 199, 211, 223, 227, 229,
    233, 239, 241, 251, 257, 263, 269, 271, 277, 281, 283, 293, 307, 311, 313,
    317, 331, 337, 347, 349, 353, 359, 367, 373, 379, 383, 389, 397, 401, 409,
    419, 421, 431, 433, 439, 443, 449, 457, 461, 463, 467, 479, 487, 491, 499,
    503, 509, 521, 523, 541
]

# Fixed witnesses for Miller-Rabin on 1024-bit numbers
miller_rabin_witnesses = [ 2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67,
    71, 73, 79, 83, 89, 97, 101, 103, 107, 109, 113]

# Check if n is divisible by small primes
def is_prime_small_divisors(n):
    if n < 2:
        return False
    for p in small_primes:
        if n % p == 0 and n != p:
            return False
    return True

# Perform the Miller-Rabin test with fixed witnesses to optimize for 1024-bit numbers
def miller_rabin_optimized(n, witnesses):
    """Perform the Miller-Rabin test with fixed witnesses."""
    if n < 2:
        return False
    if n in small_primes:
        return True
    # Write n-1 as d * 2^r
    d = n - 1
    r = 0
    while d % 2 == 0:
        d //= 2
        r += 1
    # Test against each witness
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

# Combined primality test using small divisors and Miller-Rabin for a more efficient check
def is_prime(n):
    """Combined primality test using small divisors and Miller-Rabin."""
    # Check for small divisors
    if not is_prime_small_divisors(n):
        return False
    # Perform Miller-Rabin with fixed witnesses
    return miller_rabin_optimized(n, miller_rabin_witnesses)