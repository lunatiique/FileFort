import os
import io
from datetime import datetime
from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
from bitarray import bitarray
from classes.User import User
from cobra.cobra import generate_key_128, encode_text, decode_text
from rsaEncrypt import encrypt_file_block, decrypt_file_block
from classes.Keys import Keys
from classes.CoffreFort import CoffreFort
from classes.CA import CA
from simulateCommunication import verify_safe_certificate, authenticate_user_to_safe, perform_key_exchange, send_message_to_safe, receive_message_from_user, send_message_to_user, receive_message_from_safe

# Fonction pour encoder un fichier avec une clé publique
def encode_file(public_key, request):
    # Valider les données de la requête
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    if "name" not in request.form:
        return jsonify({"error": "No name part"}), 400
    
    file = request.files["file"]
    name = request.form["name"]
    
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Définir le répertoire de l'utilisateur
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], name, "data")
    os.makedirs(user_path, exist_ok=True)
    
    # Valider la clé publique
    try:
        e, n = public_key
    except ValueError:
        return jsonify({"error": "Invalid public key format"}), 400

    # Lire et chiffrer le fichier
    encrypted_file_base64 = encrypt_file_block(file, n, e)
    # Sauvegarder les données chiffrées
    encrypted_file_path = os.path.join(user_path, f"{file.filename}")

    with open(encrypted_file_path, "w") as f:
        f.write(encrypted_file_base64)

    return jsonify({"message": "File uploaded and encrypted successfully!"}), 201

# Fonction pour envoyer un fichier déchiffré à l'utilisateur
def send_file_back(file_name, user, private_key):
    # Définir le répertoire de l'utilisateur
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user, "data")
    
    # Valider la clé privée
    try:
        k, n = private_key
    except ValueError:
        raise ValueError("Invalid private key format")
    
    # Lire le fichier chiffré
    encrypted_file_path = os.path.join(user_path, f"{file_name}")
    if not os.path.exists(encrypted_file_path):
        raise FileNotFoundError(f"Encrypted file {file_name} not found")
    
    # Ouvrir le fichier
    with open(encrypted_file_path, "r") as file:
        try:
            decrypted_data = decrypt_file_block(file, n, k)
        except Exception as e:
            print(f"Decryption failed: {e}")
            raise

    # Retourner les données déchiffrées
    return decrypted_data

app = Flask(__name__)
CORS(app)  # Autoriser les requêtes cross-origin depuis le frontend React

UPLOAD_FOLDER = "../users/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # S'assurer que le dossier de téléchargement existe
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Route pour créer un utilisateur
@app.route('/api/create_user', methods=['POST'])
def api_create_user():
    # Extraire les données de la requête
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')

    # Valider les entrées
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400
    # Vérifier si le nom est déjà pris
    if name in os.listdir('../users'):
        return jsonify({"error": "Username already exists"}), 400
    # Vérifier si le mot de passe a au moins 8 caractères et contient un chiffre
    if len(password) < 8 or not any(char.isdigit() for char in password):
        return jsonify({"error": "Password must be at least 8 characters long and contain a digit"}), 400
    try:
        # Appeler la fonction create_user
        user = User()
        keys = Keys()
        keys.d, keys.n = user.create(name, password)
        return jsonify({"message": "User created successfully!", "private_key_pem": private_key}), 201
    except Exception as e:
        if 'WinError 183' in str(e):
            return jsonify({"error": "Username already exists"}), 400
        return jsonify({"error": str(e)}), 500

