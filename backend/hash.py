import struct
from bitarray import bitarray

# 1. Ci-dessous, une implémentation simple d'une fonction de hachage de type Merkle-Damgård avec une compression de Davies-Meyer.

# Fonction de padding : prend un message et une taille de bloc en entrée et renvoie un message avec une taille fixe
# Le message est complété pour atteindre un multiple de block_size octets, avec un bit 1, suivi de 0, et la longueur du message en bits.	
def pad_message(message, block_size):
    message = message.encode('utf-8') if isinstance(message, str) else message
    message_length = len(message) * 8  # Longueur du message en bits
    
    # Créer un bitarray à partir du message
    bits = bitarray()
    bits.frombytes(message)
    
    # Ajouter un bit 1
    bits.append(1)
    
    # Ajouter des bits 0 jusqu'à ce que la longueur soit un multiple de block_size octets
    while (len(bits) + 64) % (block_size * 8) != 0:
        bits.append(0)
    
    # Ajouter la longueur en tant qu'entier 64 bits en big-endian
    length_bits = bitarray(endian='big')
    length_bits.frombytes(struct.pack('>Q', message_length))
    bits.extend(length_bits)
    
    return bits.tobytes()

# Fonction pour ajuster la taille du bloc : prend un bloc et une taille cible en entrée et renvoie des blocs de taille cible
def adjust_block_size(block, target_size=16):
    # Diviser le bloc en morceaux de taille cible, compléter le dernier si nécessaire
    blocks = [block[i:i + target_size] for i in range(0, len(block), target_size)]
    if len(blocks[-1]) < target_size:
        blocks[-1] = blocks[-1].ljust(target_size, b'\x00')  # Remplir avec des octets nuls si nécessaire
    return blocks

# Fonction de compression de Davies-Meyer : prend un état et un bloc en entrée et renvoie un nouvel état
# Le bloc est divisé en quatre mots de 32 bits, et une série d'opérations est effectuée sur l'état et le bloc.
def davies_meyer_compression(state, block, block_size=16):

    # Diviser le bloc en quatre mots de 32 bits
    block_words = struct.unpack('>IIII', block[:block_size])
    
    # Génération de clés de tour à partir des mots de bloc xorés avec des constantes (valeurs choisies arbitrairement)
    round_keys = [
        block_words[0] ^ 0x12345678,
        block_words[1] ^ 0x9ABCDEF0,
        block_words[2] ^ 0x0FEDCBA9,
        block_words[3] ^ 0x87654321,
        block_words[0] ^ 0xAA44B923,
        block_words[1] ^ 0xEEAAFF99,
        block_words[2] ^ 0x349718AD,
        block_words[3] ^ 0x2498ABEF,
        block_words[0] ^ 0x98274291,
        block_words[1] ^ 0xADBEF342,
        block_words[2] ^ 0xCCDA8934,
        block_words[3] ^ 0xBBAEF342,
        block_words[0] ^ 0xFF000012,
        block_words[1] ^ 0x55555555,
        block_words[2] ^ 0xBBEFFA34,
        block_words[3] ^ 0xFECA1302
    ]
    
    # Initialiser l'état local avec l'état actuel
    local_state = state[:]
    
    # Réaliser 16 tours de mélange (nombre bas pour la simplicité)
    for round_num in range(16):
        # Opérations arbitraires mélangeant l'état et les clés de tour (addition, multiplication, XOR, rotation)
        new_state = [
            (local_state[0] + round_keys[round_num] + (local_state[1] << 7)) & 0xFFFFFFFF,
            (local_state[1] ^ ((local_state[0] >> 5) | (local_state[2] << 27))) & 0xFFFFFFFF,
            (local_state[2] * round_keys[round_num] + local_state[3]) & 0xFFFFFFFF,
            (local_state[3] ^ (local_state[2] + (round_keys[round_num] >> 3))) & 0xFFFFFFFF
        ]
        
        # Encore plus d'options de mélange (rotation, XOR, addition)
        local_state = [
            (new_state[0] ^ ((new_state[3] << 11) | (new_state[3] >> 21))) & 0xFFFFFFFF,
            (new_state[1] + ((new_state[2] << 5) | (new_state[2] >> 27))) & 0xFFFFFFFF,
            (new_state[2] ^ ((new_state[0] >> 7) | (new_state[0] << 25))) & 0xFFFFFFFF,
            (new_state[3] + ((new_state[1] << 3) | (new_state[1] >> 29))) & 0xFFFFFFFF
        ]
    
    # XOR Final avec l'état actuel (construction Davies-Meyer)
    final_state = [
        (local_state[0] ^ state[0]) & 0xFFFFFFFF,
        (local_state[1] ^ state[1]) & 0xFFFFFFFF,
        (local_state[2] ^ state[2]) & 0xFFFFFFFF,
        (local_state[3] ^ state[3]) & 0xFFFFFFFF
    ]
    
    return final_state

