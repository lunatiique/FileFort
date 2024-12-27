# Description: A simple key derivation function based on a sponge hash function.


def pad_to_block_size(data, block_size):
    """Pads the input to the specified block size using zero-padding."""
    return data + b'\x00' * (block_size - (len(data) % block_size)) 

def xor_bytes(a, b):
    """Performs byte-wise XOR between two byte sequences."""
    return bytes(x ^ y for x, y in zip(a, b))

def sponge_hash(password, output_size=32, state_size=200, rounds=1000):
    """
    Implements a simple sponge function with a spin-based round system.
    
    - `password`: Input password to hash.
    - `output_size`: Desired size of the output in bytes (e.g., 32 bytes for 256-bit key).
    - `state_size`: Size of the internal state in bytes (should be large enough, e.g., 200 bytes).
    - `rounds`: Number of spin rounds for each block absorption.
    """
    # Initialize state with all zeros
    state = bytearray(state_size)  # Use bytearray to allow item assignment
    
    # Convert the password into a byte array
    password_bytes = password.encode('utf-8')
    block_size = 64  # Define a block size for absorption (e.g., 64 bytes)
    
    # Pad the password to match the block size
    padded_password = pad_to_block_size(password_bytes, block_size)
    
    # Absorb phase: Split password into blocks and XOR with state
    for i in range(0, len(padded_password), block_size):
        block = padded_password[i:i+block_size]
        block = block.ljust(state_size, b'\x00')  # Ensure block is same size as state
        
        # XOR block into state
        state = bytearray(xor_bytes(state, block))  # Convert back to bytearray after XOR
        
        # Perform multiple "spin" rounds
        for _ in range(rounds):
            # Simple permutation (pseudo-random mixing)
            state = sponge_permutation(state)

    # Squeeze phase: Generate output by repeatedly permuting and taking output bytes
    output = bytearray()
    while len(output) < output_size:
        state = sponge_permutation(state)
        output.extend(state[:output_size - len(output)])  # Append bytes until output size

    return bytes(output)

def sponge_permutation(state):
    """A basic permutation function to mix the state."""
    # Rotate each byte in state and XOR with neighboring bytes
    for i in range(len(state)):
        left = (i - 1) % len(state)
        right = (i + 1) % len(state)
        
        # Simple rotation and XOR to introduce diffusion
        state[i] = (state[i] ^ ((state[left] << 1) | (state[left] >> 7)) ^ state[right]) & 0xFF

    # Perform additional bitwise operations to add complexity
    for i in range(1, len(state), 2):
        state[i] ^= (state[i - 1] ^ (state[(i + 1) % len(state)] >> 3)) & 0xFF
    
    return state

def bytes_to_int(b):
    """Converts bytes to an integer."""
    return int.from_bytes(b, byteorder='big')
