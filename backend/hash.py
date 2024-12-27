import struct
from bitarray import bitarray

# Padding function : takes a message and a block size as input and returns a padded message
# The message is padded to a multiple of block_size bytes, with a 1-bit, followed by 0s, and the message length in bits.
def pad_message(message, block_size):
    message = message.encode('utf-8') if isinstance(message, str) else message
    message_length = len(message) * 8  # Length in bits
    
    # Create a bitarray from the message
    bits = bitarray()
    bits.frombytes(message)
    
    # Append a single 1-bit
    bits.append(1)
    
    # Append enough 0 bits to leave room for the length (64 bits)
    while (len(bits) + 64) % (block_size * 8) != 0:
        bits.append(0)
    
    # Append the length as a 64-bit big-endian integer
    length_bits = bitarray(endian='big')
    length_bits.frombytes(struct.pack('>Q', message_length))
    bits.extend(length_bits)
    
    return bits.tobytes()

# Function to adjust block size
def adjust_block_size(block, target_size=16):
    # Split the block into target_size chunks, pad the last one if needed
    blocks = [block[i:i + target_size] for i in range(0, len(block), target_size)]
    if len(blocks[-1]) < target_size:
        blocks[-1] = blocks[-1].ljust(target_size, b'\x00')  # Pad last chunk
    return blocks

# Davies-Meyer compression function : takes a state and a block as input and returns a new state
# The block is split into four 32-bit words, and a series of operations are performed on the state and block.
def davies_meyer_compression(state, block, block_size=16):

    # Split block into four 32-bit words
    block_words = struct.unpack('>IIII', block[:block_size])
    
    # Generate round keys from the block words xor-ed with constants (values chosen arbitrarily)
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
    
    # Initialize local state for rounds
    local_state = state[:]
    
    # Perform multiple rounds (16 rounds for simplicity)
    for round_num in range(16):
        # Arbitrary operations mixing the state and round keys (addition, multiplication, XOR, shifts)
        new_state = [
            (local_state[0] + round_keys[round_num] + (local_state[1] << 7)) & 0xFFFFFFFF,
            (local_state[1] ^ ((local_state[0] >> 5) | (local_state[2] << 27))) & 0xFFFFFFFF,
            (local_state[2] * round_keys[round_num] + local_state[3]) & 0xFFFFFFFF,
            (local_state[3] ^ (local_state[2] + (round_keys[round_num] >> 3))) & 0xFFFFFFFF
        ]
        
        # Further mixing with XOR and rotation
        local_state = [
            (new_state[0] ^ ((new_state[3] << 11) | (new_state[3] >> 21))) & 0xFFFFFFFF,
            (new_state[1] + ((new_state[2] << 5) | (new_state[2] >> 27))) & 0xFFFFFFFF,
            (new_state[2] ^ ((new_state[0] >> 7) | (new_state[0] << 25))) & 0xFFFFFFFF,
            (new_state[3] + ((new_state[1] << 3) | (new_state[1] >> 29))) & 0xFFFFFFFF
        ]
    
    # Final XOR with the original state (Davies-Meyer construction)
    final_state = [
        (local_state[0] ^ state[0]) & 0xFFFFFFFF,
        (local_state[1] ^ state[1]) & 0xFFFFFFFF,
        (local_state[2] ^ state[2]) & 0xFFFFFFFF,
        (local_state[3] ^ state[3]) & 0xFFFFFFFF
    ]
    
    return final_state

# Merkle-Damgård hash function : takes a message and a block size as input and returns the hash value.
# Optionally, an initial state can be provided (default is [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321, 0x5364DBBA, 0x342BAD34, 0xA8824BEF, 0x99355FFE]).
# The message is padded to a multiple of block_size bytes, and split into blocks.
# Each block is processed using the Davies-Meyer compression function, with two 4-word states.
# The final state is converted to a 16-byte hash value.
# Output is a hexadecimal 256-bit hash value.
def merkle_damgard_hash(message, block_size=16, initial_state=None):
    """
    Hash function using Merkle-Damgård construction and Davies-Meyer compression.
    """
    # Ensure initial state has 4 elements (arbitrary constants)
    if initial_state is None:
        initial_state = [0x12345678, 0x9ABCDEF0, 0x0FEDCBA9, 0x87654321, 0x5364DBBA, 0x342BAD34, 0xA8824BEF, 0x99355FFE]
    
    # Split initial state into two 4-word states
    state_a = initial_state[:4]
    state_b = initial_state[4:]
    
    # Pad the input message
    padded_message = pad_message(message, block_size)
    
    # Process blocks for both states
    blocks = adjust_block_size(padded_message, 16)
    for block in blocks:
        state_a = davies_meyer_compression(state_a, block)
        state_b = davies_meyer_compression(state_b, block)
    
    # Combine the states into a 32-byte hash
    final_hash = struct.pack('>IIIIIIII', *(state_a + state_b))
    return final_hash.hex()

if __name__ == "__main__":
    # Test the hash function
    message = "Hello, world!"
    hash_value = merkle_damgard_hash(message, block_size=32)
    print("Complex hash value:", hash_value)
