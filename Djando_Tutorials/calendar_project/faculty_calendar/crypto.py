import base64
import hashlib

from cryptography.fernet import Fernet
from django.conf import settings


def _cipher():
    key = hashlib.sha256(settings.PUSH_ENCRYPTION_KEY.encode('utf-8')).digest()
    return Fernet(base64.urlsafe_b64encode(key))


def encrypt(value):
    return _cipher().encrypt(value.encode('utf-8')).decode('ascii')


def decrypt(value):
    return _cipher().decrypt(value.encode('ascii')).decode('utf-8')
