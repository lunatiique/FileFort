import base64
import ast
from classes.Keys import Keys
import os

# Chiffrer un message en utilisant RSA avec padding aléatoire
def encrypt_message_with_padding(message, n, e, block_size):
    if isinstance(message, str):
        message = message.encode()

    # Diviser le message en blocs de taille `block_size // 2`
    blocks = [message[i:i + block_size // 2] for i in range(0, len(message), block_size // 2)]
    padding_size = block_size // 2
    padded_blocks = []

    for block in blocks:
        # Ajouter un padding aléatoire pour remplir le bloc
        padding = os.urandom(padding_size)
        padded_block = block + padding
        padded_blocks.append(padded_block)
    # Chiffrer les blocs avec padding
    encrypted_blocks = [pow(int.from_bytes(block, byteorder='big'), e, n) for block in padded_blocks]
    return encrypted_blocks

# Déchiffrer un message en utilisant RSA et enlever le padding aléatoire
def decrypt_message_with_padding(encrypted_blocks, n, d, block_size):
    decrypted_message = bytearray()
    padding_size = block_size // 2  # La moitié de la taille du bloc est utilisée pour le padding aléatoire

    for block in encrypted_blocks:
        # Effectuer le déchiffrement RSA
        decrypted_block = pow(block, d, n)
        # Convertir le bloc déchiffré en octets, en s'assurant qu'il a exactement block_size octets
        block_bytes = decrypted_block.to_bytes(block_size, byteorder='big')
        # Supprimer les "\x00" au début du bloc
        block_bytes = block_bytes.lstrip(b'\x00')
        # Extraire la partie du message original (en enlevant le padding aléatoire)
        original_message_part = block_bytes[:-padding_size]
        # Ajouter la partie du message original au résultat
        decrypted_message.extend(original_message_part)

    return decrypted_message.decode()

# Chiffrer un fichier en utilisant RSA avec padding aléatoire
def encrypt_file_with_padding(file, n, e):
    data = file.read()
    block_size = (n.bit_length() // 8) - 1
    encrypted_data = encrypt_message_with_padding(data, n, e, block_size)
    # Encoder les blocs chiffrés en base64 pour le stockage
    encrypted_data_base64 = base64.b64encode(str(encrypted_data).encode()).decode()
    return encrypted_data_base64

# Déchiffrer un fichier en utilisant RSA et enlever le padding aléatoire
def decrypt_file_with_padding(file, n, d):
    encrypted_data_base64 = file.read()
    # Décoder le base64 pour obtenir les blocs chiffrés
    encrypted_blocks = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode())
    block_size = (n.bit_length() // 8) - 1
    decrypted_data = decrypt_message_with_padding(encrypted_blocks, n, d, block_size)
    return decrypted_data

# Chiffrer un fichier PGM en utilisant RSA avec la clé publique (n, e)
def encrypt_pgm(file, n, e):
    # Lire le fichier PGM en binaire
    data = file.read()

    # Séparer l'en-tête et les données de pixel
    parts = data.split(b'\n', 3)
    header = b'\n'.join(parts[:3]) + b'\n'
    pixel_data = parts[3]

    # Ajouter un padding pour que la taille des blocs soit correcte
    block_size = (n.bit_length() // 8) - 1
    padding_length = block_size - len(pixel_data) % block_size
    if padding_length != block_size:
        pixel_data += b'\x00' * padding_length  # Si la taille n'est pas un multiple de la taille du bloc, ajouter un padding

    # Chiffrer les blocs de données de pixel (en utilisant la méthode RSA classique)
    encrypted_blocks = []
    for i in range(0, len(pixel_data), block_size):
        block = pixel_data[i:i + block_size]
        encrypted_blocks.append(pow(int.from_bytes(block, byteorder='big'), e, n))

    # Convertir les blocs chiffrés en base64 pour le stockage
    encrypted_data = base64.b64encode(bytes(str(encrypted_blocks), 'utf-8')).decode('utf-8')

    # Retourner l'en-tête et les données chiffrées
    return header + encrypted_data.encode('utf-8')

# Déchiffrer un fichier PGM en utilisant RSA avec la clé privée (n, d)
def decrypt_pgm(file, n, d):
    # Lire le fichier PGM
    data = file.read()

    # Séparer l'en-tête et les données chiffrées
    parts = data.split(b'\n', 3) 
    header = b'\n'.join(parts[:3]) + b'\n'
    encrypted_data_base64 = parts[3]

    # Décoder le base64 pour obtenir les blocs chiffrés
    encrypted_blocks = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode())

    # Déchiffrer les blocs de données de pixel (en utilisant la méthode RSA classique)
    block_size = (n.bit_length() // 8) - 1
    decrypted_pixel_data = bytearray()
    for block in encrypted_blocks:
        decrypted_value = pow(block, d, n)
        decrypted_pixel_data.extend(decrypted_value.to_bytes(block_size, byteorder='big'))

    # Supprimer le padding ajouté lors du chiffrement
    decrypted_pixel_data = decrypted_pixel_data.rstrip(b'\x00')

    # Retourner l'en-tête et les données déchiffrées
    return header + decrypted_pixel_data

# Exemple d'utilisation (pour test)
if __name__ == '__main__':
    # Lire la clé depuis le fichier
    keys = Keys()
    keys.read_key(f"../users/luna/luna_private_key.pem")
    keys.read_key(f"../users/luna/public_key.pem")

    # Chiffrer/ Déchiffrer un fichier .txt
    with open("coucou.txt", "r") as file:
        encrypted_data = encrypt_file_with_padding(file, keys.n, keys.e)

    with open("encrypted_coucou.txt", "w") as file:
        file.write(encrypted_data)

    with open("encrypted_coucou.txt", "r") as file:
        decrypted_data = decrypt_file_with_padding(file, keys.n, keys.d)
        print("texte lu : ",decrypted_data)


