import json 
import time
from generateKeyPair import generate_key_pair, write_keys_to_file, read_key, int_to_bytes
import struct
import base64
from signature import sign_message, verify_signature

# create a new certificate authority (CA) and store the keys in a file
def create_certificate_authority():
    private_key, public_key = generate_key_pair(1024)
    write_keys_to_file("users", "CA", public_key, private_key)

class CA:
    def __init__(self):
        self.e, self.n = read_key("users/CA/public_key.pem")
        self.d, _ = read_key("users/CA/private_key.pem")
        self.v = pow(self.d, self.e, self.n)

    # Generate content of safe certificate
    def create_content_certificate_safe(self):
        pub_key_bytes = struct.pack(">I", len(int_to_bytes(self.e))) + int_to_bytes(self.e) + int_to_bytes(self.n)
        pub_key_base64 = base64.encodebytes(pub_key_bytes).decode('ascii')
        return {
            "name": "FileFort",
            "contact": "Luna Schenk",
            "organization": "FileFort&Co",
            "domain name": "filefort.com",
            "public_key": pub_key_base64,
            "issued": time.time(),
            "expiration": time.time() + 31536000
        }

    # Return a certificate with the content and a signature
    def create_certificate(content):
        key_data = read_key("users/CA/private_key.pem")
        content_dump = json.dumps(content)
        signature = sign_message(content_dump, key_data)
        return {
            "content" : content,
            "signature" : signature
        }

    # Verify a certificate signed by the CA
    def verify_certificate_by_CA(self, cert):
        content = cert["content"]
        signature = cert["signature"]
        key_data = (self.e, self.n)
        content_dump = json.dumps(content)
        return verify_signature(content_dump, signature, key_data)

    # create a certificate for FileFort
    def create_safe_certificate(self):
        content = self.create_content_certificate_safe()
        certificate = self.create_certificate(content)
        # write the JSON certificate to a file in users/Filefort/certificate.json
        with open("users/Filefort/certificate.json", "w") as file:
            json.dump(certificate, file, indent=4)
            return certificate

    # verify the certificate for FileFort
    def verify_safe_certificate(self):
        with open("users/Filefort/certificate.json", "r") as file:
            certificate = json.load(file)
            return self.verify_certificate_by_CA(certificate)
# test
if __name__ == "__main__":
    ca = CA()
    print(ca.verify_safe_certificate())
