# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Signature/PKCS1_PSS.py
from __future__ import nested_scopes
__revision__ = '$Id$'
__all__ = ['new', 'PSS_SigScheme']
from Crypto.Util.py3compat import *
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
import Crypto.Util.number
from Crypto.Util.number import ceil_shift, ceil_div, long_to_bytes
from Crypto.Util.strxor import strxor
from Crypto.Hash import new as Hash_new

class PSS_SigScheme:

    def __init__(self, key, mgfunc, saltLen):
        self._key = key
        self._saltLen = saltLen
        self._mgfunc = mgfunc

    def can_sign(self):
        return self._key.has_private()

    def sign(self, mhash):
        randfunc = self._key._randfunc
        if self._saltLen == None:
            sLen = mhash.digest_size
        else:
            sLen = self._saltLen
        if self._mgfunc:
            mgf = self._mgfunc
        else:
            mgf = lambda x, y: MGF1(x, y, mhash)
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        em = EMSA_PSS_ENCODE(mhash, modBits - 1, randfunc, mgf, sLen)
        m = self._key.decrypt(em)
        S = bchr(0) * (k - len(m)) + m
        return S

    def verify(self, mhash, S):
        if self._saltLen == None:
            sLen = mhash.digest_size
        else:
            sLen = self._saltLen
        if self._mgfunc:
            mgf = self._mgfunc
        else:
            mgf = lambda x, y: MGF1(x, y, mhash)
        modBits = Crypto.Util.number.size(self._key.n)
        k = ceil_div(modBits, 8)
        if len(S) != k:
            return False
        else:
            em = self._key.encrypt(S, 0)[0]
            emLen = ceil_div(modBits - 1, 8)
            em = bchr(0) * (emLen - len(em)) + em
            try:
                result = EMSA_PSS_VERIFY(mhash, em, modBits - 1, mgf, sLen)
            except ValueError:
                return False

            return result


def MGF1(mgfSeed, maskLen, hash):
    T = b('')
    for counter in xrange(ceil_div(maskLen, hash.digest_size)):
        c = long_to_bytes(counter, 4)
        try:
            T = T + hash.new(mgfSeed + c).digest()
        except AttributeError:
            T = T + Hash_new(hash, mgfSeed + c).digest()

    return T[:maskLen]


def EMSA_PSS_ENCODE(mhash, emBits, randFunc, mgf, sLen):
    emLen = ceil_div(emBits, 8)
    lmask = 0
    for i in xrange(8 * emLen - emBits):
        lmask = lmask >> 1 | 128

    if emLen < mhash.digest_size + sLen + 2:
        raise ValueError('Digest or salt length are too long for given key size.')
    salt = b('')
    if randFunc and sLen > 0:
        salt = randFunc(sLen)
    try:
        h = mhash.new(bchr(0) * 8 + mhash.digest() + salt)
    except AttributeError:
        h = Hash_new(mhash, bchr(0) * 8 + mhash.digest() + salt)

    db = bchr(0) * (emLen - sLen - mhash.digest_size - 2) + bchr(1) + salt
    dbMask = mgf(h.digest(), emLen - mhash.digest_size - 1)
    maskedDB = strxor(db, dbMask)
    maskedDB = bchr(bord(maskedDB[0]) & ~lmask) + maskedDB[1:]
    em = maskedDB + h.digest() + bchr(188)
    return em


def EMSA_PSS_VERIFY(mhash, em, emBits, mgf, sLen):
    emLen = ceil_div(emBits, 8)
    lmask = 0
    for i in xrange(8 * emLen - emBits):
        lmask = lmask >> 1 | 128

    if emLen < mhash.digest_size + sLen + 2:
        return False
    if ord(em[-1:]) != 188:
        return False
    maskedDB = em[:emLen - mhash.digest_size - 1]
    h = em[emLen - mhash.digest_size - 1:-1]
    if lmask & bord(em[0]):
        return False
    dbMask = mgf(h, emLen - mhash.digest_size - 1)
    db = strxor(maskedDB, dbMask)
    db = bchr(bord(db[0]) & ~lmask) + db[1:]
    if not db.startswith(bchr(0) * (emLen - mhash.digest_size - sLen - 2) + bchr(1)):
        return False
    salt = b('')
    if sLen:
        salt = db[-sLen:]
    try:
        hp = mhash.new(bchr(0) * 8 + mhash.digest() + salt).digest()
    except AttributeError:
        hp = Hash_new(mhash, bchr(0) * 8 + mhash.digest() + salt).digest()

    return False if h != hp else True


def new(key, mgfunc=None, saltLen=None):
    return PSS_SigScheme(key, mgfunc, saltLen)
