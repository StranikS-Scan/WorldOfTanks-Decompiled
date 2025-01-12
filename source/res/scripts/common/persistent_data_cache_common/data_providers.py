# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/data_providers.py
import typing
from persistent_data_cache_common.common import getLogger
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from persistent_data_cache_common.types import TData, TDataFactory
    from persistent_data_cache_common.serializers import ISerializer

class PDProvider(object):
    __slots__ = ('_logger', '_name', '_factory', '_serializer', '_data')

    def __init__(self, name, factory, serializer):
        self._logger = getLogger(self.__class__.__name__, name)
        self._name = name
        self._factory = factory
        self._serializer = serializer
        self._data = None
        self._logger.debug('Initialized.')
        return

    @property
    def name(self):
        return self._name

    def destroy(self):
        self._factory = None
        self._serializer = None
        self._data = None
        self._logger.debug('Destroyed.')
        return

    @property
    def isDataCreated(self):
        return self._data is not None

    def getSerializerClass(self):
        return self._serializer.__class__

    def get(self):
        return self._data

    def create(self):
        if self._data is not None:
            self._logger.debug('Data has been created already.')
            return self._data
        else:
            try:
                self._data = self._factory()
            except Exception:
                self._logger.exception('Failed to create data for <%s>.', self._name)

            if self._data is None:
                raise SoftException('Failed to create data for <{}>.'.format(self._name))
            self._logger.debug('Data has been created.')
            return self._data

    def serialize(self, rawData):
        result = self._serializer.serialize(rawData)
        self._logger.debug('Data has been serialized.')
        return result

    def deserialize(self, serializedData):
        result = self._serializer.deserialize(serializedData)
        self._logger.debug('Data has been deserialized.')
        return result
