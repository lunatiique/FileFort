from hash import merkle_damgard_hash
from bitarray import bitarray

# Fonction pour normaliser la clé
# Elle prend une clé sous forme de bitarray en entrée et retourne un bitarray de longueur 256
def normalize_key(key):
    # Convertir la clé en bitarray
    key_bits = bitarray()
    key_bits.frombytes(key)
    
    # Si la clé est plus longue que la taille du bloc de hachage, la hacher
    if len(key_bits) > 256:
        key_bits = bitarray()
        key_bits.frombytes(merkle_damgard_hash(key_bits.tobytes()))
    # Si la clé est plus courte que la taille du bloc de hachage, la compléter
    elif len(key_bits) < 256:
        key_bits.extend(bitarray('0' * (256 - len(key_bits))))
    
    return key_bits

# Fonction pour créer des clés dérivées à partir de la clé normalisée
# Elle prend une clé normalisée en entrée et retourne deux clés dérivées
# L'entrée et les sorties sont des bitarrays
def create_derived_keys(normalized_key):
    # Constantes de remplissage fixes de 64 octets pour ipad et opad
    ipad = bitarray()
    ipad.frombytes((0x36).to_bytes(1, byteorder='big') * 32)
    opad = bitarray()
    opad.frombytes((0x5C).to_bytes(1, byteorder='big') * 32)
    # Appliquer XOR élément par élément en utilisant bitarray
    k_i = normalized_key ^ ipad
    k_o = normalized_key ^ opad
    
    return k_i, k_o

# Fonction HMAC : prend une clé et un message en entrée et retourne la valeur HMAC
# La clé doit être un bitarray, le message doit être un objet bytes
# Elle retourne la valeur HMAC sous forme de chaîne hexadécimale
def hmac(key, message):
    # Normaliser la clé
    normalized_key = normalize_key(key)
    # Créer des clés dérivées
    k_i, k_o = create_derived_keys(normalized_key)
    # Convertir le message en bitarray
    message_bits = bitarray()
    message_bits.frombytes(message)
    # Calculer le hachage interne : hash(k_i + message)
    inner_hash = merkle_damgard_hash((k_i + message_bits).tobytes())
    # Convertir inner_hash en bitarray
    inner_hash_bits = bitarray()
    inner_hash_bits.frombytes(inner_hash.encode())
    # Calculer le hachage externe : hash(k_o + inner_hash)
    outer_hash = merkle_damgard_hash((k_o + inner_hash_bits).tobytes())
    # Retourner le hachage externe comme valeur HMAC
    return outer_hash

if __name__ == "__main__":
    # Tester la fonction hmac
    key = bitarray('01100101101100101011110000010101101111101110111000111000110101001011000010101101100101100110010110101001110111101100101000101011')
    message = b"The quick brown fox jumps over the lazy dog"
    hmac_value = hmac(key, message)
    print("Valeur HMAC :", hmac_value)