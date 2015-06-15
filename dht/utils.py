import hashlib


def hash_string(value):
    return hashlib.sha512(str.encode(value)).hexdigest()
