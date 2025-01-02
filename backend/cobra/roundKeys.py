from bitarray import bitarray
from cobra.s_boxes import sboxes_cobra, apply_sbox

# Définir la constante phi en binaire
binary_phi = 0b10110111011010111011010111011011

# Génération des clés de tour : on génère 132 clés de 32 bits à partir d'une clé de 128, 192 ou 256 bits
def key_scheduling(key):
    # Vérifier que la clé est de 128, 192 ou 256 bits
    if len(key) != 128 and len(key) != 192 and len(key) != 256:
        raise ValueError("The key must be 128, 192 or 256 bits long.")
    # Si la clé contient moins de 256 bits, on la complète avec des 0
    if len(key) < 256:
        key.extend(bitarray('0' * (256 - len(key))))
    # Diviser la clé en 8 blocs de 32 bits et générer 132 clés de 32 bits
    w = key_expansion(key)
    # On applique les S-boxes aux clés
    blocs = apply_sbox_to_keys(w)
    # On assemble les 132 clés en 33 clés de tour de 128 bits
    round_keys = assemble_keys(blocs)
    return round_keys



# Expansion de clé : on génère 132 clés de 32 bits à partir d'une clé de 256 bits
def key_expansion(key):
    # On divise la clé en 8 blocs de 32 bits
    w = [key[i:i+32] for i in range(0, 256, 32)]
    # On génère les 124 clés supplémentaires
    for i in range(8, 132):
        # On appliquer un XOR aux 4 clés précédentes, à la représentation binaire de phi et au numéro d'itération
        new_key = w[i-8] ^ w[i-5] ^ w[i-3] ^ w[i-1] ^ bitarray(bin(binary_phi)[2:]) ^ bitarray(bin(i)[2:].zfill(32))
        # On décale la clé de 11 bits vers la gauche
        new_key = new_key << 11
        # On ajoute la nouvelle clé à la liste
        w.append(new_key[:32])
    return w



# Application des S-boxes à un bloc de 32 bits
def apply_sbox_to_bloc(bloc):
    # S'assurer que le bloc est un bitarray de 32 bits
    if len(bloc) != 32:
        raise ValueError("Bloc must be a 32-bit bitarray.")
    
    # Séparer le bloc de 32 bits en 8 sous-blocs de 4 bits
    sub_blocs = [bloc[i:i+4] for i in range(0, 32, 4)]
    
    # Appliquer les S-boxes à chaque sous-bloc et concaténer les résultats
    output_bloc = bitarray()
    for i, sub_bloc in enumerate(sub_blocs):
        output_bloc.extend(apply_sbox(sub_bloc, sboxes_cobra[i]))

    return output_bloc

# Application des S-boxes aux clés
def apply_sbox_to_keys(keys):
    # S'assurer que les clés sont des bitarrays de 32 bits
    if not all(len(key) == 32 for key in keys):
        raise ValueError("Keys must be 32-bit bitarrays.")
    
    # Appliquer les S-boxes à chaque clé
    output_keys = [apply_sbox_to_bloc(key) for key in keys]
    
    return output_keys

# Assemblage des clés de tour
def assemble_keys(keys):
    # S'assurer que les clés sont des bitarrays de 32 bits
    if not all(len(key) == 32 for key in keys):
        raise ValueError("Keys must be 32-bit bitarrays.")
    
    # Assemler les 132 clés en 33 clés de tour de 128 bits
    round_keys = []
    for i in range(0, 132, 4):
        # Concaténer 4 clés pour former une clé de tour
        round_key = bitarray()
        for j in range(4):
            round_key.extend(keys[i+j])
        round_keys.append(round_key)
    
    return round_keys