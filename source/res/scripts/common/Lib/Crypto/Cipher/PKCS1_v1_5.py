# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/PKCS1_v1_5.py
__revision__ = '$Id$'
__all__ = ['new', 'PKCS115_Cipher']
from Crypto.Util.number import ceil_div
from Crypto.Util.py3compat import *
import Crypto.Util.number

class PKCS115_Cipher:

    def __init__(self, key):
        self._key = key

    def can_encrypt(self):
        return self._key.can_encrypt()

    def can_decrypt(self):
        return self._key.can_decrypt()

    def encrypt(self, message):
        randFunc = self._key._randfunc
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        mLen = len(message)
        if mLen > k - 11:
            raise ValueError('Plaintext is too long.')

        class nonZeroRandByte:

            def __init__(self, rf):
                self.rf = rf

            def __call__(self, c):
                while bord(c) == 0:
                    c = self.rf(1)[0]

                return c

        ps = tobytes(map(nonZeroRandByte(randFunc), randFunc(k - mLen - 3)))
        em = b('\x00\x02') + ps + bchr(0) + message
        m = self._key.encrypt(em, 0)[0]
        c = bchr(0) * (k - len(m)) + m
        return c

    def decrypt(self, ct, sentinel):
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        if len(ct) != k:
            raise ValueError('Ciphertext with incorrect length.')
        m = self._key.decrypt(ct)
        em = bchr(0) * (k - len(m)) + m
        sep = em.find(bchr(0), 2)
        return sentinel if not em.startswith(b('\x00\x02')) or sep < 10 else em[sep + 1:]


def new(key):
    return PKCS115_Cipher(key)
