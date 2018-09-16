# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/PublicKey/RSA.py
__revision__ = '$Id$'
__all__ = ['generate',
 'construct',
 'error',
 'importKey',
 'RSAImplementation',
 '_RSAobj',
 'oid',
 'algorithmIdentifier']
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto.Util.number import getRandomRange, bytes_to_long, long_to_bytes
from Crypto.PublicKey import _RSA, _slowmath, pubkey
from Crypto.IO import PKCS8, PEM
from Crypto import Random
from Crypto.Util.asn1 import *
import binascii
import struct
from Crypto.Util.number import inverse
try:
    from Crypto.PublicKey import _fastmath
except ImportError:
    _fastmath = None

def decode_der(obj_class, binstr):
    der = obj_class()
    der.decode(binstr)
    return der


class _RSAobj(pubkey.pubkey):
    keydata = ['n',
     'e',
     'd',
     'p',
     'q',
     'u']

    def __init__(self, implementation, key, randfunc=None):
        self.implementation = implementation
        self.key = key
        if randfunc is None:
            randfunc = Random.new().read
        self._randfunc = randfunc
        return

    def __getattr__(self, attrname):
        if attrname in self.keydata:
            return getattr(self.key, attrname)
        raise AttributeError('%s object has no %r attribute' % (self.__class__.__name__, attrname))

    def encrypt(self, plaintext, K):
        return pubkey.pubkey.encrypt(self, plaintext, K)

    def decrypt(self, ciphertext):
        return pubkey.pubkey.decrypt(self, ciphertext)

    def sign(self, M, K):
        return pubkey.pubkey.sign(self, M, K)

    def verify(self, M, signature):
        return pubkey.pubkey.verify(self, M, signature)

    def _encrypt(self, c, K):
        if not 0 < c < self.n:
            raise ValueError('Plaintext too large')
        return (self.key._encrypt(c),)

    def _decrypt(self, c):
        ciphertext = c[:1]
        if not 0 < ciphertext < self.n:
            raise ValueError('Ciphertext too large')
        r = getRandomRange(1, self.key.n - 1, randfunc=self._randfunc)
        cp = self.key._blind(ciphertext, r)
        mp = self.key._decrypt(cp)
        return self.key._unblind(mp, r)

    def _blind(self, m, r):
        return self.key._blind(m, r)

    def _unblind(self, m, r):
        return self.key._unblind(m, r)

    def _sign(self, m, K=None):
        return (self.key._sign(m),)

    def _verify(self, m, sig):
        s = sig[:1]
        return self.key._verify(m, s)

    def has_private(self):
        return self.key.has_private()

    def size(self):
        return self.key.size()

    def can_blind(self):
        return True

    def can_encrypt(self):
        return True

    def can_sign(self):
        return True

    def publickey(self):
        return self.implementation.construct((self.key.n, self.key.e))

    def __getstate__(self):
        d = {}
        for k in self.keydata:
            try:
                d[k] = getattr(self.key, k)
            except AttributeError:
                pass

        return d

    def __setstate__(self, d):
        if not hasattr(self, 'implementation'):
            self.implementation = RSAImplementation()
        if not hasattr(self, '_randfunc'):
            self._randfunc = Random.new().read
        t = []
        for k in self.keydata:
            if not d.has_key(k):
                break
            t.append(d[k])

        self.key = self.implementation._math.rsa_construct(*tuple(t))

    def __repr__(self):
        attrs = []
        for k in self.keydata:
            if k == 'n':
                attrs.append('n(%d)' % (self.size() + 1,))
            if hasattr(self.key, k):
                attrs.append(k)

        if self.has_private():
            attrs.append('private')
        return '<%s @0x%x %s>' % (self.__class__.__name__, id(self), ','.join(attrs))

    def exportKey(self, format='PEM', passphrase=None, pkcs=1, protection=None):
        if passphrase is not None:
            passphrase = tobytes(passphrase)
        if format == 'OpenSSH':
            eb = long_to_bytes(self.e)
            nb = long_to_bytes(self.n)
            if bord(eb[0]) & 128:
                eb = bchr(0) + eb
            if bord(nb[0]) & 128:
                nb = bchr(0) + nb
            keyparts = [b('ssh-rsa'), eb, nb]
            keystring = b('').join([ struct.pack('>I', len(kp)) + kp for kp in keyparts ])
            return b('ssh-rsa ') + binascii.b2a_base64(keystring)[:-1]
        else:
            if self.has_private():
                binary_key = newDerSequence(0, self.n, self.e, self.d, self.p, self.q, self.d % (self.p - 1), self.d % (self.q - 1), inverse(self.q, self.p)).encode()
                if pkcs == 1:
                    keyType = 'RSA PRIVATE'
                    if format == 'DER' and passphrase:
                        raise ValueError('PKCS#1 private key cannot be encrypted')
                elif format == 'PEM' and protection is None:
                    keyType = 'PRIVATE'
                    binary_key = PKCS8.wrap(binary_key, oid, None)
                else:
                    keyType = 'ENCRYPTED PRIVATE'
                    if not protection:
                        protection = 'PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC'
                    binary_key = PKCS8.wrap(binary_key, oid, passphrase, protection)
                    passphrase = None
            else:
                keyType = 'RSA PUBLIC'
                binary_key = newDerSequence(algorithmIdentifier, newDerBitString(newDerSequence(self.n, self.e))).encode()
            if format == 'DER':
                return binary_key
            if format == 'PEM':
                pem_str = PEM.encode(binary_key, keyType + ' KEY', passphrase, self._randfunc)
                return tobytes(pem_str)
            raise ValueError("Unknown key format '%s'. Cannot export the RSA key." % format)
            return


