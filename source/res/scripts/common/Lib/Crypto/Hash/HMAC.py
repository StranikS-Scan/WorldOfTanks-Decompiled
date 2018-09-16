# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Hash/HMAC.py
__revision__ = '$Id$'
__all__ = ['new', 'digest_size', 'HMAC']
from binascii import unhexlify
from Crypto.Util.strxor import strxor_c
from Crypto.Util.py3compat import *
digest_size = None

class HMAC:
    digest_size = None

    def __init__(self, key, msg=None, digestmod=None):
        if digestmod is None:
            import MD5
            digestmod = MD5
        self.digestmod = digestmod
        self.outer = digestmod.new()
        self.inner = digestmod.new()
        try:
            self.digest_size = digestmod.digest_size
        except AttributeError:
            self.digest_size = len(self.outer.digest())

        try:
            blocksize = digestmod.block_size
        except AttributeError:
            blocksize = 64

        ipad = 54
        opad = 92
        if len(key) > blocksize:
            key = digestmod.new(key).digest()
        key = key + bchr(0) * (blocksize - len(key))
        self.outer.update(strxor_c(key, opad))
        self.inner.update(strxor_c(key, ipad))
        if msg:
            self.update(msg)
        return

    def update(self, msg):
        self.inner.update(msg)

    def copy(self):
        other = HMAC(b(''))
        other.digestmod = self.digestmod
        other.inner = self.inner.copy()
        other.outer = self.outer.copy()
        return other

    def digest(self):
        h = self.outer.copy()
        h.update(self.inner.digest())
        return h.digest()

    def verify(self, mac_tag):
        mac = self.digest()
        res = 0
        for x, y in zip(mac, mac_tag):
            res |= bord(x) ^ bord(y)

        if res or len(mac_tag) != self.digest_size:
            raise ValueError('MAC check failed')

    def hexdigest(self):
        return ''.join([ '%02x' % bord(x) for x in tuple(self.digest()) ])

    def hexverify(self, hex_mac_tag):
        self.verify(unhexlify(tobytes(hex_mac_tag)))


def new(key, msg=None, digestmod=None):
    return HMAC(key, msg, digestmod)
