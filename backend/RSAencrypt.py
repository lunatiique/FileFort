import base64
import ast
from classes.Keys import Keys

# Chiffrer un message en utilisant RSA avec la clé publique (n, e). C = M^e mod n
def encrypt_message(message, n, e):
    return [pow(char, e, n) for char in message]

# Déchiffrer un message en utilisant RSA avec la clé privée (n, d). M = C^d mod n
def decrypt_message(encrypted_message, n, d):
    decrypted_chars = []
    for char in encrypted_message:
        decrypted_char = pow(char, d, n)
        if decrypted_char < 0x110000:
            decrypted_chars.append(chr(decrypted_char))
        else:
            raise ValueError(f"Decrypted value {decrypted_char} is out of range for chr()")
    return ''.join(decrypted_chars)

# Chiffrer un fichier en utilisant RSA avec la clé publique (n, e)
def encrypt_file(file, n, e):
    # Lire le fichier en binaire
    data = file.read()
    # Chiffrer les données binaires octet par octet
    encrypted_data = [pow(byte, e, n) for byte in data]
    # Convertir les données chiffrées en base64
    encrypted_data_base64 = base64.b64encode(bytes(str(encrypted_data), 'utf-8')).decode('utf-8')
    return encrypted_data_base64

# Déchiffrer un fichier en utilisant RSA avec la clé privée (n, d)
def decrypt_file(file, n, d):
    # Lire le fichier
    encrypted_data_base64 = file.read()
    # Décoder le base64 pour obtenir les données chiffrées
    encrypted_data = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode('utf-8'))
    # Déchiffrer le fichier
    decrypted_data = decrypt_message(encrypted_data, n, d)
    return decrypted_data

# Chiffrer un message en utilisant RSA avec la clé publique (n, e) en divisant le message en blocs
def encrypt_message_blockwise(message, n, e, block_size):
    # Convertir le message en octets s'il s'agit d'une chaîne
    if isinstance(message, str):
        message = message.encode()
    # Diviser le message en blocs
    blocks = [message[i:i + block_size] for i in range(0, len(message), block_size)]
    encrypted_blocks = [pow(int.from_bytes(block, byteorder='big'), e, n) for block in blocks]
    return encrypted_blocks

# Déchiffrer un message en utilisant RSA avec la clé privée (n, d) en divisant le message en blocs
def decrypt_message_blockwise(encrypted_blocks, n, d, block_size):
    decrypted_message = bytearray()
    for block in encrypted_blocks:
        decrypted_block = pow(block, d, n)
        decrypted_message.extend(decrypted_block.to_bytes(block_size, byteorder='big'))
    return decrypted_message.decode()

# Chiffrer un fichier en utilisant RSA avec la clé publique (n, e) en divisant le fichier en blocs
def encrypt_file_block(file, n, e):
    # Lire le fichier en binaire
    data = file.read()
    block_size = (n.bit_length() // 8) - 1
    encrypted_data = encrypt_message_blockwise(data, n, e, block_size)
    # Encoder les données chiffrées en base64 pour le stockage
    encrypted_data_base64 = base64.b64encode(str(encrypted_data).encode()).decode()
    return encrypted_data_base64

# Déchiffrer un fichier en utilisant RSA avec la clé privée (n, d) en divisant le fichier en blocs
def decrypt_file_block(file, n, d):
    # Lire le fichier chiffré (encodé en base64)
    encrypted_data_base64 = file.read()
    # Décoder le base64 pour obtenir les blocs chiffrés
    encrypted_blocks = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode())
    block_size = (n.bit_length() // 8) - 1
    # Déchiffrer les blocs
    decrypted_data = decrypt_message_blockwise(encrypted_blocks, n, d, block_size)
    return decrypted_data

# Exemple d'utilisation (pour test)
if __name__ == '__main__':
    # Lire la clé depuis le fichier
    keys = Keys()
    keys.read_key(f"../users/luna/luna_private_key.pem")
    keys.read_key(f"../users/luna/public_key.pem")

    # Chiffrer un fichier
    with open("test.txt", "rb") as file:  # Ouvrir en mode binaire
        encrypted_message = encrypt_file_block(file, keys.n, keys.e)

    # Enregistrer le fichier chiffré
    with open("encrypted_file.txt", "w") as file:
        file.write(encrypted_message)

    # Déchiffrer le fichier
    with open("encrypted_file.txt", "r") as file:
        decrypted_message = decrypt_file_block(file, keys.n, keys.d)
    print("Decrypted message:", decrypted_message)
