import json 
from hashlib import sha256
import time
from generate_key_pair import generate_key_pair, write_keys_to_file, read_key

# create a new certificate authority (CA) and store the keys in a file
def create_certificate_authority():
    private_key, public_key = generate_key_pair(1024)
    write_keys_to_file("CA", "", public_key, private_key)

# sign a certificate with the CA's private key
def sign_certificate(certificate_content):
    hashed_content = sha256(certificate_content.encode()).hexdigest() # est-ce qu'on a le droit de faire ça ?
    key_data = read_key("CA/private_key.pem")
    #sign the certificate
    signature = "je sais pas comment faire"
    # TODO: à finir quand on aura vu le cours sur les signatures lol
    return signature

# create a certificate 
def create_certificate(safe):
    content = json.dumps(safe)
    signature = sign_certificate(content)
    return {
        "content" : content,
        "signature" : signature
    }

def create_content_certificate_safe():
    return json.dumps({
        "name" : "Safe",
        "is_safe" : True,
        "issued" : time.time(),
        "expiration" : time.time() + 3600
    })
