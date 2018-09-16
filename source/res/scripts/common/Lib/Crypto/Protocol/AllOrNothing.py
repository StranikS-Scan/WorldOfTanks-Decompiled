# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Protocol/AllOrNothing.py
__revision__ = '$Id$'
import operator
import sys
from Crypto.Util.number import bytes_to_long, long_to_bytes
from Crypto.Util.py3compat import *

def isInt(x):
    test = 0
    try:
        test += x
    except TypeError:
        return 0


class AllOrNothing:

    def __init__(self, ciphermodule, mode=None, IV=None):
        self.__ciphermodule = ciphermodule
        self.__mode = mode
        self.__IV = IV
        self.__key_size = ciphermodule.key_size
        if not isInt(self.__key_size) or self.__key_size == 0:
            self.__key_size = 16

    __K0digit = bchr(105)

    def digest(self, text):
        key = self._inventkey(self.__key_size)
        K0 = self.__K0digit * self.__key_size
        mcipher = self.__newcipher(key)
        hcipher = self.__newcipher(K0)
        block_size = self.__ciphermodule.block_size
        padbytes = block_size - len(text) % block_size
        text = text + b(' ') * padbytes
        s = divmod(len(text), block_size)[0]
        blocks = []
        hashes = []
        for i in range(1, s + 1):
            start = (i - 1) * block_size
            end = start + block_size
            mi = text[start:end]
            cipherblock = mcipher.encrypt(long_to_bytes(i, block_size))
            mticki = bytes_to_long(mi) ^ bytes_to_long(cipherblock)
            blocks.append(mticki)
            hi = hcipher.encrypt(long_to_bytes(mticki ^ i, block_size))
            hashes.append(bytes_to_long(hi))

        i = i + 1
        cipherblock = mcipher.encrypt(long_to_bytes(i, block_size))
        mticki = padbytes ^ bytes_to_long(cipherblock)
        blocks.append(mticki)
        hi = hcipher.encrypt(long_to_bytes(mticki ^ i, block_size))
        hashes.append(bytes_to_long(hi))
        mtick_stick = bytes_to_long(key) ^ reduce(operator.xor, hashes)
        blocks.append(mtick_stick)
        return [ long_to_bytes(i, self.__ciphermodule.block_size) for i in blocks ]

    def undigest(self, blocks):
        if len(blocks) < 2:
            raise ValueError, 'List must be at least length 2.'
        blocks = map(bytes_to_long, blocks)
        K0 = self.__K0digit * self.__key_size
        hcipher = self.__newcipher(K0)
        block_size = self.__ciphermodule.block_size
        hashes = []
        for i in range(1, len(blocks)):
            mticki = blocks[i - 1] ^ i
            hi = hcipher.encrypt(long_to_bytes(mticki, block_size))
            hashes.append(bytes_to_long(hi))

        key = blocks[-1] ^ reduce(operator.xor, hashes)
        mcipher = self.__newcipher(long_to_bytes(key, self.__key_size))
        parts = []
        for i in range(1, len(blocks)):
            cipherblock = mcipher.encrypt(long_to_bytes(i, block_size))
            mi = blocks[i - 1] ^ bytes_to_long(cipherblock)
            parts.append(mi)

        padbytes = int(parts[-1])
        text = b('').join(map(long_to_bytes, parts[:-1]))
        return text[:-padbytes]

    def _inventkey(self, key_size):
        from Crypto import Random
        return Random.new().read(key_size)

    def __newcipher(self, key):
        if self.__mode is None and self.__IV is None:
            return self.__ciphermodule.new(key)
        elif self.__IV is None:
            return self.__ciphermodule.new(key, self.__mode)
        else:
            return self.__ciphermodule.new(key, self.__mode, self.__IV)
            return


if __name__ == '__main__':
    import sys
    import getopt
    import base64
    usagemsg = 'Test module usage: %(program)s [-c cipher] [-l] [-h]\n\nWhere:\n    --cipher module\n    -c module\n        Cipher module to use.  Default: %(ciphermodule)s\n\n    --aslong\n    -l\n        Print the encoded message blocks as long integers instead of base64\n        encoded strings\n\n    --help\n    -h\n        Print this help message\n'
    ciphermodule = 'AES'
    aslong = 0

    def usage(code, msg=None):
        if msg:
            print msg
        print usagemsg % {'program': sys.argv[0],
         'ciphermodule': ciphermodule}
        sys.exit(code)


    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:l', ['cipher=', 'aslong'])
    except getopt.error as msg:
        usage(1, msg)

    if args:
        usage(1, 'Too many arguments')
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage(0)
        if opt in ('-c', '--cipher'):
            ciphermodule = arg
        if opt in ('-l', '--aslong'):
            aslong = 1

    module = __import__('Crypto.Cipher.' + ciphermodule, None, None, ['new'])
    x = AllOrNothing(module)
    print 'Original text:\n=========='
    print __doc__
    print '=========='
    msgblocks = x.digest(b(__doc__))
    print 'message blocks:'
    for i, blk in zip(range(len(msgblocks)), msgblocks):
        print '    %3d' % i,
        if aslong:
            print bytes_to_long(blk)
        print base64.encodestring(blk)[:-1]

    y = AllOrNothing(module)
    text = y.undigest(msgblocks)
    if text == b(__doc__):
        print 'They match!'
    else:
        print 'They differ!'
