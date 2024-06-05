# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/DossierBlockBuilders.py
import typing
from typing import List, Union
from dossiers2.common.DossierBlocks import *
from dossiers2.custom.records import RECORDS, RECORD_INDICES, BIT_STORAGES
from serialization.serializable_component import SerializableComponentChildType
if typing.TYPE_CHECKING:
    from dossiers2.common.DossierDescr import DossierDescr
    EVENT_HANDLERS_TYPE = Iterable[Callable[[DossierDescr, SerializableBlockDescr, [str, Any, Any]], None]]
_SUPPORTED_FORMATS = frozenset('cbBhHiIlLqQfd')

class IBlockBuilderWithRecordsLayout(object):
    name = None
    recordsLayout = []

    def build(self, dossierDescr, compDescr=''):
        raise NotImplementedError


class StaticSizeBlockBuilder(IBlockBuilderWithRecordsLayout):

    def __init__(self, name, recordsLayout, eventsHandlers, popUpRecords, logRecords=None):
        self.name = name
        self.recordsLayout = recordsLayout
        self.__eventsHandlers = eventsHandlers
        self.__popUpRecords = set(popUpRecords)
        self.__logRecords = set(logRecords) if logRecords else popUpRecords
        self.__layout = layout = [ (record, {}) for record in recordsLayout ]
        self.__packing = dict(layout)
        self.__format = '<'
        self.__initialData = initial = {}
        offset = 0
        for record, recordPacking in layout:
            recordInfo = RECORDS[RECORD_INDICES[name, record]]
            type, fmt, maxValue = recordInfo[2:5]
            size = struct.calcsize('<' + fmt)
            recordPacking['type'] = type
            recordPacking['format'] = fmt
            recordPacking['offset'] = offset
            recordPacking['maxValue'] = maxValue
            initial[record] = 0
            offset += size
            self.__format += fmt
            bits = BIT_STORAGES.get((name, record), None)
            if bits is not None:
                for bit in bits:
                    bitOffset = RECORDS[RECORD_INDICES[name, bit]][4]
                    self.__packing[bit] = {'type': 'b',
                     'storage': record,
                     'offset': bitOffset}

        self.__blockSize = struct.calcsize(self.__format)
        return

    def build(self, dossierDescr, compDescr=''):
        return StaticDossierBlockDescr(name=self.name, dossierDescr=dossierDescr, compDescr=compDescr, eventsHandlers=self.__eventsHandlers, popUpRecords=self.__popUpRecords, logRecords=self.__logRecords, recordsLayout=self.__layout, packing=self.__packing, format=self.__format, blockSize=self.__blockSize, initialData=self.__initialData)


class DictBlockBuilder(object):

    def __init__(self, name, keyFormat, valueFormat, eventsHandlers, popUpRecords=None, logRecords=None):
        self.name = name
        self.__keyFormat = keyFormat
        self.__valueFormat = valueFormat
        self.__eventsHandlers = eventsHandlers
        self.__popUpRecords = popUpRecords
        self.__logRecords = logRecords

    def build(self, dossierDescr, compDescr=''):
        if not isinstance(self.__popUpRecords, set):
            self.__popUpRecords = set(self.__popUpRecords) if self.__popUpRecords else set()
        if not isinstance(self.__logRecords, set):
            self.__logRecords = set(self.__logRecords) if self.__logRecords else self.__popUpRecords
        return DictDossierBlockDescr(name=self.name, dossierDescr=dossierDescr, compDescr=compDescr, eventsHandlers=self.__eventsHandlers, keyFormat=self.__keyFormat, valueFormat=self.__valueFormat, popUpRecords=self.__popUpRecords, logRecords=self.__logRecords)


class ListBlockBuilder(object):

    def __init__(self, name, itemFormat, eventsHandlers):
        self.name = name
        self.__itemFormat = itemFormat
        self.__eventsHandlers = eventsHandlers

    def build(self, dossierDescr, compDescr=''):
        return ListDossierBlockDescr(name=self.name, dossierDescr=dossierDescr, compDescr=compDescr, eventsHandlers=self.__eventsHandlers, itemFormat=self.__itemFormat)


class BinarySetDossierBlockBuilder(IBlockBuilderWithRecordsLayout):

    def __init__(self, name, valueNames, eventHandlers, popUpRecords, logRecords=None):
        self.name = name
        self.recordsLayout = valueNames
        self.__valueToPosition = self.__buildValueToPosition(valueNames)
        self.__eventHandlers = eventHandlers
        self.__popUpRecords = set(popUpRecords)
        self.__logRecords = set(logRecords) if logRecords else popUpRecords

    def build(self, dossierDescr, compDescr=''):
        return BinarySetDossierBlockDescr(self.name, dossierDescr, compDescr, self.__eventHandlers, self.__popUpRecords, self.recordsLayout, self.__valueToPosition, self.__logRecords)

    def __buildValueToPosition(self, valueNames):
        valToPos = {}
        for valueNum, name in enumerate(valueNames):
            byteNum, bitNum = divmod(valueNum, 8)
            valToPos[name] = (byteNum, 1 << bitNum)

        return valToPos


class SerializableBlockBuilder(IBlockBuilderWithRecordsLayout):

    def __init__(self, name, componentClass, parserCallback, eventHandlers, popUpRecords, logRecords):
        self.name = name
        self.componentClass = componentClass
        self.parserCallback = parserCallback
        self.recordsLayout = list(self.componentClass.fields.keys())
        self.__eventHandlers = eventHandlers
        self.__popUpRecords = set(popUpRecords)
        self.__logRecords = set(logRecords) if logRecords else set(popUpRecords)

    def build(self, dossierDescr, compDescr=''):
        return SerializableBlockDescr(self.name, dossierDescr, self.componentClass, self.parserCallback, compDescr, self.__eventHandlers, self.__popUpRecords, self.__logRecords)


TYPE_BLOCK_BUILDER = Union[StaticSizeBlockBuilder, DictBlockBuilder, ListBlockBuilder, BinarySetDossierBlockBuilder, SerializableBlockBuilder]
