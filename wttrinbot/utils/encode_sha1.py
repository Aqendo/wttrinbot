import hashlib


def encode_sha1(text: str):
    sha1 = hashlib.sha1()
    sha1.update(text.encode())
    return sha1.hexdigest()
