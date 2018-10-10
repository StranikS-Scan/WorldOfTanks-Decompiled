# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Util/Counter.py
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
from Crypto.pct_warnings import DisableShortcut_DeprecationWarning
import _counter
import struct
import warnings
_deprecated = 'deprecated'

def new(nbits, prefix=b(''), suffix=b(''), initial_value=1, overflow=0, little_endian=False, allow_wraparound=False, disable_shortcut=_deprecated):
    nbytes, remainder = divmod(nbits, 8)
    if remainder != 0:
        raise ValueError('nbits must be a multiple of 8; got %d' % (nbits,))
    if nbytes < 1:
        raise ValueError('nbits too small')
    elif nbytes > 65535:
        raise ValueError('nbits too large')
    initval = _encode(initial_value, nbytes, little_endian)
    if disable_shortcut is not _deprecated:
        warnings.warn('disable_shortcut has no effect and is deprecated', DisableShortcut_DeprecationWarning)
    if little_endian:
        return _counter._newLE(bstr(prefix), bstr(suffix), initval, allow_wraparound=allow_wraparound)
    else:
        return _counter._newBE(bstr(prefix), bstr(suffix), initval, allow_wraparound=allow_wraparound)


def _encode(n, nbytes, little_endian=False):
    retval = []
    n = long(n)
    for i in range(nbytes):
        if little_endian:
            retval.append(bchr(n & 255))
        else:
            retval.insert(0, bchr(n & 255))
        n >>= 8

    return b('').join(retval)
