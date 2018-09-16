# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Cipher/AES.py
__revision__ = '$Id$'
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Cipher import blockalgo
import _AES
from Crypto.Util import cpuid
try:
    if cpuid.have_aes_ni():
        from Crypto.Cipher import _AESNI
    else:
        _AESNI = None
except ImportError:
    _AESNI = None

class AESCipher(blockalgo.BlockAlgo):

    def __init__(self, key, *args, **kwargs):
        use_aesni = True
        if kwargs.has_key('use_aesni'):
            use_aesni = kwargs['use_aesni']
            del kwargs['use_aesni']
        if _AESNI is not None and use_aesni:
            blockalgo.BlockAlgo.__init__(self, _AESNI, key, *args, **kwargs)
        else:
            blockalgo.BlockAlgo.__init__(self, _AES, key, *args, **kwargs)
        return


def new(key, *args, **kwargs):
    return AESCipher(key, *args, **kwargs)


MODE_ECB = 1
MODE_CBC = 2
MODE_CFB = 3
MODE_PGP = 4
MODE_OFB = 5
MODE_CTR = 6
MODE_OPENPGP = 7
MODE_CCM = 8
MODE_EAX = 9
MODE_SIV = 10
MODE_GCM = 11
block_size = 16
key_size = (16, 24, 32)
