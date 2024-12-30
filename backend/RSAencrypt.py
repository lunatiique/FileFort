import base64
import ast
from classes.Keys import Keys

# Encrypt a message using RSA with the public key (n, e). C = M^e mod n
def encrypt_message(message, n, e):
    return [pow(char, e, n) for char in message]

# Decrypt a message using RSA with the private key (n, k). M = C^k mod n
def decrypt_message(encrypted_message, n, k):
    decrypted_chars = []
    for char in encrypted_message:
        decrypted_char = pow(char, k, n)
        if decrypted_char < 0x110000:
            decrypted_chars.append(chr(decrypted_char))
        else:
            raise ValueError(f"Decrypted value {decrypted_char} is out of range for chr()")
    return ''.join(decrypted_chars)

def encrypt_file(file, n, e):
    # Read the file as binary
    data = file.read()
    # Encrypt the binary data byte by byte
    encrypted_data = [pow(byte, e, n) for byte in data]
    # Convert encrypted data to base64
    encrypted_data_base64 = base64.b64encode(bytes(str(encrypted_data), 'utf-8')).decode('utf-8')
    return encrypted_data_base64

def decrypt_file(file, n, k):
    # Read the file
    encrypted_data_base64 = file.read()
    # Decode base64 to get the encrypted data
    encrypted_data = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode('utf-8'))
    # Decrypt the file
    decrypted_data = decrypt_message(encrypted_data, n, k)
    return decrypted_data


def encrypt_message_blockwise(message, n, e, block_size):
    # Convert the message to bytes if it's a string
    if isinstance(message, str):
        message = message.encode()
    # Break message into blocks
    blocks = [message[i:i + block_size] for i in range(0, len(message), block_size)]
    encrypted_blocks = [pow(int.from_bytes(block, byteorder='big'), e, n) for block in blocks]
    return encrypted_blocks

def decrypt_message_blockwise(encrypted_blocks, n, k, block_size):
    decrypted_message = bytearray()
    for block in encrypted_blocks:
        decrypted_block = pow(block, k, n)
        decrypted_message.extend(decrypted_block.to_bytes(block_size, byteorder='big'))
    return decrypted_message.decode()

def encrypt_file_block(file, n, e):
    # Read the file as binary
    data = file.read()
    block_size = (n.bit_length() // 8) - 1
    encrypted_data = encrypt_message_blockwise(data, n, e, block_size)
    # Encode encrypted data as base64 for storage
    encrypted_data_base64 = base64.b64encode(str(encrypted_data).encode()).decode()
    return encrypted_data_base64

def decrypt_file_block(file, n, k):
    # Read the encrypted file (base64-encoded)
    encrypted_data_base64 = file.read()
    # Decode base64 to get encrypted blocks
    encrypted_blocks = ast.literal_eval(base64.b64decode(encrypted_data_base64).decode())
    block_size = (n.bit_length() // 8) - 1
    # Decrypt the blocks
    decrypted_data = decrypt_message_blockwise(encrypted_blocks, n, k, block_size)
    return decrypted_data




if __name__ == '__main__':
    #Read key from file
    keys = Keys()
    keys.read_key(f"../users/luna/private_key.pem")
    keys.read_key(f"../users/luna/public_key.pem")

    # Encrypt a file
    with open("test.txt", "rb") as file:  # Open in binary mode
        encrypted_message = encrypt_file_block(file, keys.n, keys.e)

    # Save the encrypted file
    with open("encrypted_file.txt", "w") as file:
        file.write(encrypted_message)

    # Decrypt the file
    with open("encrypted_file.txt", "r") as file:
        decrypted_message = decrypt_file_block(file, keys.n, keys.d)
    print("Decrypted message:", decrypted_message)


