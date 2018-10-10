# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/PublicKey/_DSA.py
__revision__ = '$Id$'
from Crypto.PublicKey.pubkey import *
from Crypto.Util import number
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Hash import SHA1
from Crypto.Util.py3compat import *

class error(Exception):
    pass


def generateQ(randfunc):
    S = randfunc(20)
    hash1 = SHA1.new(S).digest()
    hash2 = SHA1.new(long_to_bytes(bytes_to_long(S) + 1)).digest()
    q = bignum(0)
    for i in range(0, 20):
        c = bord(hash1[i]) ^ bord(hash2[i])
        if i == 0:
            c = c | 128
        if i == 19:
            c = c | 1
        q = q * 256 + c

    while not isPrime(q):
        q = q + 2

    if pow(2, 159L) < q < pow(2, 160L):
        return (S, q)
    raise RuntimeError('Bad q value generated')


def generate_py(bits, randfunc, progress_func=None):
    if bits < 160:
        raise ValueError('Key length < 160 bits')
    obj = DSAobj()
    if progress_func:
        progress_func('p,q\n')
    while 1:
        S, obj.q = generateQ(randfunc)
        n = divmod(bits - 1, 160)[0]
        C, N, V = 0, 2, {}
        b = obj.q >> 5 & 15
        powb = pow(bignum(2), b)
        powL1 = pow(bignum(2), bits - 1)
        while C < 4096:
            for k in range(0, n + 1):
                V[k] = bytes_to_long(SHA1.new(S + bstr(N) + bstr(k)).digest())

            W = V[n] % powb
            for k in range(n - 1, -1, -1):
                W = (W << 160L) + V[k]

            X = W + powL1
            p = X - (X % (2 * obj.q) - 1)
            if powL1 <= p and isPrime(p):
                break
            C, N = C + 1, N + n + 1

        if C < 4096:
            break
        if progress_func:
            progress_func('4096 multiples failed\n')

    obj.p = p
    power = divmod(p - 1, obj.q)[0]
    if progress_func:
        progress_func('h,g\n')
    while 1:
        h = bytes_to_long(randfunc(bits)) % (p - 1)
        g = pow(h, power, p)
        if 1 < h < p - 1 and g > 1:
            break

    obj.g = g
    if progress_func:
        progress_func('x,y\n')
    while 1:
        x = bytes_to_long(randfunc(20))
        if 0 < x < obj.q:
            break

    obj.x, obj.y = x, pow(g, x, p)
    return obj


class DSAobj:
    pass
