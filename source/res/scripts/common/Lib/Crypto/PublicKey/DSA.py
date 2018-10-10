# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/PublicKey/DSA.py
__revision__ = '$Id$'
__all__ = ['generate',
 'construct',
 'error',
 'DSAImplementation',
 '_DSAobj',
 'importKey']
import binascii
import struct
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto import Random
from Crypto.IO import PKCS8, PEM
from Crypto.Util.number import bytes_to_long, long_to_bytes, getRandomRange
from Crypto.PublicKey import _DSA, _slowmath, pubkey
from Crypto.Util.asn1 import DerObject, DerSequence, DerInteger, DerObjectId, DerBitString, newDerSequence, newDerBitString
try:
    from Crypto.PublicKey import _fastmath
except ImportError:
    _fastmath = None

def decode_der(obj_class, binstr):
    der = obj_class()
    der.decode(binstr)
    return der


class _DSAobj(pubkey.pubkey):
    keydata = ['y',
     'g',
     'p',
     'q',
     'x']

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

    def sign(self, M, K):
        return pubkey.pubkey.sign(self, M, K)

    def verify(self, M, signature):
        return pubkey.pubkey.verify(self, M, signature)

    def _encrypt(self, c, K):
        raise TypeError('DSA cannot encrypt')

    def _decrypt(self, c):
        raise TypeError('DSA cannot decrypt')

    def _blind(self, m, r):
        raise TypeError('DSA cannot blind')

    def _unblind(self, m, r):
        raise TypeError('DSA cannot unblind')

    def _sign(self, m, k):
        blind_factor = getRandomRange(1, self.key.q, self._randfunc)
        return self.key._sign(m, k, blind_factor)

    def _verify(self, m, sig):
        r, s = sig
        return self.key._verify(m, r, s)

    def has_private(self):
        return self.key.has_private()

    def size(self):
        return self.key.size()

    def can_blind(self):
        return False

    def can_encrypt(self):
        return False

    def can_sign(self):
        return True

    def publickey(self):
        return self.implementation.construct((self.key.y,
         self.key.g,
         self.key.p,
         self.key.q))

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
            self.implementation = DSAImplementation()
        if not hasattr(self, '_randfunc'):
            self._randfunc = Random.new().read
        t = []
        for k in self.keydata:
            if not d.has_key(k):
                break
            t.append(d[k])

        self.key = self.implementation._math.dsa_construct(*tuple(t))

    def __repr__(self):
        attrs = []
        for k in self.keydata:
            if k == 'p':
                attrs.append('p(%d)' % (self.size() + 1,))
            if hasattr(self.key, k):
                attrs.append(k)

        if self.has_private():
            attrs.append('private')
        return '<%s @0x%x %s>' % (self.__class__.__name__, id(self), ','.join(attrs))

    def exportKey(self, format='PEM', pkcs8=None, passphrase=None, protection=None):
        if passphrase is not None:
            passphrase = tobytes(passphrase)
        if format == 'OpenSSH':
            tup1 = [ long_to_bytes(x) for x in (self.p,
             self.q,
             self.g,
             self.y) ]

            def func(x):
                if bord(x[0]) & 128:
                    return bchr(0) + x
                else:
                    return x

            tup2 = map(func, tup1)
            keyparts = [b('ssh-dss')] + tup2
            keystring = b('').join([ struct.pack('>I', len(kp)) + kp for kp in keyparts ])
            return b('ssh-dss ') + binascii.b2a_base64(keystring)[:-1]
        else:
            params = newDerSequence(self.p, self.q, self.g)
            if self.has_private():
                if pkcs8 is None:
                    pkcs8 = True
                if pkcs8:
                    if not protection:
                        protection = 'PBKDF2WithHMAC-SHA1AndDES-EDE3-CBC'
                    private_key = DerInteger(self.x).encode()
                    binary_key = PKCS8.wrap(private_key, oid, passphrase, protection, key_params=params, randfunc=self._randfunc)
                    if passphrase:
                        key_type = 'ENCRYPTED PRIVATE'
                    else:
                        key_type = 'PRIVATE'
                    passphrase = None
                else:
                    if format != 'PEM' and passphrase:
                        raise ValueError('DSA private key cannot be encrypted')
                    ints = [0,
                     self.p,
                     self.q,
                     self.g,
                     self.y,
                     self.x]
                    binary_key = newDerSequence(*ints).encode()
                    key_type = 'DSA PRIVATE'
            else:
                if pkcs8:
                    raise ValueError('PKCS#8 is only meaningful for private keys')
                binary_key = newDerSequence(newDerSequence(DerObjectId(oid), params), newDerBitString(DerInteger(self.y))).encode()
                key_type = 'DSA PUBLIC'
            if format == 'DER':
                return binary_key
            if format == 'PEM':
                pem_str = PEM.encode(binary_key, key_type + ' KEY', passphrase, self._randfunc)
                return tobytes(pem_str)
            raise ValueError("Unknown key format '%s'. Cannot export the DSA key." % format)
            return


