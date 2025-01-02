import random
from multiprocessing import Pool 
import time
from bitarray import bitarray

from cobra.roundKeys import key_scheduling
from cobra.s_boxes import sboxes_cobra, apply_sbox, inverse_sboxes_cobra
from mathFunctions import inv_mod
from hash import sponge_hash

# Variable qui définit le nombre de tours de COBRA
NB_ROUNDS = 12

# Génération aléatoire de la clé de 128 bits
def generate_key_128():
    key = bitarray()
    key.frombytes(random.getrandbits(128).to_bytes(16, byteorder='big'))
    return key


# Ajout de la clé de tour : XOR entre le bloc et la clé
def add_round_key(bloc, key):
    return bloc ^ key

# Fonctions nécessaires pour la parallélisation des S-boxes
def apply_first_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[0])
def apply_second_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[1])
def apply_third_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[2])
def apply_fourth_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[3])

# Fonctions nécessaires pour la parallélisation des S-boxes inversées
def inverse_first_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[0])
def inverse_second_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[1])
def inverse_third_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[2])
def inverse_fourth_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[3])

# Substitution : On applique 32 fois (en parallèle) la même S-box à chaque bloc de 4 bits du bloc
def substitution(bloc, i):
    # Séparer le bloc en 32 blocs de 4 bits
    blocs = [bloc[i:i+4] for i in range(0, 128, 4)]
    # Utiliser multiprocessing pour appliquer la S-box en parallèle
    # Modifier la S-box appliquée en fonction du numéro de tour
    with Pool() as p:
        if i // 8 == 0:
            blocs = p.map(apply_first_sbox, blocs)
        elif i // 8 == 1:
            blocs = p.map(apply_second_sbox, blocs)
        elif i // 8 == 2:
            blocs = p.map(apply_third_sbox, blocs)
        elif i // 8 == 3:
            blocs = p.map(apply_fourth_sbox, blocs)
        else :
            raise ValueError("Invalid round number.")
    # Réassembler le bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    # Retourner le bloc
    return bloc

# Substitution inversée : On applique la S-box inversée à chaque bloc de 4 bits du bloc
def inverse_substitution(bloc, i):
    # Séparer le bloc en 32 blocs de 4 bits
    blocs = [bloc[i:i+4] for i in range(0, 128, 4)]
    # Utiliser multiprocessing pour appliquer la S-box en parallèle
    # Modifier la S-box appliquée en fonction du numéro de tour
    with Pool() as p:
        if i // 8 == 0:
            blocs = p.map(inverse_first_sbox, blocs)
        elif i // 8 == 1:
            blocs = p.map(inverse_second_sbox, blocs)
        elif i // 8 == 2:
            blocs = p.map(inverse_third_sbox, blocs)
        elif i // 8 == 3:
            blocs = p.map(inverse_fourth_sbox, blocs)
        else :
            raise ValueError("Invalid round number.")
    # Réassembler le bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    # Retourner le bloc
    return bloc

# Appliquer la fonction de Feistel : f(x) = ((x+1)^-1mod257)-1
def apply_feistel_function(right_bloc, key, feistel_table):
    # Le bloc de droite est divisé en 8 blocs de 8 bits
    sub_blocs = [right_bloc[i:i+8] for i in range(0, 64, 8)]
    # Inverser les bits de chaque bloc
    sub_blocs = [b[::-1] for b in sub_blocs]
    # Appliquer la fonction de Feistel à chaque bloc
    z_blocs = [feistel_table[int(b.to01(), 2)] for b in sub_blocs]
    # Réassembler les blocs
    z_bloc = bitarray()
    for z in z_blocs:
        z_bloc.extend(z)
    # Appliquer une permutation P au bloc
    z_bloc = permutation_P(z_bloc)
    # Diviser à nouveau le bloc en 8 blocs de 8 bits
    z_blocs = [z_bloc[i:i+8] for i in range(0, 64, 8)]
    # Générer des nombres pseudo-aléatoires à partir des blocs z
    prng_bloc = generate_pseudo_random_numbers(z_blocs)
    # Dériver la clé en utilisant l'algorithme KDF
    derivated_key_tmp = sponge_hash(key.to01(), 8)
    # Convertir en bitarray
    derivated_key = bitarray()
    derivated_key.frombytes(derivated_key_tmp)
    # XOR le nombre pseudo-aléatoire avec la clé dérivée
    output = prng_bloc ^ derivated_key
    return output

