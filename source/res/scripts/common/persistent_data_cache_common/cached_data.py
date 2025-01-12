# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/cached_data.py
import typing
from collections import OrderedDict
import wg_pickle
from persistent_data_cache_common.common import getLogger, MeasureExecutionTime
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.types import TData, TPDCVersion
    from persistent_data_cache_common.serializers import ISerializer
    from persistent_data_cache_common.data_providers import PDProvider

class LoadedData(object):
    __slots__ = ('_logger', '_version', '_data')

    def __init__(self, version, data):
        self._logger = getLogger(self.__class__.__name__)
        self._version = version
        self._data = data

    @property
    def version(self):
        return self._version

    def deserialize(self, onDataDeserialized=None):
        appliedSerializers = OrderedDict()
        deserialized, timing = {}, MeasureExecutionTime('cache.part.unpacked')
        try:
            for name, (serialized, serializerClass) in self._data:
                with timing.start(name):
                    serializer = serializerClass()
                    appliedSerializers[name] = serializer
                    deserialized[name] = serializer.deserialize(serialized)
                    if callable(onDataDeserialized):
                        onDataDeserialized(name)
                self._logger.debug('Data <%s> has been loaded with <%s>.', name, serializer)

        except Exception:
            for name, appliedSerializer in appliedSerializers.iteritems():
                appliedSerializer.rollbackSideEffects()
                self._logger.debug('Deserialized data <%s|%s> side effects rollback.', name, appliedSerializer)

            raise

        timing.printTotalTime()
        return deserialized


class CreatedData(object):
    __slots__ = ('_logger', '_version', '_data')

    def __init__(self, version):
        self._logger = getLogger(self.__class__.__name__)
        self._version = version
        self._data = OrderedDict()

    def isEmpty(self):
        return len(self._data) == 0

    def add(self, provider, data):
        name = provider.name
        if name in self._data:
            self._logger.error('Data for <%s> already exist.', name)
            return
        serializerClass = provider.getSerializerClass()
        self._data[name] = (data, serializerClass)
        self._logger.debug('Data <%s|%s> added.', name, serializerClass)

    def toDict(self):
        return {'version': self._version,
         'data': self._data.items()}


def dumps(cachedData):
    return wg_pickle.dumps(cachedData.toDict())


def loads(string):
    return LoadedData(**wg_pickle.loads(string))
