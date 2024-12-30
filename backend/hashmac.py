from hash import merkle_damgard_hash
from bitarray import bitarray

# Function to normalize the key
# It takes a bitarray key as input and returns a bitarray of length 256
def normalize_key(key):
    # Convert key to bitarray
    key_bits = bitarray()
    key_bits.frombytes(key)
    
    # If key is longer than hash block size, hash it
    if len(key_bits) > 256:
        key_bits = bitarray()
        key_bits.frombytes(merkle_damgard_hash(key_bits.tobytes()))
    # If key is shorter than hash block size, pad it
    elif len(key_bits) < 256:
        key_bits.extend(bitarray('0' * (256 - len(key_bits))))
    
    return key_bits

# Function to create derived keys from the normalized key
# It takes a normalized key as input and returns two derived keys
# The input and outputs are bitarrays
def create_derived_keys(normalized_key):
    # Fixed padding constants of 64 bytes for ipad and opad
    ipad = bitarray()
    ipad.frombytes((0x36).to_bytes(1, byteorder='big') * 32)
    opad = bitarray()
    opad.frombytes((0x5C).to_bytes(1, byteorder='big') * 32)
    # Apply XOR element-wise using bitarray
    k_i = normalized_key ^ ipad
    k_o = normalized_key ^ opad
    
    return k_i, k_o

# HMAC function : takes a key and a message as input and returns the HMAC value
# key should be a bitarray, message should be a bytes object
# It returns the HMAC value as a hex string
def hmac(key, message):
    # Normalize the key
    normalized_key = normalize_key(key)
    # Create derived keys
    k_i, k_o = create_derived_keys(normalized_key)
    # Convert message to bitarray
    message_bits = bitarray()
    message_bits.frombytes(message)
    # Compute the inner hash : hash(k_i + message)
    inner_hash = merkle_damgard_hash((k_i + message_bits).tobytes())
    # Convert inner_hash to bitarray
    inner_hash_bits = bitarray()
    inner_hash_bits.frombytes(inner_hash.encode())
    # Compute the outer hash : hash(k_o + inner_hash)
    outer_hash = merkle_damgard_hash((k_o + inner_hash_bits).tobytes())
    # Return the outer hash as the HMAC value
    return outer_hash

if __name__ == "__main__":
    # Test the hmac function
    key = bitarray('01100101101100101011110000010101101111101110111000111000110101001011000010101101100101100110010110101001110111101100101000101011')
    message = b"The quick brown fox jumps over the lazy dog"
    hmac_value = hmac(key, message)
    print("HMAC value:", hmac_value)