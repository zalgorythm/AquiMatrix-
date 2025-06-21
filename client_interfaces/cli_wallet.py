import os
import json
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from cryptography.exceptions import InvalidSignature

WALLET_DIR = os.path.expanduser("~/.aquimatrix_wallet")
KEY_FILE = os.path.join(WALLET_DIR, "private_key.pem")
PUBKEY_FILE = os.path.join(WALLET_DIR, "public_key.pem")

def create_wallet():
    if not os.path.exists(WALLET_DIR):
        os.makedirs(WALLET_DIR)
    private_key = ec.generate_private_key(ec.SECP256K1())
    with open(KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    public_key = private_key.public_key()
    with open(PUBKEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    print(f"Wallet created. Keys saved in {WALLET_DIR}")

def load_private_key():
    if not os.path.exists(KEY_FILE):
        raise FileNotFoundError("Wallet not found. Please create a wallet first.")
    with open(KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    return private_key

def load_public_key():
    if not os.path.exists(PUBKEY_FILE):
        raise FileNotFoundError("Wallet not found. Please create a wallet first.")
    with open(PUBKEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    return public_key

def sign_message(message: bytes) -> bytes:
    private_key = load_private_key()
    signature = private_key.sign(message, ec.ECDSA(hashes.SHA256()))
    return signature

def verify_signature(public_key, message: bytes, signature: bytes) -> bool:
    try:
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False

def get_public_key_hex() -> str:
    public_key = load_public_key()
    pub_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return pub_bytes.hex()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="AquiMatrix Wallet CLI")
    parser.add_argument("command", choices=["create-wallet", "show-pubkey"], help="Command to execute")
    args = parser.parse_args()

    if args.command == "create-wallet":
        create_wallet()
    elif args.command == "show-pubkey":
        try:
            pubkey_hex = get_public_key_hex()
            print(f"Public Key (hex): {pubkey_hex}")
        except FileNotFoundError as e:
            print(str(e))
