import os
import io
from datetime import datetime
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from bitarray import bitarray
from classes.User import User
from cobra.cobra import generate_key_128, encode_text, decode_text
from rsaEncrypt import encrypt_file_block, decrypt_file_block
from classes.Keys import Keys

def encode_file(public_key, request):
    # Validate request data
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    if "name" not in request.form:
        return jsonify({"error": "No name part"}), 400
    
    file = request.files["file"]
    name = request.form["name"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Define user directory
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], name, "data")
    os.makedirs(user_path, exist_ok=True)
    
    # Validate public key
    try:
        e, n = public_key
    except ValueError:
        return jsonify({"error": "Invalid public key format"}), 400

    # Read and encrypt the file
    encrypted_file_base64 = encrypt_file_block(file, n, e)
    # Save the encrypted data
    encrypted_file_path = os.path.join(user_path, f"{file.filename}")

    with open(encrypted_file_path, "w") as f:
        f.write(encrypted_file_base64)

    return jsonify({"message": "File uploaded and encrypted successfully!"}), 201

def send_file_back(file_name, user, private_key):
    # Define user directory
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user, "data")
    
    # Validate private key
    try:
        k, n = private_key
    except ValueError:
        raise ValueError("Invalid private key format")
    
    # Read the encrypted file
    encrypted_file_path = os.path.join(user_path, f"{file_name}")
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError(f"Encrypted file {file_name} not found")
    
    # Open the file
    with open(encrypted_file_path, "r") as file:
        try:
            decrypted_data = decrypt_file_block(file, n, k)
        except Exception as e:
            print(f"Decryption failed: {e}")
            raise

    # Return decrypted data
    return decrypted_data



app = Flask(__name__)
CORS(app,expose_headers=["PrivateKey"])  # Allow cross-origin requests from the React frontend

UPLOAD_FOLDER = "../users/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure upload folder exists
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
        user = User()
        keys = Keys()
        keys.d,keys.n = user.create(name, password)
        private_key = keys.write_private_key_format()
        return jsonify({"message": "User created successfully!", "private_key_pem": private_key}), 201
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
        user = User()
        success = user.login(name, password)
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

@app.route("/api/upload", methods=["POST"])
def upload_file():
    # read the public_key from the user logged in
    keys = Keys()
    keys.read_key(f"../users/{request.form['name']}/public_key.pem")
    result = encode_file((keys.e, keys.n), request)
    return result

@app.route('/api/files', methods=['GET'])
def get_files():
    user_name = request.headers.get("Authorization")    
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user_name, "data")
    
    if not os.path.exists(user_path):
        return jsonify({"error": "User files not found"}), 404
    
    files = []
    
    # Iterate through the files in the directory
    for file_name in os.listdir(user_path):
        file_path = os.path.join(user_path, file_name)
        
        # Ensure that we only include files (skip directories)
        if os.path.isfile(file_path):
            # Get the creation time (or last modification time)
            file_creation_time = os.path.getctime(file_path)  # Use getmtime if preferred
            
            # Convert the timestamp to a readable date string
            file_date_added = datetime.fromtimestamp(file_creation_time).isoformat()
            
            # Append the file details to the list
            files.append({
                "name": file_name,
                "dateAdded": file_date_added
            })
    
    return jsonify({"files": files}), 200


@app.route('/api/files/<file_name>', methods=['GET'])
def download_file(file_name):
    # Get the 'Authorization' header and extract the username
    user_name = request.headers.get('Authorization')
    privateKey = request.args.get('privateKey')
    keys = Keys()
    keys.decode_key(privateKey)
    if user_name is None:
        return jsonify({"error": "Authorization header missing"}), 400
    if not file_name:
        return jsonify({"error": "File name is required"}), 400
    if not keys.d:
        return jsonify({"error": "Valid private key is required"}), 400
    try:
        # TODO : read the private key from the user logged in (ask him to give the file ? how can I do this ?)
        decrypted_file = send_file_back(file_name, user_name, (keys.d, keys.n))
        decrypted_file = decrypted_file.replace('\x00', '')
        # Use io.BytesIO to create a file-like object in memory
        file_stream = io.BytesIO(decrypted_file.encode('utf-8'))
        file_stream.seek(0)  # Ensure the stream's pointer is at the beginning

        # Send the in-memory file to the user
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=file_name,  # Suggests the file name for download
            mimetype='application/octet-stream'  # Default binary MIME type
        )
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500
    

@app.route('/api/files/<file_name>', methods=['DELETE'])
def delete_file(file_name):
    user_name = request.headers.get("Authorization")
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user_name, "data")
    
    if not os.path.exists(user_path):
        return jsonify({"error": "User files not found"}), 404
    
    file_path = os.path.join(user_path, file_name)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)  # Remove the file
            return jsonify({"message": "File deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
    else:
        return jsonify({"error": "File not found"}), 404


if __name__ == '__main__':
    # Run the app on port 5000
    #Allow all origins for CORS, allow every computer to access the server
    app.run(port=5000, host='0.0.0.0')