class RSAImplementation(object):

    def __init__(self, **kwargs):
        use_fast_math = kwargs.get('use_fast_math', None)
        if use_fast_math is None:
            if _fastmath is not None:
                self._math = _fastmath
            else:
                self._math = _slowmath
        elif use_fast_math:
            if _fastmath is not None:
                self._math = _fastmath
            else:
                raise RuntimeError('fast math module not available')
        else:
            self._math = _slowmath
        self.error = self._math.error
        self._default_randfunc = kwargs.get('default_randfunc', None)
        self._current_randfunc = None
        return

    def _get_randfunc(self, randfunc):
        if randfunc is not None:
            return randfunc
        else:
            if self._current_randfunc is None:
                self._current_randfunc = Random.new().read
            return self._current_randfunc

    def generate(self, bits, randfunc=None, progress_func=None, e=65537):
        if bits < 1024 or bits & 255 != 0:
            raise ValueError('RSA modulus length must be a multiple of 256 and >= 1024')
        if e % 2 == 0 or e < 3:
            raise ValueError('RSA public exponent must be a positive, odd integer larger than 2.')
        rf = self._get_randfunc(randfunc)
        obj = _RSA.generate_py(bits, rf, progress_func, e)
        key = self._math.rsa_construct(obj.n, obj.e, obj.d, obj.p, obj.q, obj.u)
        return _RSAobj(self, key)

    def construct(self, tup):
        key = self._math.rsa_construct(*tup)
        return _RSAobj(self, key)

    def _importKeyDER(self, extern_key, passphrase=None):
        try:
            der = decode_der(DerSequence, extern_key)
            if len(der) == 9 and der.hasOnlyInts() and der[0] == 0:
                del der[6:]
                der.append(inverse(der[4], der[5]))
                del der[0]
                return self.construct(der[:])
            if len(der) == 2:
                try:
                    if der.hasOnlyInts():
                        return self.construct(der[:])
                    if der[0] == algorithmIdentifier:
                        bitmap = decode_der(DerBitString, der[1])
                        rsaPub = decode_der(DerSequence, bitmap.value)
                        if len(rsaPub) == 2 and rsaPub.hasOnlyInts():
                            return self.construct(rsaPub[:])
                except (ValueError, EOFError):
                    pass

            k = PKCS8.unwrap(extern_key, passphrase)
            if k[0] == oid:
                return self._importKeyDER(k[1], passphrase)
        except (ValueError, EOFError):
            pass

        raise ValueError('RSA key format is not supported')

    def importKey(self, extern_key, passphrase=None):
        extern_key = tobytes(extern_key)
        if passphrase is not None:
            passphrase = tobytes(passphrase)
        if extern_key.startswith(b('-----')):
            der, marker, enc_flag = PEM.decode(tostr(extern_key), passphrase)
            if enc_flag:
                passphrase = None
            return self._importKeyDER(der, passphrase)
        elif extern_key.startswith(b('ssh-rsa ')):
            keystring = binascii.a2b_base64(extern_key.split(b(' '))[1])
            keyparts = []
            while len(keystring) > 4:
                l = struct.unpack('>I', keystring[:4])[0]
                keyparts.append(keystring[4:4 + l])
                keystring = keystring[4 + l:]

            e = bytes_to_long(keyparts[1])
            n = bytes_to_long(keyparts[2])
            return self.construct([n, e])
        elif bord(extern_key[0]) == 48:
            return self._importKeyDER(extern_key, passphrase)
        else:
            raise ValueError('RSA key format is not supported')
            return


oid = '1.2.840.113549.1.1.1'
algorithmIdentifier = DerSequence([DerObjectId(oid).encode(), DerNull().encode()]).encode()
_impl = RSAImplementation()
generate = _impl.generate
construct = _impl.construct
importKey = _impl.importKey
error = _impl.error
