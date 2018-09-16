# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/ARC4.py
__revision__ = '$Id$'
from Crypto.Util.py3compat import *
from Crypto.Cipher import _ARC4

class ARC4Cipher:

    def __init__(self, key, *args, **kwargs):
        if len(args) > 0:
            ndrop = args[0]
            args = args[1:]
        else:
            ndrop = kwargs.get('drop', 0)
            if ndrop:
                del kwargs['drop']
        self._cipher = _ARC4.new(key, *args, **kwargs)
        if ndrop:
            self._cipher.encrypt(b('\x00') * ndrop)
        self.block_size = self._cipher.block_size
        self.key_size = self._cipher.key_size

    def encrypt(self, plaintext):
        return self._cipher.encrypt(plaintext)

    def decrypt(self, ciphertext):
        return self._cipher.decrypt(ciphertext)


def new(key, *args, **kwargs):
    return ARC4Cipher(key, *args, **kwargs)


block_size = 1
key_size = xrange(1, 257)
