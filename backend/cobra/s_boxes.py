import numpy as np
import random
from bitarray import bitarray

# Variables contenants les S-boxes de SERPENT
sbox_0 = [
    [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
    [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
    [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
    [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13]
]

sbox_1 = [
    [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
    [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
    [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
    [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9]
]

sbox_2 = [
    [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
    [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
    [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
    [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12]
]

sbox_3 = [
    [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
    [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
    [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
    [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14]
]

sbox_4 = [
    [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
    [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
    [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
    [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3]
]

sbox_5 = [
    [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
    [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
    [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
    [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13]
]


sbox_6 = [
    [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
    [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
    [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
    [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12]
]


sbox_7 = [
    [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
    [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
    [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
    [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11]
]

# Liste contenant les S-boxes de SERPENT
sboxes_des = [sbox_0, sbox_1, sbox_2, sbox_3, sbox_4, sbox_5, sbox_6, sbox_7]

# Liste des S-boxes pour COBRA (définies grâce au code ci-dessous)
sboxes_cobra = [
    [[12, 3, 11, 8], [0, 7, 6, 9], [1, 13, 14, 2], [5, 4, 15, 10]],
    [[14, 3, 4, 7], [13, 1, 2, 12], [6, 15, 5, 9], [11, 8, 10, 0]],
    [[10, 0, 1, 6], [7, 3, 15, 14], [12, 5, 13, 9], [4, 2, 8, 11]],
    [[7, 13, 1, 11], [5, 6, 9, 14], [8, 10, 15, 2], [4, 3, 0, 12]],
    [[2, 6, 1, 7], [13, 12, 0, 5], [8, 14, 15, 3], [11, 4, 9, 10]],
    [[12, 10, 9, 14], [15, 8, 5, 4], [0, 2, 7, 1], [3, 13, 11, 6]],
    [[7, 8, 4, 9], [2, 11, 0, 1], [13, 15, 10, 12], [5, 6, 3, 14]],
    [[13, 10, 12, 15], [7, 11, 5, 9], [6, 4, 0, 1], [8, 14, 2, 3]]
]

# Inverser une S-box
def invert_sbox(sbox):
    # Initialise la S-box inverse comme une matrice 4x4 remplie de zéros
    inverse_sbox = [[0] * 4 for _ in range(4)]
    # Itérer sur chaque ligne et colonne de la S-box originale
    for row in range(4):
        for col in range(4):
            output_value = bitarray(f"{sbox[row][col]:04b}")
            # Déterminer la ligne et la colonne inverse en décodant la sortie de 4 bits
            # en 2 bits pour la ligne et 2 bits pour la colonne
            inverse_row = int(output_value[:2].to01(), 2)
            inverse_col = int(output_value[2:].to01(), 2)
            # Placer l'entrée originale (encodée comme (row << 2) | col) à la position inverse
            inverse_sbox[inverse_row][inverse_col] = (row << 2) | col
    
    return inverse_sbox

# Liste des S-boxes inversées pour COBRA (définies avec la fonction invert_sbox)
inverse_sboxes_cobra = [invert_sbox(sbox) for sbox in sboxes_cobra]

# Appliquer une S-box donnée à une entrée de 4 bits
def apply_sbox(input, sbox):
     # S'assurer que l'entrée est une bitarray de 4 bits
    if len(input) != 4:
        raise ValueError("Input must be a 4-bit bitarray.")

    # Convertir les 2 premiers bits pour déterminer la ligne et les 2 derniers bits pour la colonne
    row = int(input[:2].to01(), 2)  # First 2 bits as row
    col = int(input[2:].to01(), 2)  # Last 2 bits as column
 
    # Récupérer la valeur de sortie de la S-box à partir de la ligne et de la colonne
    output_value = sbox[row][col]
    # Convertir la valeur de sortie en une bitarray de 4 bits
    output_bits = bitarray(f"{output_value:04b}")
    
    return output_bits

# Fonction pour calculer l'uniformité différentielle d'une S-box
def differential_uniformity(sbox):
    # Convertir la S-box en une liste à plat pour faciliter l'itération
    flat_sbox = [item for row in sbox for item in row]
    # Initialiser la table de différences à zéro
    max_diff_prob = 0
    diff_table = np.zeros((16, 16), dtype=int)
    
    # Itérer sur toutes les entrées possibles de la S-box
    for x in range(len(flat_sbox)):
        for dx in range(16):
            # Calculer les sorties pour x et x XOR dx
            y1 = flat_sbox[x]
            y2 = flat_sbox[x ^ dx]
            # Calculer la différence de sortie
            dy = y1 ^ y2
            # Incrémenter le compteur de différence pour cette paire d'entrées
            diff_table[dx][dy] += 1
            
    # Calculer la probabilité maximale de différence
    for dx in range(1, 16):
        # Pour chaque différence d'entrée, trouver la probabilité maximale de différence de sortie
        max_diff_prob = max(max_diff_prob, max(diff_table[dx]) / 16)
        
    return max_diff_prob

# Fonction pour calculer la table d'approximation linéaire d'une S-box
def linear_approximation_table(sbox):
    # Convertir la S-box en une liste à plat pour faciliter l'itération
    flat_sbox = [item for row in sbox for item in row]
    # Initialiser la table d'approximation linéaire à zéro
    lat = np.zeros((16, 16), dtype=int)
    
    # Itérer sur toutes les paires d'entrées possibles de la S-box
    for a in range(16):
        for b in range(16):
            count = 0
            # Calculer le nombre de paires d'entrées qui satisfont la condition de parité
            for x in range(len(flat_sbox)):
                input_parity = bin(x & a).count("1") % 2
                output_parity = bin(flat_sbox[x] & b).count("1") % 2
                if input_parity == output_parity:
                    count += 1
            lat[a][b] = abs(count - 8)  # Offset de 8 pour obtenir des valeurs positives
    
    # Calculer la probabilité maximale d'approximation linéaire
    max_lin_prob = max([lat[a][b] for a in range(1, 16) for b in range(1, 16)]) / 16.0
    return max_lin_prob

# Fonction pour vérifier si une S-box a des valeurs de sortie en double
def has_duplicates(sbox):
    flat_sbox = [item for row in sbox for item in row]
    return len(set(flat_sbox)) != len(flat_sbox)

# Fonction pour inverser deux valeurs dans une S-box donnée en fonction de leurs positions
def swap_values(sbox, pos1, pos2):
    (row1, col1), (row2, col2) = pos1, pos2
    sbox[row1][col1], sbox[row2][col2] = sbox[row2][col2], sbox[row1][col1]
    return sbox

# Supprimer les valeurs dupliquées dans la S-box en échangeant pour garantir des mappages uniques (afin de pouvoir inverser la S-box)
def remove_duplicates(sbox):
    flat_sbox = [item for row in sbox for item in row]
    unique_values = set(flat_sbox)
    
    # Trouver les positions des valeurs en double et les valeurs manquantes
    duplicates = [i for i, value in enumerate(flat_sbox) if flat_sbox.count(value) > 1]
    all_possible_values = set(range(16))
    missing_values = list(all_possible_values - unique_values)

    # Remplacer les valeurs en double par des valeurs manquantes
    for duplicate_index in duplicates:
        row, col = divmod(duplicate_index, 4)
        if missing_values:
            # Remplacer la valeur en double par une valeur manquante
            sbox[row][col] = missing_values.pop()
    return sbox

# Stratégie d'échantillonnage pour générer une S-box aléatoire
def sample_strategie(sbox):
    return [sbox[i // 4][i % 4 * 4] for i in range(16)]

# Fonction pour trouver une configuration de S-box valide (respectant les conditions mathématiques) en échangeant des valeurs
def find_valid_sbox(sbox, max_attempts=1000):
    # Vérifier si la S-box a des valeurs en double
    sbox = remove_duplicates(sbox)
    best_sbox = sbox[:]
    # Calculer les probabilités de différence et d'approximation linéaire pour la S-box initiale
    best_diff_prob = differential_uniformity(best_sbox)
    best_lin_prob = linear_approximation_table(best_sbox)
    
    # Itérer sur un nombre maximal de tentatives pour trouver une configuration valide
    for attempt in range(max_attempts):
        # Choisir de manière aléatoire deux indices à échanger dans une grille 4x4
        i, j = random.sample(range(4), 2)
        k, l = random.sample(range(4), 2)
        
        # Échanger les valeurs et calculer les nouvelles probabilités
        candidate_sbox = swap_values(best_sbox, (i, j), (k, l))
        # Calculer les probabilités de différence et d'approximation linéaire pour la nouvelle S-box
        diff_prob = differential_uniformity(candidate_sbox)
        lin_prob = linear_approximation_table(candidate_sbox)
        
        # Vérifier si la nouvelle configuration est valide
        if diff_prob <= 0.25 and 0.125 <= lin_prob <= 0.25:
            print(f"Found a valid S-box configuration after {attempt+1} attempts.")
            return candidate_sbox
        
        # Sauvegarder la meilleure configuration trouvée jusqu'à présent
        if diff_prob < best_diff_prob or (diff_prob == best_diff_prob and lin_prob < best_lin_prob):
            best_sbox = candidate_sbox
            best_diff_prob = diff_prob
            best_lin_prob = lin_prob

    print("Could not find a valid configuration within the attempt limit. Returning the best attempt.")
    return best_sbox

# Fonction pour trouver une S-box valide en utilisant la stratégie d'échantillonnage
def find_valid_sbox_using_sample_strategie(sbox, max_attempts=30):
    best_sbox = sbox[:]    
    for _ in range(max_attempts):
        # Générer une S-box aléatoire en utilisant la stratégie d'échantillonnage
        sampled_sbox = sample_strategie(sbox)
        # Diviser la S-box échantillonnée en 4 lignes de 4 éléments chacune
        sampled_sbox = [sampled_sbox[i:i+4] for i in range(0, len(sampled_sbox), 4)]
        # Supprimer les valeurs en double dans la S-box échantillonnée
        sampled_sbox = remove_duplicates(sampled_sbox)
        # Trouver une configuration valide pour la S-box échantillonnée
        best_sbox = find_valid_sbox(sampled_sbox)
        # Calculer les probabilités de différence et d'approximation linéaire pour la meilleure S-box trouvée
        best_diff_prob = differential_uniformity(best_sbox)
        best_lin_prob = linear_approximation_table(best_sbox)
        
        # Vérifier si la S-box trouvée est valide
        if best_diff_prob <= 0.25 and 0.125 <= best_lin_prob <= 0.25:
            return best_sbox
    
    print("Could not find a valid configuration using the sample strategy. Returning the best attempt.")
    return best_sbox

# Fonction pour trouver de nouvelles S-boxes pour COBRA
def find_new_sboxes(sboxes_des) :
    sboxes_cobra = []
    # Itérer sur chaque S-box de DES
    for sbox in sboxes_des:
        # Trouver une S-box valide pour COBRA en utilisant la stratégie d'échantillonnage
        optimized_sbox = find_valid_sbox_using_sample_strategie(sbox)
        print("Optimized S-box:", optimized_sbox)
        # Ajouter la S-box optimisée à la liste des S-boxes de COBRA
        sboxes_cobra.append(optimized_sbox)
        # Afficher les propriétés de la S-box optimisée
        print("Differential uniformity:", differential_uniformity(optimized_sbox))
        print("Linear approximation table:", linear_approximation_table(optimized_sbox))
        print()
    # Retourner les S-boxes de COBRA
    return sboxes_cobra

#if __name__ == "__main__":
    # Decomment the following line to find new S-boxes for COBRA
    #sboxes_cobra = find_new_sboxes(sboxes_des)