# Route pour connecter un utilisateur
@app.route('/api/login_user', methods=['POST'])
def api_login_user():
    # Extraire les données de la requête
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    privateKey_encoded = data.get('privateKey')  # Pour simplifier le projet, normalement les calculs de ZPK se font côté client
    # Valider les entrées
    if not name or not password:
        return jsonify({"error": "Name and password are required"}), 400

    try:
        # Décoder la clé privée
        privateKey = Keys()
        privateKey.decode_key(privateKey_encoded)
        # Appeler la fonction login_user
        user = User()
        success = user.login(name, password, privateKey)
        if success:
            return jsonify({"message": "Login successful!"}), 200
        else:
            return jsonify({"error": "Login failed"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour générer une clé de 128 bits
@app.route('/api/generate_key_128', methods=['GET'])
def api_generate_key_128():
    try:
        # Appeler la fonction generate_key_128
        key = generate_key_128()
        # Convertir bitarray en chaîne hexadécimale
        key = key.tobytes().hex()
        return jsonify({"key": key}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour encoder un texte
@app.route('/api/encode_text', methods=['POST'])
def api_encode_text():
    # Extraire les données de la requête
    data = request.get_json()
    text = data.get('text')
    key = data.get('key')
    # Valider les entrées
    if not text and not key:
        return jsonify({"error": "Text and key are required"}), 400
    # Convertir la chaîne hexadécimale en bitarray
    bin_key = bitarray()
    bin_key.frombytes(bytes.fromhex(key))
    # Vérifier la longueur de la clé (128 bits)
    if len(bin_key) != 128:
        return jsonify({"error": "Invalid key length"}), 400
    try:
        # Appeler la fonction encode_text
        encoded_text = encode_text(text, bin_key)
        return jsonify({"encoded_text": encoded_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour décoder un texte
@app.route('/api/decode_text', methods=['POST'])
def api_decode_text():
    # Extraire les données de la requête
    data = request.get_json()
    text = data.get('text')
    key = data.get('key')
    # Valider les entrées
    if not text and not key:
        return jsonify({"error": "Text and key are required"}), 400
    # Convertir la chaîne hexadécimale en bitarray
    bin_key = bitarray()
    bin_key.frombytes(bytes.fromhex(key))
    # Vérifier la longueur de la clé (128 bits)
    if len(bin_key) != 128:
        return jsonify({"error": "Invalid key length"}), 400
    try:
        # Appeler la fonction decode_text
        decoded_text = decode_text(text, bin_key)
        return jsonify({"decoded_text": decoded_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route pour télécharger un fichier
@app.route("/api/upload", methods=["POST"])
def upload_file():
    # Lire la clé publique de l'utilisateur connecté
    keys = Keys()
    keys.read_key(f"../users/{request.form['name']}/public_key.pem")
    result = encode_file((keys.e, keys.n), request)
    return result

# Route pour obtenir la liste des fichiers d'un utilisateur
@app.route('/api/files', methods=['GET'])
def get_files():
    user_name = request.headers.get("Authorization")    
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user_name, "data")
    
    if not os.path.exists(user_path):
        return jsonify({"error": "User files not found"}), 404
    
    files = []
    
    # Itérer à travers les fichiers dans le répertoire
    for file_name in os.listdir(user_path):
        file_path = os.path.join(user_path, file_name)
        
        # S'assurer que nous incluons uniquement les fichiers (ignorer les répertoires)
        if os.path.isfile(file_path):
            # Obtenir le temps de création (ou le dernier temps de modification)
            file_creation_time = os.path.getctime(file_path)  # Utiliser getmtime si préféré
            
            # Convertir le timestamp en chaîne de date lisible
            file_date_added = datetime.fromtimestamp(file_creation_time).isoformat()
            
            # Ajouter les détails du fichier à la liste
            files.append({
                "name": file_name,
                "dateAdded": file_date_added
            })
    
    return jsonify({"files": files}), 200

# Route pour télécharger un fichier déchiffré
@app.route('/api/files/<file_name>', methods=['GET'])
def download_file(file_name):
    # Obtenir l'en-tête 'Authorization' et extraire le nom d'utilisateur
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
        # TODO : lire la clé privée de l'utilisateur connecté (lui demander de fournir le fichier ? comment puis-je faire cela ?)
        decrypted_file = send_file_back(file_name, user_name, (keys.d, keys.n))
        decrypted_file = decrypted_file.replace('\x00', '')
        # Utiliser io.BytesIO pour créer un objet fichier en mémoire
        file_stream = io.BytesIO(decrypted_file.encode('utf-8'))
        file_stream.seek(0)  # S'assurer que le pointeur du flux est au début

        # Envoyer le fichier en mémoire à l'utilisateur
        return send_file(
            file_stream,
            as_attachment=True,
            download_name=file_name,  # Suggérer le nom du fichier pour le téléchargement
            mimetype='application/octet-stream'  # Type MIME binaire par défaut
        )
    except Exception as e:
        return jsonify({"error": f"Failed to process file: {str(e)}"}), 500

# Route pour supprimer un fichier
@app.route('/api/files/<file_name>', methods=['DELETE'])
def delete_file(file_name):
    user_name = request.headers.get("Authorization")
    user_path = os.path.join(app.config["UPLOAD_FOLDER"], user_name, "data")
    
    if not os.path.exists(user_path):
        return jsonify({"error": "User files not found"}), 404
    
    file_path = os.path.join(user_path, file_name)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)  # Supprimer le fichier
            return jsonify({"message": "File deleted successfully"}), 200
        except Exception as e:
            return jsonify({"error": f"Failed to delete file: {str(e)}"}), 500
    else:
        return jsonify({"error": "File not found"}), 404

# Route pour simuler une communication sécurisée
@app.route('/api/simulation', methods=['GET'])
def simulate_communication():
    def event_stream():
        # Initialiser CA, Utilisateur et Coffre Fort
        ca = CA()
        user = User()
        private_key = Keys()
        private_key.read_key("../users/luna/luna_private_key.pem")
        # Pour simplifier le projet, on connecte l'utilisateur automatiquement (c'est une simulation)
        user.login("luna", "blabla13", private_key)
        safe = CoffreFort()
        # Étape 1: Vérifier le certificat du coffre fort
        yield f"data: Etape 1 : Vérification du certificat du coffre fort...\n\n"
        verify_safe_certificate(ca)
        yield f"data: Certificat du coffre fort vérifié.\n\n"
        # Étape 2: Authentifier l'utilisateur auprès du coffre fort
        yield f"data: Etape 2 : Authentification de l'utilisateur auprès du coffre fort...(Guillou-Quisquater)\n\n"
        authenticate_user_to_safe(user, safe)
        yield f"data: Utilisateur authentifié auprès du coffre fort.\n\n"
        # Étape 3: Échange de clés
        yield f"data: Etape 3 : Echange de clés...(Diffie-Hellman)\n\n"
        key = perform_key_exchange(user, safe)
        if key == 1:
            yield f"data: Échec de l'échange de clés : les secrets partagés ne correspondent pas. Abandon.\n\n"
            return
        yield f"data: Secret partagé établi : {key}.\n\n"
        # Étape 4: Communication sécurisée
        yield f"data: Etape 4 : Communication sécurisée...(COBRA)\n\n"
        encrypted, hmac = send_message_to_safe(user)
        yield f"data: L'utilisateur envoie un message au coffre-fort.\n\n"
        yield f"data: Message chiffré : {encrypted}.\n\n"
        yield f"data: HMAC : {hmac}.\n\n"
        decrypted = receive_message_from_user(safe, encrypted, hmac)
        yield f"data: Le coffre-fort reçoit le message de l'utilisateur.\n\n"
        if decrypted == 1:
            yield f"data: Échec de la vérification du HMAC : la communication est compromise.\n\n"
            return
        yield f"data: Message reçu par le coffre fort : {decrypted}.\n\n"
        encrypted, hmac = send_message_to_user(safe)
        yield f"data: Le coffre-fort envoie un message à l'utilisateur.\n\n"
        yield f"data: Message chiffré : {encrypted}.\n\n"
        yield f"data: HMAC : {hmac}.\n\n"
        decrypted = receive_message_from_safe(user, encrypted, hmac)
        yield f"data: L'utilisateur reçoit le message du coffre fort.\n\n"
        if decrypted == 1:
            yield f"data: Échec de la vérification du HMAC : la communication est compromise.\n\n"
            return
        yield f"data: Message reçu par l'utilisateur : {decrypted}.\n\n"
        yield f"data: Fin de la communication sécurisée.\n\n"

    return Response(event_stream(), content_type='text/event-stream')

if __name__ == '__main__':
    # Exécuter l'application sur le port 5000
    # Autoriser toutes les origines pour CORS, permettre à chaque ordinateur d'accéder au serveur
    app.run(port=5000, host='0.0.0.0')
