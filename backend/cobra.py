#this file contains the functions that allows to encode your data using the COBRA algorithm
import random 
from bitarray import bitarray
from round_keys import key_scheduling
from s_boxes import sboxes_cobra, apply_sbox, inverse_sboxes_cobra
from multiprocessing import Pool
from math_functions import inv_mod
from key_derivation_function import sponge_hash
import time

# Generate random key of 128 bits
def generate_key_128():
    key = bitarray()
    key.frombytes(random.getrandbits(128).to_bytes(16, byteorder='big'))
    return key


# Add round key : XOR with the iteration key (128 bits)
def add_round_key(bloc, key):
    return bloc ^ key

# Functions needed for parallelization of the S-boxes
def apply_first_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[0])
def apply_second_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[1])
def apply_third_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[2])
def apply_fourth_sbox(bloc):
    return apply_sbox(bloc, sboxes_cobra[3])

# Functions needed for parallelization of the inverse S-boxes
def inverse_first_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[0])
def inverse_second_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[1])
def inverse_third_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[2])
def inverse_fourth_sbox(bloc):
    return apply_sbox(bloc, inverse_sboxes_cobra[3])

# Substitution : We apply 32 times (in parallel) the same S-box to each 4 bits of the bloc
def substitution(bloc, i):
    # Separate the bloc into 32 blocs of 4 bits
    blocs = [bloc[i:i+4] for i in range(0, 128, 4)]
    # Use multiprocessing to apply the S-box in parallel
    # Change the S-box applied depending on the round number
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
    # Reassemble the bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

# Inverse substitution : We apply the inverse S-box to each 4 bits of the bloc
def inverse_substitution(bloc, i):
    # Separate the bloc into 32 blocs of 4 bits
    blocs = [bloc[i:i+4] for i in range(0, 128, 4)]
    # Use multiprocessing to apply the inverse S-box in parallel
    # Change the S-box applied depending on the round number
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
    # Reassemble the bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

def apply_feistel_function(right_bloc, key, feistel_table):
    # The right bloc is divided into 8 blocs of 8 bits
    sub_blocs = [right_bloc[i:i+8] for i in range(0, 64, 8)]
    # Invert the order of the bits of each sub-bloc
    sub_blocs = [b[::-1] for b in sub_blocs]
    # Apply the inverse function f(x) = ((x+1)^-1mod257)-1
    z_blocs = [feistel_table[int(b.to01(), 2)] for b in sub_blocs]
    # Reassemble the bloc
    z_bloc = bitarray()
    for z in z_blocs:
        z_bloc.extend(z)
    # Apply permutation P to the bloc
    z_bloc = permutation_P(z_bloc)
    # Divide into 8 blocs of 8 bits again
    z_blocs = [z_bloc[i:i+8] for i in range(0, 64, 8)]
    # Generate pseudo-random numbers using z_blocs as seeds
    prng_bloc = generate_pseudo_random_numbers(z_blocs)
    # Derivate the key using KDF algorithm
    derivated_key_tmp = sponge_hash(key.to01(), 8)
    # Convert to bitarray
    derivated_key = bitarray()
    derivated_key.frombytes(derivated_key_tmp)
    # XOR the pseudo-random numbers with the derivated key
    output = prng_bloc ^ derivated_key
    return output

# Permutation P : We apply a permutation to the bloc of 64 bits
def permutation_P(bloc):
    # define permutation vector (improve it ?)
    P = [63, 31, 62, 30, 61, 29, 60, 28, 59, 27, 58, 26, 57, 25, 56, 24, 55, 23, 54, 22, 53, 21, 52, 20, 51, 19, 50, 18, 49, 17, 48, 16, 47, 15, 46, 14, 45, 13, 44, 12, 43, 11, 42, 10, 41, 9, 40, 8, 39, 7, 38, 6, 37, 5, 36, 4, 35, 3, 34, 2, 33, 1, 32, 0]
    # Apply the permutation
    if len(bloc) == 64:
        bloc = bitarray([bloc[i] for i in P])
    else:
        raise ValueError("Bloc must be of 64 bits.")
    return bloc

# Generate pseudo-random numbers using z_blocs as seeds
def generate_pseudo_random_numbers(z_blocs):
    prng_blocs = []
    for z_bloc in z_blocs:
        # Generate pseudo-random number using z_bloc as seed
        random.seed(int(z_bloc.to01(), 2))
        prng_bloc = bitarray()
        prng_bloc.frombytes(random.getrandbits(8).to_bytes(1, byteorder='big'))
        prng_blocs.append(prng_bloc)
    # We assemble the pseudo-random numbers into a bloc
    prng_bloc = bitarray()
    for prng in prng_blocs:
        prng_bloc.extend(prng)
    return prng_bloc

# Compute the Feistel function : f(x) = ((x + 1)^-1 mod 257)-1
def feistel_function(x):
    # If x is 256, the result is 0 (to avoid division by 0)
    if x == 256:
        return 0
    else:
        return inv_mod((x + 1) % 257, 257) - 1


