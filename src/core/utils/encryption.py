import base64
import json

from pathlib import Path

from cryptography.hazmat.primitives import serialization

def get_private_key():
    with Path.open("keys/key.pem", "rb") as file:
        return serialization.load_pem_private_key(file.read(), password=None)
        

def decrypt_data(data: str) -> dict:
    """
    Decrypt data with private key on server.
    """
    private_key = get_private_key()

    data = base64.b64decode(data.encode())
    data = private_key.decrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    data_str = data.decode()
    return json.loads(data_str)
