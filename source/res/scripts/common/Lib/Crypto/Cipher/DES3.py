# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/DES3.py
__revision__ = '$Id$'
from Crypto.Cipher import blockalgo
from Crypto.Cipher import _DES3

class DES3Cipher(blockalgo.BlockAlgo):

    def __init__(self, key, *args, **kwargs):
        blockalgo.BlockAlgo.__init__(self, _DES3, key, *args, **kwargs)


def new(key, *args, **kwargs):
    return DES3Cipher(key, *args, **kwargs)


MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_EAX = 9
block_size = 8
key_size = (16, 24)
