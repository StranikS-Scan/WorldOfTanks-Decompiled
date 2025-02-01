# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/configs.py
import typing
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.types import TPDCVersion

class BasePDCConfig(object):
    __slots__ = ('version', 'cacheFilePath')

    def __init__(self, version, cacheFilePath):
        self.version = version
        if not cacheFilePath:
            raise SoftException('Cache file path cannot be empty.')
        self.cacheFilePath = cacheFilePath

    def __repr__(self):
        return '<{}>(version={}, cacheFilePath={})'.format(self.__class__.__name__, self.version, self.cacheFilePath)