class DSAImplementation(object):

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

    def generate(self, bits, randfunc=None, progress_func=None):
        for i in (0, 1, 2, 3, 4, 5, 6, 7, 8):
            if bits == 512 + 64 * i:
                return self._generate(bits, randfunc, progress_func)

        raise ValueError('Number of bits in p must be a multiple of 64 between 512 and 1024, not %d bits' % (bits,))

    def _generate(self, bits, randfunc=None, progress_func=None):
        rf = self._get_randfunc(randfunc)
        obj = _DSA.generate_py(bits, rf, progress_func)
        key = self._math.dsa_construct(obj.y, obj.g, obj.p, obj.q, obj.x)
        return _DSAobj(self, key)

    def construct(self, tup):
        key = self._math.dsa_construct(*tup)
        return _DSAobj(self, key)

    def _importKeyDER(self, key_data, passphrase=None, params=None):
        try:
            if params:
                x = decode_der(DerInteger, key_data).value
                params = decode_der(DerSequence, params)
                p, q, g = list(params)
                y = pow(g, x, p)
                tup = (y,
                 g,
                 p,
                 q,
                 x)
                return self.construct(tup)
            der = decode_der(DerSequence, key_data)
            if len(der) == 6 and der.hasOnlyInts() and der[0] == 0:
                tup = [ der[comp] for comp in (4, 3, 1, 2, 5) ]
                return self.construct(tup)
            if len(der) == 2:
                try:
                    algo = decode_der(DerSequence, der[0])
                    algo_oid = decode_der(DerObjectId, algo[0]).value
                    params = decode_der(DerSequence, algo[1])
                    if algo_oid == oid and len(params) == 3 and params.hasOnlyInts():
                        bitmap = decode_der(DerBitString, der[1])
                        pub_key = decode_der(DerInteger, bitmap.value)
                        tup = [pub_key.value]
                        tup += [ params[comp] for comp in (2, 0, 1) ]
                        return self.construct(tup)
                except (ValueError, EOFError):
                    pass

            p8_pair = PKCS8.unwrap(key_data, passphrase)
            if p8_pair[0] == oid:
                return self._importKeyDER(p8_pair[1], passphrase, p8_pair[2])
        except (ValueError, EOFError):
            pass

        raise ValueError('DSA key format is not supported')

    def importKey(self, extern_key, passphrase=None):
        extern_key = tobytes(extern_key)
        if passphrase is not None:
            passphrase = tobytes(passphrase)
        if extern_key.startswith(b('-----')):
            der, marker, enc_flag = PEM.decode(tostr(extern_key), passphrase)
            if enc_flag:
                passphrase = None
            return self._importKeyDER(der, passphrase)
        else:
            if extern_key.startswith(b('ssh-dss ')):
                keystring = binascii.a2b_base64(extern_key.split(b(' '))[1])
                keyparts = []
                while len(keystring) > 4:
                    length = struct.unpack('>I', keystring[:4])[0]
                    keyparts.append(keystring[4:4 + length])
                    keystring = keystring[4 + length:]

                if keyparts[0] == b('ssh-dss'):
                    tup = [ bytes_to_long(keyparts[x]) for x in (4, 3, 1, 2) ]
                    return self.construct(tup)
            if bord(extern_key[0]) == 48:
                return self._importKeyDER(extern_key, passphrase)
            raise ValueError('DSA key format is not supported')
            return


oid = '1.2.840.10040.4.1'
_impl = DSAImplementation()
generate = _impl.generate
construct = _impl.construct
importKey = _impl.importKey
error = _impl.error
