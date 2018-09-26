import hashlib

from dht import settings


def hash_string(value):
    return hashlib.sha512(str.encode(value)).hexdigest()


def hex_to_bin(value):
    return bin(int(value, 16))[2:].zfill(settings.KEY_SIZE)
