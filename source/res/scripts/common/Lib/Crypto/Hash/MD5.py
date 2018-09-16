# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Hash/MD5.py
from __future__ import nested_scopes
_revision__ = '$Id$'
__all__ = ['new', 'block_size', 'digest_size']
from Crypto.Util.py3compat import *
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *

def __make_constructor():
    try:
        from hashlib import md5 as _hash_new
    except ImportError:
        from md5 import new as _hash_new

    h = _hash_new()
    if hasattr(h, 'new') and hasattr(h, 'name') and hasattr(h, 'digest_size') and hasattr(h, 'block_size'):
        return _hash_new
    else:
        _copy_sentinel = object()

        class _MD5(object):
            digest_size = 16
            block_size = 64
            name = 'md5'

            def __init__(self, *args):
                if args and args[0] is _copy_sentinel:
                    self._h = args[1]
                else:
                    self._h = _hash_new(*args)

            def copy(self):
                return _MD5(_copy_sentinel, self._h.copy())

            def update(self, *args):
                f = self.update = self._h.update
                f(*args)

            def digest(self):
                f = self.digest = self._h.digest
                return f()

            def hexdigest(self):
                f = self.hexdigest = self._h.hexdigest
                return f()

        _MD5.new = _MD5
        return _MD5


new = __make_constructor()
del __make_constructor
digest_size = new().digest_size
block_size = new().block_size
