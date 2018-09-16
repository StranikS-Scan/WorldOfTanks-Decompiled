# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Random/OSRNG/__init__.py
__revision__ = '$Id$'
import os
if os.name == 'posix':
    from Crypto.Random.OSRNG.posix import new
elif os.name == 'nt':
    from Crypto.Random.OSRNG.nt import new
elif hasattr(os, 'urandom'):
    from Crypto.Random.OSRNG.fallback import new
else:
    raise ImportError('Not implemented')
