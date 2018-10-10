# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Protocol/KDF.py
__revision__ = '$Id$'
import math
import struct
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto.Hash import SHA1, HMAC, CMAC
from Crypto.Util.strxor import strxor
from Crypto.Util.number import long_to_bytes, bytes_to_long

def PBKDF1(password, salt, dkLen, count=1000, hashAlgo=None):
    if not hashAlgo:
        hashAlgo = SHA1
    password = tobytes(password)
    pHash = hashAlgo.new(password + salt)
    digest = pHash.digest_size
    if dkLen > digest:
        raise TypeError('Selected hash algorithm has a too short digest (%d bytes).' % digest)
    if len(salt) != 8:
        raise ValueError('Salt is not 8 bytes long.')
    for i in xrange(count - 1):
        pHash = pHash.new(pHash.digest())

    return pHash.digest()[:dkLen]


def PBKDF2(password, salt, dkLen=16, count=1000, prf=None):
    password = tobytes(password)
    if prf is None:
        prf = lambda p, s: HMAC.new(p, s, SHA1).digest()
    key = b('')
    i = 1
    while len(key) < dkLen:
        U = previousU = prf(password, salt + struct.pack('>I', i))
        for j in xrange(count - 1):
            previousU = t = prf(password, previousU)
            U = strxor(U, t)

        key += U
        i = i + 1

    return key[:dkLen]


class _S2V(object):

    def __init__(self, key, ciphermod):
        self._key = key
        self._ciphermod = ciphermod
        self._last_string = self._cache = bchr(0) * ciphermod.block_size
        self._n_updates = ciphermod.block_size * 8 - 1

    def new(key, ciphermod):
        return _S2V(key, ciphermod)

    new = staticmethod(new)

    def _double(self, bs):
        doubled = bytes_to_long(bs) << 1
        if bord(bs[0]) & 128:
            doubled ^= 135
        return long_to_bytes(doubled, len(bs))[-len(bs):]

    def update(self, item):
        if not item:
            raise ValueError('A component cannot be empty')
        if self._n_updates == 0:
            raise TypeError('Too many components passed to S2V')
        self._n_updates -= 1
        mac = CMAC.new(self._key, msg=self._last_string, ciphermod=self._ciphermod)
        self._cache = strxor(self._double(self._cache), mac.digest())
        self._last_string = item

    def derive(self):
        if len(self._last_string) >= 16:
            final = self._last_string[:-16] + strxor(self._last_string[-16:], self._cache)
        else:
            padded = (self._last_string + bchr(128) + bchr(0) * 15)[:16]
            final = strxor(padded, self._double(self._cache))
        mac = CMAC.new(self._key, msg=final, ciphermod=self._ciphermod)
        return mac.digest()