# Permutation P : On applique une permutation sur le bloc de 64 bits
def permutation_P(bloc):
    # define permutation vector (TODO)
    P = [63, 31, 62, 30, 61, 29, 60, 28, 59, 27, 58, 26, 57, 25, 56, 24, 55, 23, 54, 22, 53, 21, 52, 20, 51, 19, 50, 18, 49, 17, 48, 16, 47, 15, 46, 14, 45, 13, 44, 12, 43, 11, 42, 10, 41, 9, 40, 8, 39, 7, 38, 6, 37, 5, 36, 4, 35, 3, 34, 2, 33, 1, 32, 0]
    # Appliquer la permutation si le bloc est bien de 64 bits (sinon, soulever une erreur)
    if len(bloc) == 64:
        bloc = bitarray([bloc[i] for i in P])
    else:
        raise ValueError("Bloc must be of 64 bits.")
    return bloc

# Générer des nombres pseudo-aléatoires à partir des blocs z
def generate_pseudo_random_numbers(z_blocs):
    # Initialiser la liste des nombres pseudo-aléatoires à une liste vide
    prng_blocs = []
    for z_bloc in z_blocs:
        # Mettre la seed du générateur de nombres pseudo-aléatoires à la valeur du bloc z
        random.seed(int(z_bloc.to01(), 2))
        prng_bloc = bitarray()
        # Générer un nombre pseudo-aléatoire de 8 bits
        prng_bloc.frombytes(random.getrandbits(8).to_bytes(1, byteorder='big'))
        prng_blocs.append(prng_bloc)
    # On concatène les nombres pseudo-aléatoires pour obtenir un bloc de 64 bits
    prng_bloc = bitarray()
    for prng in prng_blocs:
        prng_bloc.extend(prng)
    return prng_bloc

# Calculer la fonction de feistel : f(x) = ((x + 1)^-1 mod 257)-1
def feistel_function(x):
    # Si x = 256, on retourne 0 (pour éviter la division par 0)
    if x == 256:
        return 0
    else:
        return inv_mod((x + 1) % 257, 257) - 1


# Tabulation de la fonction de Feistel : On calcule la fonction de Feistel pour chaque valeur de 0 à 255
def tabulation_function():
    table = [0] * 256
    for i in range(256):
        table[i] = bitarray(format(feistel_function(i), '08b'))
    return table

# Feistel de Réré : On applique 3 ou 4 tours du réseau de Feistel
def feistel_de_rere(bloc, feistel_table, key):
    # Séparer le bloc en 2 blocs de 64 bits
    left_bloc = bloc[:64]
    right_bloc = bloc[64:]
    # On fait 3 tours du réseau de Feistel (par soucis de performance)
    for _ in range(0, 3):
        # On sauvegarde le bloc de gauche
        tmp_left_bloc = left_bloc
        # On met le bloc de gauche à jour en lui donnant la valeur du bloc de droite
        left_bloc = right_bloc
        # On met le bloc de droite à jour en lui donnant la valeur du bloc de gauche XOR la fonction de Feistel appliquée au bloc de droite
        right_bloc = tmp_left_bloc ^ apply_feistel_function(right_bloc, key, feistel_table)
    # On réassemble le bloc
    bloc = bitarray()
    bloc.extend(left_bloc)
    bloc.extend(right_bloc)
    return bloc

