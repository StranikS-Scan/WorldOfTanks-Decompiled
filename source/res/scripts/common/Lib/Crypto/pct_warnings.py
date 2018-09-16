# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/pct_warnings.py


class CryptoWarning(Warning):
    pass


class CryptoDeprecationWarning(DeprecationWarning, CryptoWarning):
    pass


class CryptoRuntimeWarning(RuntimeWarning, CryptoWarning):
    pass


class RandomPool_DeprecationWarning(CryptoDeprecationWarning):
    pass


class ClockRewindWarning(CryptoRuntimeWarning):
    pass


class GetRandomNumber_DeprecationWarning(CryptoDeprecationWarning):
    pass


class DisableShortcut_DeprecationWarning(CryptoDeprecationWarning):
    pass


class PowmInsecureWarning(CryptoRuntimeWarning):
    pass


import warnings as _warnings
_warnings.filterwarnings('always', category=ClockRewindWarning, append=1)
