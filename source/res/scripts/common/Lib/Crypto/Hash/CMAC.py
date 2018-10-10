# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Hash/CMAC.py
__all__ = ['new', 'digest_size', 'CMAC']
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from binascii import unhexlify
from Crypto.Util.strxor import strxor
from Crypto.Util.number import long_to_bytes, bytes_to_long
digest_size = None

def _shift_bytes(bs, xor_lsb=0):
    num = bytes_to_long(bs) << 1 ^ xor_lsb
    return long_to_bytes(num, len(bs))[-len(bs):]


class _SmoothMAC(object):

    def __init__(self, block_size, msg=b(''), min_digest=0):
        self._bs = block_size
        self._buffer = []
        self._buffer_len = 0
        self._total_len = 0
        self._min_digest = min_digest
        self._mac = None
        self._tag = None
        if msg:
            self.update(msg)
        return

    def can_reduce(self):
        return self._mac is not None

    def get_len(self):
        return self._total_len

    def zero_pad(self):
        if self._buffer_len & self._bs - 1:
            npad = self._bs - self._buffer_len & self._bs - 1
            self._buffer.append(bchr(0) * npad)
            self._buffer_len += npad

    def update(self, data):
        if self._buffer_len == 0 and self.can_reduce() and self._min_digest == 0 and len(data) % self._bs == 0:
            self._update(data)
            self._total_len += len(data)
            return
        self._buffer.append(data)
        self._buffer_len += len(data)
        self._total_len += len(data)
        blocks, rem = divmod(self._buffer_len, self._bs)
        if rem < self._min_digest:
            blocks -= 1
        if blocks > 0 and self.can_reduce():
            aligned_data = blocks * self._bs
            buf = b('').join(self._buffer)
            self._update(buf[:aligned_data])
            self._buffer = [buf[aligned_data:]]
            self._buffer_len -= aligned_data

    def _deep_copy(self, target):
        target._buffer = self._buffer[:]
        for m in ['_bs',
         '_buffer_len',
         '_total_len',
         '_min_digest',
         '_tag']:
            setattr(target, m, getattr(self, m))

    def _update(self, data_block):
        raise NotImplementedError('_update() must be still implemented')

    def _digest(self, left_data):
        raise NotImplementedError('_digest() must be still implemented')

    def digest(self):
        if self._tag:
            return self._tag
        if self._buffer_len > 0:
            self.update(b(''))
        left_data = b('').join(self._buffer)
        self._tag = self._digest(left_data)
        return self._tag


class CMAC(_SmoothMAC):
    digest_size = None

    def __init__(self, key, msg=None, ciphermod=None):
        if ciphermod is None:
            raise TypeError('ciphermod must be specified (try AES)')
        _SmoothMAC.__init__(self, ciphermod.block_size, msg, 1)
        self._key = key
        self._factory = ciphermod
        if ciphermod.block_size == 8:
            const_Rb = 27
        elif ciphermod.block_size == 16:
            const_Rb = 135
        else:
            raise TypeError('CMAC requires a cipher with a block size of 8 or 16 bytes, not %d' % (ciphermod.block_size,))
        self.digest_size = ciphermod.block_size
        cipher = ciphermod.new(key, ciphermod.MODE_ECB)
        l = cipher.encrypt(bchr(0) * ciphermod.block_size)
        if bord(l[0]) & 128:
            self._k1 = _shift_bytes(l, const_Rb)
        else:
            self._k1 = _shift_bytes(l)
        if bord(self._k1[0]) & 128:
            self._k2 = _shift_bytes(self._k1, const_Rb)
        else:
            self._k2 = _shift_bytes(self._k1)
        self._IV = bchr(0) * ciphermod.block_size
        self._mac = ciphermod.new(key, ciphermod.MODE_CBC, self._IV)
        return

    def update(self, msg):
        _SmoothMAC.update(self, msg)

    def _update(self, data_block):
        self._IV = self._mac.encrypt(data_block)[-self._mac.block_size:]

    def copy(self):
        obj = CMAC(self._key, ciphermod=self._factory)
        _SmoothMAC._deep_copy(self, obj)
        obj._mac = self._factory.new(self._key, self._factory.MODE_CBC, self._IV)
        for m in ['_tag',
         '_k1',
         '_k2',
         '_IV']:
            setattr(obj, m, getattr(self, m))

        return obj

    def digest(self):
        return _SmoothMAC.digest(self)

    def _digest(self, last_data):
        if len(last_data) == self._bs:
            last_block = strxor(last_data, self._k1)
        else:
            last_block = strxor(last_data + bchr(128) + bchr(0) * (self._bs - 1 - len(last_data)), self._k2)
        tag = self._mac.encrypt(last_block)
        return tag

    def hexdigest(self):
        return ''.join([ '%02x' % bord(x) for x in tuple(self.digest()) ])

    def verify(self, mac_tag):
        mac = self.digest()
        res = 0
        for x, y in zip(mac, mac_tag):
            res |= bord(x) ^ bord(y)

        if res or len(mac_tag) != self.digest_size:
            raise ValueError('MAC check failed')

    def hexverify(self, hex_mac_tag):
        self.verify(unhexlify(tobytes(hex_mac_tag)))


def new(key, msg=None, ciphermod=None):
    return CMAC(key, msg, ciphermod)