# Déchiffrer la Feistel de Réré : On applique 3 ou 4 tours du réseau de feistel en sens inverse
def decipher_feistel_de_rere(bloc, feistel_table, key):
    # Séparer le bloc en 2 blocs de 64 bits
    left_bloc = bloc[:64]
    right_bloc = bloc[64:]
    # On applique 3 tours du réseau de Feistel en sens inverse (comme on en applique 3 dans la fonction de Feistel)
    for _ in range(0, 3):
        # On sauvegarde le bloc de droite
        tmp_right_bloc = right_bloc
        # On met le bloc de droite à jour en lui donnant la valeur du bloc de gauche
        right_bloc = left_bloc
        # On met le bloc de gauche à jour en lui donnant la valeur du bloc de droite XOR la fonction de Feistel appliquée au bloc de gauche
        left_bloc = tmp_right_bloc ^ apply_feistel_function(left_bloc, key, feistel_table)
    # On réassemble le bloc
    bloc = bitarray()
    bloc.extend(left_bloc)
    bloc.extend(right_bloc)
    return bloc

# Transformation linéaire : On réalise des opérations binaires sur 4 blocs de 32 bits
def linear_transformation(bloc):
    # Séparer les blocs en 4 blocs de 32 bits
    blocs = [bloc[i:i+32] for i in range(0, 128, 32)]
    # Décalage circulaire à gauche de 13 bits pour le bloc 0
    blocs[0] = blocs[0][13:] + blocs[0][:13]
    # Décalage circulaire à gauche de 3 bits pour le bloc 2
    blocs[2] = blocs[2][3:] + blocs[2][:3]
    # XOR entre le bloc 0, 1 et 2 sauvegardé dans le bloc 1
    blocs[1] = blocs[0] ^ blocs[1] ^ blocs[2]
    # XOR entre le bloc 2, 3 et 0 (avec un décalage circulaire à gauche de 3 bits) sauvegardé dans le bloc 3
    blocs[3] = blocs[2] ^ blocs[3] ^ (blocs[0][3:] + blocs[0][:3])
    # Décalage circulaire à gauche de 1 bit pour le bloc 1
    blocs[1] = blocs[1][1:] + blocs[1][:1]
    # Décalage circulaire à gauche de 7 bits pour le bloc 3
    blocs[3] = blocs[3][7:] + blocs[3][:7]
    # XOR entre le bloc 0, 1 et 3 sauvegardé dans le bloc 0
    blocs[0] = blocs[1] ^ blocs[0] ^ blocs[3]
    # XOR entre le bloc 3, 2 et 1 (avec un décalage circulaire à gauche de 7 bits) sauvegardé dans le bloc 2
    blocs[2] = blocs[3] ^ blocs[2] ^ (blocs[1][7:] + blocs[1][:7])
    # Décalage circulaire à gauche de 5 bits pour le bloc 0
    blocs[0] = blocs[0][5:] + blocs[0][:5]
    # Décalage circulaire à gauche de 22 bits pour le bloc 2
    blocs[2] = blocs[2][22:] + blocs[2][:22]
    # On réassemble le bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

# Transformation linéaire inverse : On réalise des opérations binaires sur 4 blocs de 32 bits
def inverse_linear_transformation(bloc):
    # Séparer les blocs en 4 blocs de 32 bits
    blocs = [bloc[i:i+32] for i in range(0, 128, 32)]
    # Décalage circulaire à droite de 22 bits pour le bloc 2
    blocs[2] = blocs[2][-22:] + blocs[2][:-22]
    # Décage circulaire à droite de 5 bits pour le bloc 0
    blocs[0] = blocs[0][-5:] + blocs[0][:-5]
    # XOR entre le bloc 3, 2 et 1 (avec un décalage circulaire à droite de 7 bits) sauvegardé dans le bloc 2
    blocs[2] = blocs[3] ^ blocs[2] ^ (blocs[1][7:] + blocs[1][:7])
    # XOR entre le bloc 0, 1 et 3 sauvegardé dans le bloc 0
    blocs[0] = blocs[0] ^ blocs[1] ^ blocs[3]
    # Décalage circulaire à droite de 7 bits pour le bloc 3
    blocs[3] = blocs[3][-7:] + blocs[3][:-7]
    # Décalage circulaire à droite de 1 bit pour le bloc 1
    blocs[1] = blocs[1][-1:] + blocs[1][:-1]
    # XOR entre le bloc 2, 3 et 0 (avec un décalage circulaire à droite de 3 bits) sauvegardé dans le bloc 3
    blocs[3] = blocs[2] ^ blocs[3] ^ (blocs[0][3:] + blocs[0][:3])
    # XOR entre le bloc 0, 1 et 2 sauvegardé dans le bloc 1
    blocs[1] = blocs[0] ^ blocs[1] ^ blocs[2]
    # Décalage circulaire à droite de 3 bits pour le bloc 2
    blocs[2] = blocs[2][-3:] + blocs[2][:-3]
    # Décalage circulaire à droite de 13 bits pour le bloc 0
    blocs[0] = blocs[0][-13:] + blocs[0][:-13]
    # On réassemble le bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

