# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/ARC2.py
__revision__ = '$Id$'
from Crypto.Cipher import blockalgo
import _ARC2

class RC2Cipher(blockalgo.BlockAlgo):

    def __init__(self, key, *args, **kwargs):
        blockalgo.BlockAlgo.__init__(self, _ARC2, key, *args, **kwargs)


def new(key, *args, **kwargs):
    return RC2Cipher(key, *args, **kwargs)


MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_EAX = 9
block_size = 8
key_size = xrange(1, 17)
