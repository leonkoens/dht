import hashlib
from settings import KEY_SIZE


def hash_string(value):
    return hashlib.sha512(str.encode(value)).hexdigest()


def hex_to_bin(value):
    return bin(int(value, 16))[2:].zfill(KEY_SIZE)