# Permutation initiale : On applique une permutation sur le bloc de 128 bits
def initial_permutation(bloc, key):
    # On met le seed du générateur de nombres pseudo-aléatoires à la valeur de la clé du tour
    random.seed(int(key.to01(), 2))
    # On génère un vecteur de permutation de 128 bits (valeurs de 0 à 127)
    p_vector = list(range(128))
    # On génère pseudo-aléatoirement les valeurs du vecteur de permutation
    random.shuffle(p_vector)
    # On applique la permutation
    bloc = bitarray([bloc[i] for i in p_vector])
    return bloc

# Permutation initiale inverse : On applique une permutation sur le bloc de 128 bits
def reverse_initial_permutation(bloc, key):
    # On met le seed du générateur de nombres pseudo-aléatoires à la valeur de la clé du tour
    random.seed(int(key.to01(), 2))
    # On génère un vecteur de permutation de 128 bits (valeurs de 0 à 127)
    p_vector = list(range(128))
    # On génère pseudo-aléatoirement les valeurs du vecteur de permutation
    random.shuffle(p_vector)
    # On applique la permutation
    bloc = bitarray([bloc[p_vector.index(i)] for i in range(128)])
    return bloc

# Permutation finale : On applique une permutation sur le bloc de 128 bits
def final_permutation(bloc, key):
    # On met le seed du générateur de nombres pseudo-aléatoires à la valeur de la clé du tour
    random.seed(int(key.to01(), 2))
    # On génère un vecteur de permutation de 128 bits (valeurs de 0 à 127)
    p_vector = list(range(128))
    # On génère pseudo-aléatoirement les valeurs du vecteur de permutation
    random.shuffle(p_vector)
    # On applique la permutation
    bloc = bitarray([bloc[i] for i in p_vector])
    return bloc

# Permutation finale inverse : On applique une permutation sur le bloc de 128 bits
def reverse_final_permutation(bloc, key):
    # On met le seed du générateur de nombres pseudo-aléatoires à la valeur de la clé du tour
    random.seed(int(key.to01(), 2))
    # On génère un vecteur de permutation de 128 bits (valeurs de 0 à 127)
    p_vector = list(range(128))
    # On génère pseudo-aléatoirement les valeurs du vecteur de permutation
    random.shuffle(p_vector)
    # On applique la permutation
    bloc = bitarray([bloc[p_vector.index(i)] for i in range(128)])
    return bloc


# Encodage : On encode un bloc de données en utilisant l'algorithme COBRA
def encode_bloc(data, key):
    # On s'assure que les données représentent un bloc de 128 bits
    if len(data) != 128:
        raise ValueError("Data must be of 128 bits.")
    # On tabule la fonction de Feistel
    feistel_table = tabulation_function()
    # On génère les 33 clés
    keys = key_scheduling(key)
    # Permutation initiale
    data = initial_permutation(data, keys[0])
    # On applique les X tours (définis par NB_ROUNDS) de COBRA
    for i in range(0, NB_ROUNDS):
        # XOR avec la clé du tour
        bloc = add_round_key(data, keys[i])
        # On applique la substitution
        bloc = substitution(bloc, i)
        # On applique la fonction de Feistel
        bloc = feistel_de_rere(bloc, feistel_table, keys[i])
        # On applique la transformation linéaire
        bloc = linear_transformation(bloc)
    # Permutation finale
    data = final_permutation(data, keys[31])
    # XOR avec la dernière clé
    data = add_round_key(data, keys[32])
    return data

