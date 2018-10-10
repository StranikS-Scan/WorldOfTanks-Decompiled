# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Random/Fortuna/FortunaGenerator.py
__revision__ = '$Id$'
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
import struct
from Crypto.Util.number import ceil_shift, exact_log2, exact_div
from Crypto.Util import Counter
from Crypto.Cipher import AES
import SHAd256

class AESGenerator(object):
    block_size = AES.block_size
    key_size = 32
    max_blocks_per_request = 65536
    _four_kiblocks_of_zeros = b('\x00') * block_size * 4096

    def __init__(self):
        self.counter = Counter.new(nbits=self.block_size * 8, initial_value=0, little_endian=True)
        self.key = None
        self.block_size_shift = exact_log2(self.block_size)
        self.blocks_per_key = exact_div(self.key_size, self.block_size)
        self.max_bytes_per_request = self.max_blocks_per_request * self.block_size
        return

    def reseed(self, seed):
        if self.key is None:
            self.key = b('\x00') * self.key_size
        self._set_key(SHAd256.new(self.key + seed).digest())
        self.counter()
        return

    def pseudo_random_data(self, bytes):
        num_full_blocks = bytes >> 20
        remainder = bytes & 1048575
        retval = []
        for i in xrange(num_full_blocks):
            retval.append(self._pseudo_random_data(1048576))

        retval.append(self._pseudo_random_data(remainder))
        return b('').join(retval)

    def _set_key(self, key):
        self.key = key
        self._cipher = AES.new(key, AES.MODE_CTR, counter=self.counter)

    def _pseudo_random_data(self, bytes):
        if not 0 <= bytes <= self.max_bytes_per_request:
            raise AssertionError('You cannot ask for more than 1 MiB of data per request')
        num_blocks = ceil_shift(bytes, self.block_size_shift)
        retval = self._generate_blocks(num_blocks)[:bytes]
        self._set_key(self._generate_blocks(self.blocks_per_key))
        return retval

    def _generate_blocks(self, num_blocks):
        if self.key is None:
            raise AssertionError('generator must be seeded before use')
        retval = []
        for i in xrange(num_blocks >> 12):
            retval.append(self._cipher.encrypt(self._four_kiblocks_of_zeros))

        remaining_bytes = (num_blocks & 4095) << self.block_size_shift
        retval.append(self._cipher.encrypt(self._four_kiblocks_of_zeros[:remaining_bytes]))
        return b('').join(retval)
