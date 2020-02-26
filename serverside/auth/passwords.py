import binascii
import os
from django.contrib.auth.hashers import check_password, make_password


def generate_hashed_password(password: str) -> str:
    return make_password(password=password, salt=binascii.hexlify(os.urandom(20)).decode(), hasher="argon2")


def validate_password(password: str, hashed_password: str) -> bool:
    return check_password(password, hashed_password)