# Fonction de hachage Merkle-Damgård : prend un message et une taille de bloc en entrée et renvoie la valeur de hachage.
# Optionnellement, un état initial peut être fourni (par défaut est [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321, 0x5364DBBA, 0x342BAD34, 0xA8824BEF, 0x99355FFE]).
# Le message est complété pour atteindre un multiple de block_size octets, et divisé en blocs.
# Chaque bloc est traité en utilisant la fonction de compression Davies-Meyer, avec deux états de 4 mots.
# L'état final est converti en une valeur de hachage de 16 octets.
# La sortie est une valeur de hachage hexadécimale de 256 bits.
def merkle_damgard_hash(message, block_size=16, initial_state=None):

    # Assurez-vous que l'état initial a 4 éléments (constantes arbitraires)
    if initial_state is None:
        initial_state = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321, 0x5364DBBA, 0x342BAD34, 0xA8824BEF, 0x99355FFE]
    
    # Diviser l'état initial en deux états de 4 mots
    state_a = initial_state[:4]
    state_b = initial_state[4:]
    
    # Compléter le message d'entrée
    padded_message = pad_message(message, block_size)
    
    # Traiter les blocs pour les deux états
    blocks = adjust_block_size(padded_message, 16)
    for block in blocks:
        state_a = davies_meyer_compression(state_a, block)
        state_b = davies_meyer_compression(state_b, block)
    
    # Combiner les états en un hachage de 32 octets
    final_hash = struct.pack('>IIIIIIII', *(state_a + state_b))
    return final_hash.hex()

# 2. Ci-dessous, une implémentation simple d'une fonction de hachage de type "sponge" avec une permutation basée sur des rotations.

# Fonction de remplissage : complète l'entrée à la taille de bloc spécifiée en utilisant le remplissage par des zéros.
def pad_to_block_size(data, block_size):
    """Complète l'entrée à la taille de bloc spécifiée en utilisant le remplissage par des zéros."""
    return data + b'\x00' * (block_size - (len(data) % block_size)) 

# Fonction de XOR octet par octet entre deux séquences d'octets.
def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))

# Une fonction de hachage "sponge" simple avec un système de tours basé sur des rotations.
# password : Mot de passe d'entrée à hacher
# output_size : Taille souhaitée de la sortie en octets
# state_size : Taille de l'état interne en octets
# rounds : Nombre de tours de rotation pour chaque absorption de bloc
def sponge_hash(password, output_size=32, state_size=200, rounds=1000):
    # Initialiser l'état avec des zéros
    state = bytearray(state_size)
    
    # Convertir le mot de passe en tableau d'octets
    password_bytes = password.encode('utf-8')
    block_size = 64  # Définir une taille de bloc pour l'absorption
    
    # Compléter le mot de passe pour correspondre à la taille de bloc
    padded_password = pad_to_block_size(password_bytes, block_size)
    
    # Phase d'absorption : Diviser le mot de passe en blocs et faire un XOR avec l'état
    for i in range(0, len(padded_password), block_size):
        block = padded_password[i:i+block_size]
        block = block.ljust(state_size, b'\x00')  # S'assurer que le bloc est de la même taille que l'état
        
        # XOR du bloc dans l'état
        state = bytearray(xor_bytes(state, block))  # Convertir de nouveau en bytearray après le XOR
        
        # Effectuer plusieurs tours de "rotation"
        for _ in range(rounds):
            # Permutation simple (mélange pseudo-aléatoire)
            state = sponge_permutation(state)

    # Phase de compression : Générer la sortie en permutant et en prenant des octets de sortie
    output = bytearray()
    while len(output) < output_size:
        state = sponge_permutation(state)
        output.extend(state[:output_size - len(output)])  # Ajouter des octets jusqu'à la taille de sortie

    return bytes(output)

# Fonction de permutation basique pour mélanger l'état.
def sponge_permutation(state):
    # Faire tourner chaque octet dans l'état et faire un XOR avec les octets voisins
    for i in range(len(state)):
        left = (i - 1) % len(state)
        right = (i + 1) % len(state)
        
        # Rotation simple et XOR pour introduire de la diffusion
        state[i] = (state[i] ^ ((state[left] << 1) | (state[left] >> 7)) ^ state[right]) & 0xFF

    # Effectuer des opérations supplémentaires au niveau des bits pour ajouter de la complexité
    for i in range(1, len(state), 2):
        state[i] ^= (state[i - 1] ^ (state[(i + 1) % len(state)] >> 3)) & 0xFF
    
    return state

# Pour tester les fonctions du fichier
if __name__ == "__main__":
    # Tester la fonction de hachage
    message = "Hello, world!"
    hash_value = merkle_damgard_hash(message, block_size=32)
    print("Valeur de hachage complexe :", hash_value)