# Decodage : On décode un bloc de données en utilisant l'algorithme COBRA
def decode_bloc(data, key):
    # On s'assure que les données représentent un bloc de 128 bits
    if len(data) != 128:
        raise ValueError("Data must be of 128 bits.")
    # On tabule la fonction de Feistel
    feistel_table = tabulation_function()
    # On génère les 33 clés
    keys = key_scheduling(key)
    # On fait un XOR avec la dernière clé
    data = add_round_key(data, keys[32])
    # On inverse la permutation finale
    data = reverse_final_permutation(data, keys[31])
    # On applique les X tours (définis par NB_ROUNDS) de COBRA en sens inverse
    for i in range(NB_ROUNDS, 0, -1):
        # On inverse la transformation linéaire
        bloc = inverse_linear_transformation(data)
        # On applique la fonction de Feistel en sens inverse
        bloc = decipher_feistel_de_rere(bloc, feistel_table, keys[i])
        # On inverse la substitution
        bloc = inverse_substitution(bloc, i)
        # On fait un XOR avec la clé du tour
        bloc = add_round_key(data, keys[i])
    # On inverse la permutation initiale
    data = reverse_initial_permutation(data, keys[0])
    return data


# Convertir du texte en blocs de 128 bits
def convert_text_to_blocs_128(text):
    # Convrtir le texte en binaire en utilisant une structure bitarray
    data = bitarray()
    data.frombytes(text.encode('utf-8'))
    # Séparer les données en blocs de 128 bits
    data = [data[i:i+128] for i in range(0, len(data), 128)]
    # Ajouter des 0 pour compléter le dernier bloc si nécessaire
    if len(data[-1]) < 128:
        data[-1].extend('0' * (128 - len(data[-1])))
    return data

# Convertir des blocs de 128 bits en texte
def convert_blocs_128_to_text(data):
    # Regrouper tous les blocs en un seul bloc
    text = bitarray()
    for bloc in data:
        text.extend(bloc)
    # Convertir le bloc binaire en texte
    text = text.tobytes().decode('utf-8')
    # Supprimer les caractères nuls \x00 ajoutés pour compléter le dernier bloc
    text = text.replace('\x00', '')
    return text

# Encoder un texte en utilisant l'algorithme COBRA
def encode_text(text, key):
    # Convertir le texte en blocs de 128 bits
    data = convert_text_to_blocs_128(text)
    # Initialiser une liste pour stocker les données encodées
    encoded_data = []
    # Encoder chaque bloc de données
    for bloc in data:
        encoded_data.append(encode_bloc(bloc, key))
    # Convertir les données encodées en hexadécimal
    encoded_data = [b.tobytes().hex() for b in encoded_data]
    # Regrouper les données encodées en une seule chaîne de caractères
    encoded_data = ''.join(encoded_data)
    return encoded_data

# Déchiffrer un texte en utilisant l'algorithme COBRA (entrée : chaîne de caractères encodée en hexadécimal)
def decode_text(data, key):
    # Convertir les données hexadécimales en binaire
    bin_data = bitarray()
    bin_data.frombytes(bytes.fromhex(data))
    # Séparer les données en blocs de 128 bits
    bin_data = [bin_data[i:i+128] for i in range(0, len(bin_data), 128)]
    # Initialiser une liste pour stocker les données décodées
    decoded_data = []
    # Décoder chaque bloc de données
    for bloc in bin_data:
        decoded_data.append(decode_bloc(bloc, key))
    # Convertir les données décodées en texte avant de les retourner
    return convert_blocs_128_to_text(decoded_data)

# Fonction de test
if __name__ == "__main__":
    key = generate_key_128()
    time1 = time.time()
    test = encode_text("crypto is awesome", key)
    print("Time to encode : ", time.time() - time1)
    time1 = time.time()
    print("Encoded data : ", test)
    decoded_data = decode_text(test, key)
    print("Time to decode : ", time.time() - time1)
    print("Decoded data : ", decoded_data)    



# TODO : définition du dernier tour
# TODO : inverser substitution
# TODO : inverser add_round_key
# TODO : écrire fonction de décodage