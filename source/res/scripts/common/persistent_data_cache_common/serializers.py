# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/serializers.py
from __future__ import absolute_import
import typing
import wg_pickle
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.types import TData

class ISerializer(object):
    __slots__ = ()

    def deserialize(self, serializedData):
        raise NotImplementedError

    def serialize(self, rawData):
        raise NotImplementedError

    def rollbackSideEffects(self):
        raise NotImplementedError


class WGPickleSerializer(ISerializer):
    __slots__ = ()

    def deserialize(self, serializedData):
        return wg_pickle.loads(serializedData)

    def serialize(self, rawData):
        return wg_pickle.dumps(rawData)

    def rollbackSideEffects(self):
        pass


defaultSerializer = WGPickleSerializer()
