# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/PublicKey/ElGamal.py
__revision__ = '$Id$'
__all__ = ['generate',
 'construct',
 'error',
 'ElGamalobj']
from Crypto.PublicKey.pubkey import *
from Crypto.Util import number
from Crypto import Random

class error(Exception):
    pass


def generate(bits, randfunc, progress_func=None):
    obj = ElGamalobj()
    if progress_func:
        progress_func('p\n')
    while 1:
        q = bignum(getPrime(bits - 1, randfunc))
        obj.p = 2 * q + 1
        if number.isPrime(obj.p, randfunc=randfunc):
            break

    if progress_func:
        progress_func('g\n')
    while 1:
        obj.g = number.getRandomRange(3, obj.p, randfunc)
        safe = 1
        if pow(obj.g, 2, obj.p) == 1:
            safe = 0
        if safe and pow(obj.g, q, obj.p) == 1:
            safe = 0
        if safe and divmod(obj.p - 1, obj.g)[1] == 0:
            safe = 0
        ginv = number.inverse(obj.g, obj.p)
        if safe and divmod(obj.p - 1, ginv)[1] == 0:
            safe = 0
        if safe:
            break

    if progress_func:
        progress_func('x\n')
    obj.x = number.getRandomRange(2, obj.p - 1, randfunc)
    if progress_func:
        progress_func('y\n')
    obj.y = pow(obj.g, obj.x, obj.p)
    return obj


def construct(tup):
    obj = ElGamalobj()
    if len(tup) not in (3, 4):
        raise ValueError('argument for construct() wrong length')
    for i in range(len(tup)):
        field = obj.keydata[i]
        setattr(obj, field, tup[i])

    return obj


class ElGamalobj(pubkey):
    keydata = ['p',
     'g',
     'y',
     'x']

    def __init__(self, randfunc=None):
        if randfunc is None:
            randfunc = Random.new().read
        self._randfunc = randfunc
        return

    def encrypt(self, plaintext, K):
        return pubkey.encrypt(self, plaintext, K)

    def decrypt(self, ciphertext):
        return pubkey.decrypt(self, ciphertext)

    def sign(self, M, K):
        return pubkey.sign(self, M, K)

    def verify(self, M, signature):
        return pubkey.verify(self, M, signature)

    def _encrypt(self, M, K):
        a = pow(self.g, K, self.p)
        b = M * pow(self.y, K, self.p) % self.p
        return (a, b)

    def _decrypt(self, M):
        if not hasattr(self, 'x'):
            raise TypeError('Private key not available in this object')
        r = number.getRandomRange(2, self.p - 1, self._randfunc)
        a_blind = M[0] * pow(self.g, r, self.p) % self.p
        ax = pow(a_blind, self.x, self.p)
        plaintext_blind = M[1] * inverse(ax, self.p) % self.p
        plaintext = plaintext_blind * pow(self.y, r, self.p) % self.p
        return plaintext

    def _sign(self, M, K):
        if not hasattr(self, 'x'):
            raise TypeError('Private key not available in this object')
        p1 = self.p - 1
        if GCD(K, p1) != 1:
            raise ValueError('Bad K value: GCD(K,p-1)!=1')
        a = pow(self.g, K, self.p)
        t = (M - self.x * a) % p1
        while t < 0:
            t = t + p1

        b = t * inverse(K, p1) % p1
        return (a, b)

    def _verify(self, M, sig):
        if sig[0] < 1 or sig[0] > self.p - 1:
            return 0
        v1 = pow(self.y, sig[0], self.p)
        v1 = v1 * pow(sig[0], sig[1], self.p) % self.p
        v2 = pow(self.g, M, self.p)
        return 1 if v1 == v2 else 0

    def size(self):
        return number.size(self.p) - 1

    def has_private(self):
        if hasattr(self, 'x'):
            return 1
        else:
            return 0

    def publickey(self):
        return construct((self.p, self.g, self.y))


object = ElGamalobj
