# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/DossierBlockBuilders.py
import struct
from dossiers2.custom.records import RECORDS, RECORD_INDICES, BIT_STORAGES
from dossiers2.common.DossierBlocks import *
_SUPPORTED_FORMATS = frozenset('cbBhHiIlLqQfd')

class StaticSizeBlockBuilder(object):

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

    def __init__(self, name, keyFormat, valueFormat, eventsHandlers):
        self.name = name
        self.__keyFormat = keyFormat
        self.__valueFormat = valueFormat
        self.__eventsHandlers = eventsHandlers

    def build(self, dossierDescr, compDescr=''):
        return DictDossierBlockDescr(name=self.name, dossierDescr=dossierDescr, compDescr=compDescr, eventsHandlers=self.__eventsHandlers, keyFormat=self.__keyFormat, valueFormat=self.__valueFormat)


class ListBlockBuilder(object):

    def __init__(self, name, itemFormat, eventsHandlers):
        self.name = name
        self.__itemFormat = itemFormat
        self.__eventsHandlers = eventsHandlers

    def build(self, dossierDescr, compDescr=''):
        return ListDossierBlockDescr(name=self.name, dossierDescr=dossierDescr, compDescr=compDescr, eventsHandlers=self.__eventsHandlers, itemFormat=self.__itemFormat)


class BinarySetDossierBlockBuilder(object):

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
