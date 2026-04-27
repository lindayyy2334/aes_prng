from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import hashlib
import os


class AES_DRBG:
    def __init__(self):
        self.key = get_random_bytes(16)
        self.V = int.from_bytes(get_random_bytes(4), 'big')
        self.reseed_counter = 0
        self.UID = self._generate_uid()

    def _generate_uid(self):
        return hashlib.sha256(os.urandom(32)).digest()[:12]

    def _aes(self, block):
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.encrypt(block)

    def _expand(self, v):
        return v.to_bytes(4, 'big') * 4

    def _update(self):
        self.V = (self.V + 1) & 0xFFFFFFFF
        block = self.V.to_bytes(4, 'big') + self.UID
        self.V = int.from_bytes(self._aes(block)[:4], 'big')

    def generate(self, length=8):
        out = self._aes(self._expand(self.V))
        self._update()
        self.reseed_counter += 1
        return out[:length]

    def reseed(self):
        self.key = get_random_bytes(16)
        self.V = int.from_bytes(get_random_bytes(4), 'big')
        self.UID = self._generate_uid()
        self.reseed_counter = 0
