# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/serializers.py
import abc
import typing
import wg_pickle
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.types import TData

class ISerializer(object):
    __slots__ = ()
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def deserialize(self, serializedData):
        pass

    @abc.abstractmethod
    def serialize(self, rawData):
        pass

    @abc.abstractmethod
    def rollbackSideEffects(self):
        pass


class WGPickleSerializer(ISerializer):
    __slots__ = ()

    def deserialize(self, serializedData):
        return wg_pickle.loads(serializedData)

    def serialize(self, rawData):
        return wg_pickle.dumps(rawData)

    def rollbackSideEffects(self):
        pass


defaultSerializer = WGPickleSerializer()
