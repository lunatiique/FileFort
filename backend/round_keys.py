from bitarray import bitarray
from s_boxes import sboxes_cobra, apply_sbox

# Define the binary representation of phi
binary_phi = 0b10110111011010111011010111011011

# Key scheduling : We generate 33 keys of 128 bits using the original key of 128, 192 or 256 bits.
def key_scheduling(key):
    # Check if the key is 128, 192 or 256 bits long.
    if len(key) != 128 and len(key) != 192 and len(key) != 256:
        raise ValueError("The key must be 128, 192 or 256 bits long.")
    # If the key is less than 256 bits, we add 0s to the right until it reaches 256 bits
    if len(key) < 256:
        key.extend(bitarray('0' * (256 - len(key))))
    # Divide the key into 8 blocks of 32 bits & Generate 132 keys of 32 bits 
    w = key_expansion(key)
    # We apply the S-box to each key
    blocs = apply_sbox_to_keys(w)
    # We assemble the 132 keys into 33 round keys of 128 bits
    round_keys = assemble_keys(blocs)
    return round_keys



# Expansion of the key: generate 132 keys of 32 bits
def key_expansion(key):
    w = [key[i:i+32] for i in range(0, 256, 32)]
    for i in range(8, 132):
        #apply the XOR operation to the 4 previous keys, the binary representation of phi and the iteration number
        new_key = w[i-8] ^ w[i-5] ^ w[i-3] ^ w[i-1] ^ bitarray(bin(binary_phi)[2:]) ^ bitarray(bin(i)[2:].zfill(32))
        #apply the left rotation of 11 bits
        new_key = new_key << 11
        #add the new key to the list of keys
        w.append(new_key[:32])
    return w



# Apply S-boxes to a 32-bit block
def apply_sbox_to_bloc(bloc):
    # Ensure bloc is a 32-bit bitarray
    if len(bloc) != 32:
        raise ValueError("Bloc must be a 32-bit bitarray.")
    
    # Split the 32-bit bloc into 8 4-bit sub-blocs
    sub_blocs = [bloc[i:i+4] for i in range(0, 32, 4)]
    
    # Apply the S-boxes to each 4-bit sub-bloc
    output_bloc = bitarray()
    for i, sub_bloc in enumerate(sub_blocs):
        output_bloc.extend(apply_sbox(sub_bloc, sboxes_cobra[i]))

    return output_bloc

def apply_sbox_to_keys(keys):
    # Ensure keys is a list of 32-bit bitarrays
    if not all(len(key) == 32 for key in keys):
        raise ValueError("Keys must be 32-bit bitarrays.")
    
    # Apply the S-boxes to each key
    output_keys = [apply_sbox_to_bloc(key) for key in keys]
    
    return output_keys

def assemble_keys(keys):
    # Ensure keys is a list of 32-bit bitarrays
    if not all(len(key) == 32 for key in keys):
        raise ValueError("Keys must be 32-bit bitarrays.")
    
    # Assemble the 132 keys into 33 round keys of 128 bits
    round_keys = []
    for i in range(0, 132, 4):
        round_key = bitarray()
        for j in range(4):
            round_key.extend(keys[i+j])
        round_keys.append(round_key)
    
    return round_keys