# Tabulate the Feistel function for all values of x from 0 to 255.
def tabulation_function():
    table = [0] * 256
    for i in range(256):
        table[i] = bitarray(format(feistel_function(i), '08b'))
    return table

# Feistel de Réré : We apply 3 or 4 rounds of the Feistel network
def feistel_de_rere(bloc, feistel_table, key):
    # Separate the bloc into 2 blocs of 64 bits
    left_bloc = bloc[:64]
    right_bloc = bloc[64:]
    # We do 3 rounds of the Feistel network
    for _ in range(0, 3):
        tmp_left_bloc = left_bloc
        left_bloc = right_bloc
        right_bloc = tmp_left_bloc ^ apply_feistel_function(right_bloc, key, feistel_table)
    # We reassemble the bloc
    bloc = bitarray()
    bloc.extend(left_bloc)
    bloc.extend(right_bloc)
    return bloc

# Decipher Feistel de Réré : We apply 3 or 4 rounds of the Feistel network in reverse
def decipher_feistel_de_rere(bloc, feistel_table, key):
    # Separate the bloc into 2 blocs of 64 bits
    left_bloc = bloc[:64]
    right_bloc = bloc[64:]
    # We do 3 rounds of the Feistel network
    for _ in range(0, 3):
        tmp_right_bloc = right_bloc
        right_bloc = left_bloc
        left_bloc = tmp_right_bloc ^ apply_feistel_function(left_bloc, key, feistel_table)
    # We reassemble the bloc
    bloc = bitarray()
    bloc.extend(left_bloc)
    bloc.extend(right_bloc)
    return bloc

# Linear transformation : We realize binary operations on 4 blocs of 32 bits
def linear_transformation(bloc):
    # Separate the bloc into 4 blocs of 32 bits
    blocs = [bloc[i:i+32] for i in range(0, 128, 32)]
    # circular left shift of 13 bits for bloc 0
    blocs[0] = blocs[0][13:] + blocs[0][:13]
    # circular left shift of 3 bits for bloc 2
    blocs[2] = blocs[2][3:] + blocs[2][:3]
    # XOR operation between bloc 0, 1 and 2 saved in bloc 1
    blocs[1] = blocs[0] ^ blocs[1] ^ blocs[2]
    # XOR operation between bloc 2, 3 and 0 (with circular left shift of 3 bits) saved in bloc 3
    blocs[3] = blocs[2] ^ blocs[3] ^ (blocs[0][3:] + blocs[0][:3])
    # circular left shift of 1 bit for bloc 1
    blocs[1] = blocs[1][1:] + blocs[1][:1]
    # circular left shift of 7 bits for bloc 3
    blocs[3] = blocs[3][7:] + blocs[3][:7]
    # XOR operation between bloc 1, 0 and 3 saved in bloc 0
    blocs[0] = blocs[1] ^ blocs[0] ^ blocs[3]
    # XOR operation between bloc 3, 2 and 1 (with circular left shift of 7 bits) saved in bloc 2
    blocs[2] = blocs[3] ^ blocs[2] ^ (blocs[1][7:] + blocs[1][:7])
    # circular left shift of 5 bits for bloc 0
    blocs[0] = blocs[0][5:] + blocs[0][:5]
    # circular left shift of 22 bits for bloc 2
    blocs[2] = blocs[2][22:] + blocs[2][:22]
    # We reassemble the bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

# Inverse linear transformation : We realize binary operations on 4 blocs of 32 bits
def inverse_linear_transformation(bloc):
    # Separate the bloc into 4 blocs of 32 bits
    blocs = [bloc[i:i+32] for i in range(0, 128, 32)]
    # circular right shift of 22 bits for bloc 2
    blocs[2] = blocs[2][-22:] + blocs[2][:-22]
    # circular right shift of 5 bits for bloc 0
    blocs[0] = blocs[0][-5:] + blocs[0][:-5]
    # XOR operation between bloc 3, 2 and 1 (with circular left shift of 7 bits) saved in bloc 2
    blocs[2] = blocs[3] ^ blocs[2] ^ (blocs[1][7:] + blocs[1][:7])
    # XOR operation between bloc 0, 1 and 3 saved in bloc 0
    blocs[0] = blocs[0] ^ blocs[1] ^ blocs[3]
    # circular right shift of 7 bits for bloc 3
    blocs[3] = blocs[3][-7:] + blocs[3][:-7]
    # circular right shift of 1 bit for bloc 1
    blocs[1] = blocs[1][-1:] + blocs[1][:-1]
    # XOR operation between bloc 2, 3 and 0 (with circular left shift of 3 bits) saved in bloc 3
    blocs[3] = blocs[2] ^ blocs[3] ^ (blocs[0][3:] + blocs[0][:3])
    # XOR operation between bloc 0, 1 and 2 saved in bloc 1
    blocs[1] = blocs[0] ^ blocs[1] ^ blocs[2]
    # circular right shift of 3 bits for bloc 2
    blocs[2] = blocs[2][-3:] + blocs[2][:-3]
    # circular right shift of 13 bits for bloc 0
    blocs[0] = blocs[0][-13:] + blocs[0][:-13]
    # We reassemble the bloc
    bloc = bitarray()
    for b in blocs:
        bloc.extend(b)
    return bloc

