# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/PKCS1_OAEP.py
from __future__ import nested_scopes
__revision__ = '$Id$'
__all__ = ['new', 'PKCS1OAEP_Cipher']
import Crypto.Signature.PKCS1_PSS
import Crypto.Hash.SHA1
from Crypto.Util.py3compat import *
import Crypto.Util.number
from Crypto.Util.number import ceil_div
from Crypto.Util.strxor import strxor

class PKCS1OAEP_Cipher:

    def __init__(self, key, hashAlgo, mgfunc, label):
        self._key = key
        if hashAlgo:
            self._hashObj = hashAlgo
        else:
            self._hashObj = Crypto.Hash.SHA1
        if mgfunc:
            self._mgf = mgfunc
        else:
            self._mgf = lambda x, y: Crypto.Signature.PKCS1_PSS.MGF1(x, y, self._hashObj)
        self._label = label

    def can_encrypt(self):
        return self._key.can_encrypt()

    def can_decrypt(self):
        return self._key.can_decrypt()

    def encrypt(self, message):
        randFunc = self._key._randfunc
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        hLen = self._hashObj.digest_size
        mLen = len(message)
        ps_len = k - mLen - 2 * hLen - 2
        if ps_len < 0:
            raise ValueError('Plaintext is too long.')
        lHash = self._hashObj.new(self._label).digest()
        ps = bchr(0) * ps_len
        db = lHash + ps + bchr(1) + message
        ros = randFunc(hLen)
        dbMask = self._mgf(ros, k - hLen - 1)
        maskedDB = strxor(db, dbMask)
        seedMask = self._mgf(maskedDB, hLen)
        maskedSeed = strxor(ros, seedMask)
        em = bchr(0) + maskedSeed + maskedDB
        m = self._key.encrypt(em, 0)[0]
        c = bchr(0) * (k - len(m)) + m
        return c

    def decrypt(self, ct):
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        hLen = self._hashObj.digest_size
        if len(ct) != k or k < hLen + 2:
            raise ValueError('Ciphertext with incorrect length.')
        m = self._key.decrypt(ct)
        em = bchr(0) * (k - len(m)) + m
        lHash = self._hashObj.new(self._label).digest()
        y = em[0]
        maskedSeed = em[1:hLen + 1]
        maskedDB = em[hLen + 1:]
        seedMask = self._mgf(maskedDB, hLen)
        seed = strxor(maskedSeed, seedMask)
        dbMask = self._mgf(seed, k - hLen - 1)
        db = strxor(maskedDB, dbMask)
        valid = 1
        one = db[hLen:].find(bchr(1))
        lHash1 = db[:hLen]
        if lHash1 != lHash:
            valid = 0
        if one < 0:
            valid = 0
        if bord(y) != 0:
            valid = 0
        if not valid:
            raise ValueError('Incorrect decryption.')
        return db[hLen + one + 1:]


def new(key, hashAlgo=None, mgfunc=None, label=b('')):
    return PKCS1OAEP_Cipher(key, hashAlgo, mgfunc, label)
