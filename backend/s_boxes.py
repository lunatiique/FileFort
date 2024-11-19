import numpy as np
import random
from bitarray import bitarray

# Define the S-box using the extracted 4-bit values from S-box 0
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

sboxes_des = [sbox_0, sbox_1, sbox_2, sbox_3, sbox_4, sbox_5, sbox_6, sbox_7]

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

def invert_sbox(sbox):
    # Initialize the inverse S-box as a 4x4 matrix filled with zeros
    inverse_sbox = [[0] * 4 for _ in range(4)]
    # Iterate over each row and column in the original S-box
    for row in range(4):
        for col in range(4):
            output_value = bitarray(f"{sbox[row][col]:04b}")
            # Determine the inverse row and column by decoding the 4-bit output
            inverse_row = int(output_value[:2].to01(), 2)
            inverse_col = int(output_value[2:].to01(), 2)
            inverse_value = (row << 2) | col
            # Place the original input (encoded as (row << 2) | col) in the inverse position
            inverse_sbox[inverse_row][inverse_col] = (row << 2) | col
    
    return inverse_sbox

# Example usage for all S-boxes in SERPENT
inverse_sboxes_cobra = [invert_sbox(sbox) for sbox in sboxes_cobra]

# Apply given S-box to a 4-bit input
def apply_sbox(input, sbox):
     # Ensure input_bits is a 4-bit bitarray
    if len(input) != 4:
        raise ValueError("Input must be a 4-bit bitarray.")

    # Convert the first 2 bits to determine the row and the last 2 bits for the column
    row = int(input[:2].to01(), 2)  # First 2 bits as row
    col = int(input[2:].to01(), 2)  # Last 2 bits as column

     # Retrieve the output from the S-box
    output_value = sbox[row][col]
    # Convert the output value back to a 4-bit bitarray
    output_bits = bitarray(f"{output_value:04b}")
    
    return output_bits

# Function to calculate differential uniformity
def differential_uniformity(sbox):
    flat_sbox = [item for row in sbox for item in row]
    n = len(flat_sbox)
    max_diff_prob = 0
    diff_table = np.zeros((16, 16), dtype=int)
    
    for x in range(n):
        for dx in range(16):
            y1 = flat_sbox[x]
            y2 = flat_sbox[x ^ dx]
            dy = y1 ^ y2
            diff_table[dx][dy] += 1
            
    # Calculate probabilities
    for dx in range(1, 16):
        max_diff_prob = max(max_diff_prob, max(diff_table[dx]) / 16)
        
    return max_diff_prob

# Function to calculate linear approximation table
def linear_approximation_table(sbox):
    flat_sbox = [item for row in sbox for item in row]
    n = len(flat_sbox)
    lat = np.zeros((16, 16), dtype=int)
    
    for a in range(16):
        for b in range(16):
            count = 0
            for x in range(n):
                input_parity = bin(x & a).count("1") % 2
                output_parity = bin(flat_sbox[x] & b).count("1") % 2
                if input_parity == output_parity:
                    count += 1
            lat[a][b] = abs(count - 8)  # Offset by 8 for probability calculation
    
    # Calculate maximum linear probability
    max_lin_prob = max([lat[a][b] for a in range(1, 16) for b in range(1, 16)]) / 16.0
    return max_lin_prob

def has_duplicates(sbox):
    """Check if an S-box has any duplicate output values."""
    flat_sbox = [item for row in sbox for item in row]
    return len(set(flat_sbox)) != len(flat_sbox)


# Function to swap two values in the S-box
def swap_values(sbox, pos1, pos2):
    """Swap two values in a 2D S-box based on their positions."""
    (row1, col1), (row2, col2) = pos1, pos2
    sbox[row1][col1], sbox[row2][col2] = sbox[row2][col2], sbox[row1][col1]
    return sbox

def remove_duplicates(sbox):
    """Remove duplicate values in the S-box by swapping to ensure unique mappings."""
    flat_sbox = [item for row in sbox for item in row]
    unique_values = set(flat_sbox)
    
    # Find duplicate positions and missing values
    duplicates = [i for i, value in enumerate(flat_sbox) if flat_sbox.count(value) > 1]
    all_possible_values = set(range(16))
    missing_values = list(all_possible_values - unique_values)

    # Swap duplicates with missing values to ensure unique outputs
    for duplicate_index in duplicates:
        row, col = divmod(duplicate_index, 4)
        if missing_values:
            # Replace the duplicate with a missing value
            sbox[row][col] = missing_values.pop()
    return sbox

# Sample strategy one 
def sample_strategie(sbox):
    return [sbox[i // 4][i % 4 * 4] for i in range(16)]

# Attempt to find an S-box configuration that meets the criteria
def find_valid_sbox(sbox, max_attempts=1000):
    sbox = remove_duplicates(sbox)  # Ensure no duplicates initially
    best_sbox = sbox[:]
    best_diff_prob = differential_uniformity(best_sbox)
    best_lin_prob = linear_approximation_table(best_sbox)
    
    for attempt in range(max_attempts):
        # Randomly select two indices to swap within a 4x4 grid
        i, j = random.sample(range(4), 2)
        k, l = random.sample(range(4), 2)
        
        # Swap values and calculate new probabilities
        candidate_sbox = swap_values(best_sbox, (i, j), (k, l))
        candidate_sbox = remove_duplicates(candidate_sbox)  # Ensure unique values after swap
        diff_prob = differential_uniformity(candidate_sbox)
        lin_prob = linear_approximation_table(candidate_sbox)
        
        # Check if the new S-box meets the criteria
        if diff_prob <= 0.25 and 0.125 <= lin_prob <= 0.25:
            print(f"Found a valid S-box configuration after {attempt+1} attempts.")
            return candidate_sbox
        
        # Keep track of the best configuration
        if diff_prob < best_diff_prob or (diff_prob == best_diff_prob and lin_prob < best_lin_prob):
            best_sbox = candidate_sbox
            best_diff_prob = diff_prob
            best_lin_prob = lin_prob

    print("Could not find a valid configuration within the attempt limit. Returning the best attempt.")
    return best_sbox


def find_valid_sbox_using_sample_strategie(sbox, max_attempts=30):
    best_sbox = sbox[:]    
    for _ in range(max_attempts):
        sampled_sbox = sample_strategie(sbox)
        #2D array
        sampled_sbox = [sampled_sbox[i:i+4] for i in range(0, len(sampled_sbox), 4)]
        sampled_sbox = remove_duplicates(sampled_sbox)  # Ensure unique values
        best_sbox = find_valid_sbox(sampled_sbox)
        best_diff_prob = differential_uniformity(best_sbox)
        best_lin_prob = linear_approximation_table(best_sbox)
            
        if best_diff_prob <= 0.25 and 0.125 <= best_lin_prob <= 0.25:
            return best_sbox
    
    print("Could not find a valid configuration using any strategy. Returning the best attempt.")
    return best_sbox



def find_new_sboxes(sboxes_des) :
    sboxes_cobra = []
    for sbox in sboxes_des:
        optimized_sbox = find_valid_sbox_using_sample_strategie(sbox)
        print("Optimized S-box:", optimized_sbox)
        sboxes_cobra.append(optimized_sbox)
        print("Differential uniformity:", differential_uniformity(optimized_sbox))
        print("Linear approximation table:", linear_approximation_table(optimized_sbox))
        print()
    return sboxes_cobra

#if __name__ == "__main__":
    # Decomment the following line to find new S-boxes for COBRA
    #sboxes_cobra = find_new_sboxes(sboxes_des)