def initial_permutation(bloc, key):
    random.seed(int(key.to01(), 2))
    # permutation vector of 128 bits
    p_vector = list(range(128))
    random.shuffle(p_vector)
    # apply the permutation
    bloc = bitarray([bloc[i] for i in p_vector])
    return bloc

def reverse_initial_permutation(bloc, key):
    random.seed(int(key.to01(), 2))
    # permutation vector of 128 bits
    p_vector = list(range(128))
    random.shuffle(p_vector)
    # apply the permutation
    bloc = bitarray([bloc[p_vector.index(i)] for i in range(128)])
    return bloc

def final_permutation(bloc, key):
    random.seed(int(key.to01(), 2))
    # permutation vector of 128 bits
    p_vector = list(range(128))
    random.shuffle(p_vector)
    # apply the permutation
    bloc = bitarray([bloc[i] for i in p_vector])
    return bloc

def reverse_final_permutation(bloc, key):
    random.seed(int(key.to01(), 2))
    # permutation vector of 128 bits
    p_vector = list(range(128))
    random.shuffle(p_vector)
    # apply the permutation
    bloc = bitarray([bloc[p_vector.index(i)] for i in range(128)])
    return bloc


# Encoding : We encode the data using the COBRA algorithm
def encode_bloc(data, key):
    # We ensure the data is a 128-bit bloc
    if len(data) != 128:
        raise ValueError("Data must be of 128 bits.")
    # We tabulate the Feistel function
    feistel_table = tabulation_function()
    # We generate the 33 keys
    keys = key_scheduling(key)
    # Initial permutation
    data = initial_permutation(data, keys[0])
    # We apply the 32 rounds
    for i in range(0, 12):
        bloc = add_round_key(data, keys[i])
        bloc = substitution(bloc, i)
        bloc = feistel_de_rere(bloc, feistel_table, keys[i])
        bloc = linear_transformation(bloc)
    # Final permutation
    data = final_permutation(data, keys[31])
    # Final XOR with the last key
    data = add_round_key(data, keys[32])
    return data

# Decoding : We decode the data using the COBRA algorithm
def decode_bloc(data, key):
    # We ensure the data is a 128-bit bloc
    if len(data) != 128:
        raise ValueError("Data must be of 128 bits.")
    # We tabulate the Feistel function
    feistel_table = tabulation_function()
    # We generate the 33 keys
    keys = key_scheduling(key)
    # We remove the last key
    data = add_round_key(data, keys[32])
    # Reverse final permutation
    data = reverse_final_permutation(data, keys[31])
    # We apply the 32 rounds in reverse
    for i in range(12, 0, -1):
        bloc = inverse_linear_transformation(data)
        bloc = decipher_feistel_de_rere(bloc, feistel_table, keys[i])
        bloc = inverse_substitution(bloc, i)
        bloc = add_round_key(data, keys[i])
    # Reverse initial permutation
    data = reverse_initial_permutation(data, keys[0])
    return data


# For testing purposes, we convert the text into 128-bit blocs
def convert_text_to_blocs_128(text):
    # convert text to binary representation using bitarray
    data = bitarray()
    data.frombytes(text.encode('utf-8'))
    # separate data into 128-bit blocks
    data = [data[i:i+128] for i in range(0, len(data), 128)]
    # add padding to the last block if necessary
    if len(data[-1]) < 128:
        data[-1].extend('0' * (128 - len(data[-1])))
    return data

# For testing purposes, we convert the 128-bit blocs into text
def convert_blocs_128_to_text(data):
    #join all the 128-bit blocks
    text = bitarray()
    for bloc in data:
        text.extend(bloc)
    # convert the bitarray to text
    text = text.tobytes().decode('utf-8')
    return text

# Encode text using COBRA algorithm (input is a string, output is an hexadecimal string)
def encode_text(text, key):
    data = convert_text_to_blocs_128(text)
    encoded_data = []
    for bloc in data:
        encoded_data.append(encode_bloc(bloc, key))
    # convert the encoded data to hexadecimal
    encoded_data = [b.tobytes().hex() for b in encoded_data]
    # join all the hexadecimal blocs
    encoded_data = ''.join(encoded_data)
    return encoded_data

# Decode text using COBRA algorithm (input is an hexadecimal string)
def decode_text(data, key):
    # convert the hexadecimal data to bitarray
    bin_data = bitarray()
    bin_data.frombytes(bytes.fromhex(data))
    # separate data into 128-bit blocks
    bin_data = [bin_data[i:i+128] for i in range(0, len(bin_data), 128)]
    # initialize the decoded data
    decoded_data = []
    for bloc in bin_data:
        decoded_data.append(decode_bloc(bloc, key))
    return convert_blocs_128_to_text(decoded_data)

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