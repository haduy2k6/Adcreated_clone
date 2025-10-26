import json, zlib, base64
from cryptography.fernet import Fernet
import os
from load_var import Config

fernet = Fernet(Config.FERNET_KEY.encode())

def compress_data(data: dict) -> str:
    """Nén dict thành chuỗi base64."""
    json_str = json.dumps(data, separators=(',', ':'))  # loại bỏ khoảng trắng
    compressed = zlib.compress(json_str.encode('utf-8'))
    return base64.b64encode(compressed).decode('utf-8')

def decompress_data(encoded: str) -> dict:
    """Giải nén lại dict ban đầu."""
    compressed = base64.b64decode(encoded.encode('utf-8'))
    json_str = zlib.decompress(compressed).decode('utf-8')
    return json.loads(json_str)

def encrypt( data : str):
    return fernet.encrypt(data.encode()).decode("utf-8")

def decrypt(encrypted : bytes):
   return fernet.decrypt(encrypted).decode()
