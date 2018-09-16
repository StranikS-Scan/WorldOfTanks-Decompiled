# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Random/OSRNG/fallback.py
__revision__ = '$Id$'
__all__ = ['PythonOSURandomRNG']
import os
from rng_base import BaseRNG

class PythonOSURandomRNG(BaseRNG):
    name = '<os.urandom>'

    def __init__(self):
        self._read = os.urandom
        BaseRNG.__init__(self)

    def _close(self):
        self._read = None
        return


def new(*args, **kwargs):
    return PythonOSURandomRNG(*args, **kwargs)
