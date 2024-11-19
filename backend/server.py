import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from bitarray import bitarray
from user_functions import create_user, login_user
from cobra import generate_key_128, encode_text, decode_text

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from the React frontend


@app.route('/api/create_user', methods=['POST'])
def api_create_user():
    # Extract data from the request
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    # Validate input
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400
    # Check if the name is already taken
    if name in os.listdir('../users'):
        return jsonify({"error": "Username already exists"}), 400
    # Check if the password is at least 8 characters long and contains a digit
    if len(password) < 8 or not any(char.isdigit() for char in password):
        return jsonify({"error": "Password must be at least 8 characters long and contain a digit"}), 400
    try:
        # Call the create_user function
        create_user(name, password)
        return jsonify({"message": "User created successfully!"}), 201
    except Exception as e:
        if 'WinError 183' in str(e):
            return jsonify({"error": "Username already exists"}), 400
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/login_user', methods=['POST'])
def api_login_user():
    # Extract data from the request
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    # Validate input
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400

    try:
        # Call the login_user function
        success = login_user(name, password)
        if success:
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Login failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_key_128', methods=['GET'])
def api_generate_key_128():
    try:
        # Call the generate_key_128 function
        key = generate_key_128()
        # Convert bitarray to hex string
        key = key.tobytes().hex()
        return jsonify({"key": key}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/encode_text', methods=['POST'])
def api_encode_text():
    # Extract data from the request
    data = request.get_json()
    text = data.get('text')
    key = data.get('key')
    # Validate input
    if not text and not key:
        return jsonify({"error": "Text and key are required"}), 400
    # Convert hex string to bitarray
    bin_key = bitarray()
    bin_key.frombytes(bytes.fromhex(key))
    # Check key length (128 bits)
    if len(bin_key) != 128:
        return jsonify({"error": "Invalid key length"}), 400
    try:
        # Call the encode_text function
        encoded_text = encode_text(text, bin_key)
        return jsonify({"encoded_text": encoded_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/api/decode_text', methods=['POST'])
def api_decode_text():
    # Extract data from the request
    data = request.get_json()
    text = data.get('text')
    key = data.get('key')
    # Validate input
    if not text and not key:
        return jsonify({"error": "Text and key are required"}), 400
    # Convert hex string to bitarray
    bin_key = bitarray()
    bin_key.frombytes(bytes.fromhex(key))
    # Check key length (128 bits)
    if len(bin_key) != 128:
        return jsonify({"error": "Invalid key length"}), 400
    try:
        # Call the decode_text function
        decoded_text = decode_text(text, bin_key)
        return jsonify({"decoded_text": decoded_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the app on port 5000
    app.run(debug=True)
