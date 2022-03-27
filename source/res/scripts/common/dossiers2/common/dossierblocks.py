# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dossiers2/common/DossierBlocks.py
import struct
import weakref
from array import array
from itertools import izip
from debug_utils import LOG_ERROR

class StaticDossierBlockDescr(object):
    eventsEnabled = True

    def __init__(self, name, dossierDescr, compDescr, eventsHandlers, popUpRecords, recordsLayout, packing, format, blockSize, initialData, logRecords):
        self.name = name
        self.__dossierDescrRef = weakref.ref(dossierDescr)
        self.__initialCompDescr = compDescr
        self.__eventsHandlers = eventsHandlers
        self.__popUpRecords = popUpRecords
        self.__logRecords = logRecords
        self.__recordsLayout = recordsLayout
        self.__packing = packing
        self.__format = format
        self.__blockSize = blockSize
        self.__isExpanded = False
        self.__data = {}
        self.__changed = set()
        if compDescr == '':
            self.__isExpanded = True
            self.__data = dict(initialData)

    def __getitem__(self, record):
        data = self.__data
        if record in data:
            return data[record]
        packing = self.__packing[record]
        if packing['type'] == 'p':
            value = struct.unpack_from('<' + packing['format'], self.__initialCompDescr, packing['offset'])[0]
        else:
            value = bool(self[packing['storage']] & 1 << packing['offset'])
        data[record] = value
        return value

    def __setitem__(self, record, value):
        packing = self.__packing[record]
        if packing['type'] == 'p':
            value = min(value, packing['maxValue'])
        else:
            value = bool(value)
        prevValue = self[record]
        if value == prevValue:
            return
        self.__data[record] = value
        if packing['type'] == 'p':
            self.__changed.add(record)
        else:
            self[packing['storage']] ^= 1 << packing['offset']
        if record in self.__popUpRecords:
            self.__dossierDescrRef().addPopUp(self.name, record, value, addLogRecord=False)
        if record in self.__logRecords:
            self.__dossierDescrRef().addLogRecord(self.name, record, value)
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get(record, []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(record, value, prevValue))

    def __contains__(self, record):
        return record in self.__packing

    def __str__(self):
        self.expand()
        return str(self.__data)

    def expand(self):
        if self.__isExpanded:
            return self
        values = struct.unpack(self.__format, self.__initialCompDescr)
        data = dict([ (key, value) for value, (key, _) in izip(values, self.__recordsLayout) ])
        data.update(self.__data)
        self.__data = data
        self.__isExpanded = True
        return self

    def getChanges(self):
        return self.__changed

    def get(self, key, default=None):
        return self[key] if key in self else default

    def updateDossierCompDescr(self, dossierCompDescrArray, offset, size):
        if size == 0:
            compDescrArray = array('c', struct.pack(self.__format, *self.__getValuesForPacking()))
            self.__changed.clear()
            return (dossierCompDescrArray[:offset] + compDescrArray + dossierCompDescrArray[offset:], self.__blockSize)
        if self.__isExpanded:
            struct.pack_into(self.__format, dossierCompDescrArray, offset, *self.__getValuesForPacking())
            self.__changed.clear()
            return (dossierCompDescrArray, self.__blockSize)
        changed = self.__changed
        packing = self.__packing
        data = self.__data
        for record in changed:
            packingRec = packing[record]
            if packingRec['type'] == 'b':
                continue
            struct.pack_into('<' + packingRec['format'], dossierCompDescrArray, offset + packingRec['offset'], data[record])

        changed.clear()
        return (dossierCompDescrArray, self.__blockSize)

    def __getValuesForPacking(self):
        data = self.__data
        return [ data[rec] for rec, _ in self.__recordsLayout ]


class DictDossierBlockDescr(object):
    eventsEnabled = True

    def __init__(self, name, dossierDescr, compDescr, eventsHandlers, keyFormat, valueFormat):
        self.name = name
        self.__dossierDescrRef = weakref.ref(dossierDescr)
        self.__eventsHandlers = eventsHandlers
        self.__itemFormat = keyFormat + valueFormat
        self.__itemSize = struct.calcsize('<' + self.__itemFormat)
        self.__isExpanded = False
        keyLength = len(keyFormat)
        valueLength = len(valueFormat)
        if keyLength == 1 and valueLength == 1:
            self.__itemToList = lambda key, value: (key, value)
            self.__listToItem = lambda values, idx: (values[idx], values[idx + 1])
        elif keyLength == 1 and valueLength != 1:
            self.__itemToList = lambda key, value: (key,) + value
            self.__listToItem = lambda values, idx: (values[idx], values[idx + 1:idx + valueLength + 1])
        elif keyLength != 1 and valueLength == 1:
            self.__itemToList = lambda key, value: key + (value,)
            self.__listToItem = lambda values, idx: (values[idx:idx + keyLength], values[idx + keyLength])
        else:
            self.__itemToList = lambda key, value: key + value
            self.__listToItem = lambda values, idx: (values[idx:idx + keyLength], values[idx + keyLength:idx + valueLength + keyLength])
        self.__data, self.__offsets = self.__unpack(compDescr)
        self.__changed = set()
        self.__added = set()

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        prevValue = self.__data.get(key, None)
        if value == prevValue:
            return
        else:
            self.__data[key] = value
            if prevValue is None:
                self.__added.add(key)
                _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_insert_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(key, value))
            elif key not in self.__added:
                self.__changed.add(key)
                _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_update_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(key, value, prevValue))
            _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get(key, []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(key, value, prevValue))
            return

    def __delitem__(self, key):
        del self.__data[key]
        self.__isExpanded = True
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_delete_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(key,))

    def clear(self):
        self.__data.clear()
        self.__isExpanded = True

    def __contains__(self, key):
        return key in self.__data

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return self.__data.iterkeys()

    def __str__(self):
        return str(self.__data)

    def get(self, key, default=None):
        return self.__data.get(key, default)

    def setdefault(self, key, default):
        value = self.__data.get(key, None)
        if value is not None:
            return value
        else:
            self[key] = default
            return default

    def pop(self, key, default=None):
        value = self.__data.get(key, None)
        if value is None:
            return default
        else:
            del self[key]
            return value

    def iteritems(self):
        return self.__data.iteritems()

    def iterkeys(self):
        return self.__data.iterkeys()

    def itervalues(self):
        return self.__data.itervalues()

    def items(self):
        return self.__data.items()

    def keys(self):
        return self.__data.keys()

    def values(self):
        return self.__data.values()

    def expand(self):
        self.__isExpanded = True
        return self

    def getChanges(self):
        return self.__changed

    def updateDossierCompDescr(self, dossierCompDescrArray, offset, size):
        data = self.__data
        length = len(data)
        newSize = length * self.__itemSize
        itemToList = self.__itemToList
        itemFormat = self.__itemFormat
        if self.__isExpanded:
            fmt = '<' + itemFormat * length
            values = []
            for key, value in data.iteritems():
                values += itemToList(key, value)

            if newSize == size:
                struct.pack_into(fmt, dossierCompDescrArray, offset, *values)
                return (dossierCompDescrArray, newSize)
            return (dossierCompDescrArray[:offset] + array('c', struct.pack(fmt, *values)) + dossierCompDescrArray[offset + size:], newSize)
        offsets = self.__offsets
        changed = self.__changed
        for key in changed:
            struct.pack_into(('<' + itemFormat), dossierCompDescrArray, (offset + offsets[key]), *itemToList(key, data[key]))

        changed.clear()
        added = self.__added
        itemSize = self.__itemSize
        if added:
            values = []
            recordOffset = size
            for key in added:
                values += itemToList(key, data[key])
                offsets[key] = recordOffset
                recordOffset += itemSize

            fmt = '<' + itemFormat * len(added)
            dossierCompDescrArray = dossierCompDescrArray[:offset + size] + array('c', struct.pack(fmt, *values)) + dossierCompDescrArray[offset + size:]
            added.clear()
        return (dossierCompDescrArray, newSize)

    def __unpack(self, compDescr):
        itemSize = self.__itemSize
        length = len(compDescr) / itemSize
        if length == 0:
            return ({}, {})
        data, offsets = {}, {}
        itemFormat = self.__itemFormat
        fmt = '<' + itemFormat * length
        values = struct.unpack(fmt, compDescr)
        itemLength = len(itemFormat)
        idx = 0
        listToItem = self.__listToItem
        for i in xrange(length):
            key, value = listToItem(values, idx)
            idx += itemLength
            data[key] = value
            offsets[key] = i * itemSize

        return (data, offsets)


class ListDossierBlockDescr(object):
    eventsEnabled = True

    def __init__(self, name, dossierDescr, compDescr, eventsHandlers, itemFormat):
        self.name = name
        self.__dossierDescrRef = weakref.ref(dossierDescr)
        self.__eventsHandlers = eventsHandlers
        self.__itemFormat = itemFormat
        self.__itemSize = struct.calcsize('<' + self.__itemFormat)
        self.__isExpanded = False
        itemLength = len(self.__itemFormat)
        if itemLength == 1:
            self.__itemToList = lambda item: [item]
            self.__listToItem = lambda values, idx: values[idx]
        else:
            self.__itemToList = lambda item: item
            self.__listToItem = lambda values, idx: values[idx:idx + itemLength]
        self.__list = self.__unpack(compDescr)
        self.__changed = set()

    def __getitem__(self, i):
        return self.__list[i]

    def __setitem__(self, i, value):
        if not isinstance(i, slice):
            prevValue = self.__list[i]
            if value == prevValue:
                return
            self.__list[i] = value
            self.__changed.add(i)
        else:
            self.__list[i] = value
            self.__isExpanded = True
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_set_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(i, value))

    def __delitem__(self, index):
        del self.__list[index]
        self.__isExpanded = True
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_del_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(index,))

    def __len__(self):
        return len(self.__list)

    def __iter__(self):
        return iter(self.__list)

    def __str__(self):
        return str(self.__list)

    def append(self, value):
        self.__list.append(value)
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_append_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value,))

    def extend(self, value):
        self.__list.extend(value)
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_extend_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value,))

    def remove(self, value):
        self.__list.remove(value)
        self.__isExpanded = True
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_remove_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value,))

    def clear(self):
        self.__list[:] = []
        self.__isExpanded = True
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_clear_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=())

    def count(self, value):
        return self.__list.count(value)

    def expand(self):
        self.__isExpanded = True
        return self

    def getChanges(self):
        return self.__changed

    def updateDossierCompDescr(self, dossierCompDescrArray, offset, size):
        itemSize = self.__itemSize
        length = size / itemSize
        selfList = self.__list
        newLength = len(selfList)
        newSize = newLength * itemSize
        itemFormat = self.__itemFormat
        itemToList = self.__itemToList
        if self.__isExpanded:
            fmt = '<' + itemFormat * newLength
            values = []
            for item in selfList:
                values += itemToList(item)

            if newSize == size:
                struct.pack_into(fmt, dossierCompDescrArray, offset, *values)
                return (dossierCompDescrArray, newSize)
            return (dossierCompDescrArray[:offset] + array('c', struct.pack(fmt, *values)) + dossierCompDescrArray[offset + size:], newSize)
        changed = self.__changed
        for idx in changed:
            if idx < length:
                struct.pack_into(('<' + itemFormat), dossierCompDescrArray, (offset + idx * itemSize), *itemToList(selfList[idx]))

        changed.clear()
        added = selfList[length:]
        if added:
            values = []
            for item in added:
                values += itemToList(item)

            fmt = '<' + itemFormat * len(added)
            dossierCompDescrArray = dossierCompDescrArray[:offset + size] + array('c', struct.pack(fmt, *values)) + dossierCompDescrArray[offset + size:]
        return (dossierCompDescrArray, newSize)

    def __unpack(self, compDescr):
        data = []
        length = len(compDescr) / self.__itemSize
        if length == 0:
            return []
        fmt = '<' + self.__itemFormat * length
        values = struct.unpack(fmt, compDescr)
        itemLength = len(self.__itemFormat)
        idx = 0
        for i in xrange(length):
            data.append(self.__listToItem(values, idx))
            idx += itemLength

        return data


class BinarySetDossierBlockDescr(object):
    eventsEnabled = True

    def __init__(self, name, dossierDescr, blockCompDescr, eventHandlers, popUpRecords, valueNames, valueToPosition, logRecords):
        self.name = name
        self.__dossierDescrRef = weakref.ref(dossierDescr)
        self.__isExpanded = False
        self.__cache = None
        self.__values = valueNames
        self.__eventsHandlers = eventHandlers
        self.__popUpRecords = popUpRecords
        self.__logRecords = logRecords
        self.__valueToPosition = valueToPosition
        self.__unpackedData = self.__unpack(blockCompDescr)
        self.__cleanEmptyBytes()
        self.__changed = set()
        return

    def expand(self):
        self.__isExpanded = True
        return self

    def getChanges(self):
        return self.__changed

    def add(self, value):
        sizeDiff, byteNum, bitMask = self.__findSizeDiff(value)
        if sizeDiff:
            self.__unpackedData = self.__unpackedData + sizeDiff * [0]
        self.__unpackedData[byteNum] |= bitMask
        if self.__cache:
            self.__cache.add(value)
        if value in self.__popUpRecords:
            self.__dossierDescrRef().addPopUp(self.name, value, True, addLogRecord=False)
        if value in self.__logRecords:
            self.__dossierDescrRef().addLogRecord(self.name, value, True)
        self.__changed.add(value)
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_add_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value,))
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get(value, []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value, True))

    def remove(self, value):
        sizeDiff, byteNum, bitMask = self.__findSizeDiff(value)
        if sizeDiff:
            return
        self.__unpackedData[byteNum] &= ~bitMask
        if self.__cache:
            self.__cache.discard(value)
        self.__changed.add(value)
        if value in self.__popUpRecords:
            self.__dossierDescrRef().addPopUp(self.name, value, False, addLogRecord=False)
        if value in self.__logRecords:
            self.__dossierDescrRef().addLogRecord(self.name, value, False)
        packedDataSize = len(self.__unpackedData)
        if byteNum + 1 != packedDataSize:
            return
        self.__cleanEmptyBytes()
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get('_remove_', []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value,))
        _callEventHandlers(eventsEnabled=self.eventsEnabled, handlers=self.__eventsHandlers.get(value, []), dossierDescr=self.__dossierDescrRef(), dossierBlockDescr=self, args=(value, False))

    def __cleanEmptyBytes(self):
        packedDataSize = len(self.__unpackedData)
        for byteNum in reversed(range(packedDataSize)):
            if self.__unpackedData[byteNum]:
                return
            self.__unpackedData.pop()

    def __getitem__(self, value):
        return self.__contains__(value)

    def __setitem__(self, record, value):
        if bool(value):
            self.add(record)
        else:
            self.remove(record)

    def __contains__(self, value):
        if self.__cache:
            return value in self.__cache
        sizeDiff, byteNum, bitMask = self.__findSizeDiff(value)
        return False if sizeDiff else bool(self.__unpackedData[byteNum] & bitMask)

    def __findSizeDiff(self, value):
        byteNum, bitMask = self.__valueToPosition[value]
        sizeRequired = byteNum + 1
        packedDataSize = len(self.__unpackedData)
        return (max(sizeRequired - packedDataSize, 0), byteNum, bitMask)

    def __unpack(self, packedStr):
        if not packedStr:
            return []
        arraySize = len(packedStr)
        return list(struct.unpack('<%dB' % arraySize, packedStr))

    def __str__(self):
        return str(self.__toSet())

    def __iter__(self):
        return iter(self.__toSet())

    def __len__(self):
        return len(self.__toSet())

    def __toSet(self):
        if not self.__cache:
            self.__cache = set((possibleValue for possibleValue in self.__values if possibleValue in self))
        return self.__cache

    def updateDossierCompDescr(self, dossierCompDescrArray, offset, size):
        self.__changed.clear()
        data = self.__unpackedData
        newSize = len(data)
        _format = '<%dB' % newSize
        if size == newSize:
            struct.pack_into(_format, dossierCompDescrArray, offset, *data)
            return (dossierCompDescrArray, newSize)
        else:
            return (dossierCompDescrArray[:offset] + array('c', struct.pack(_format, *data)) + dossierCompDescrArray[offset + size:], newSize)


def _callEventHandlers(eventsEnabled, handlers, dossierDescr, dossierBlockDescr, args):
    if not eventsEnabled:
        return
    if not handlers:
        return
    isFromOutside = dossierDescr._dependentUpdates == 0
    dossierDescr._dependentUpdates += 1
    if dossierDescr._dependentUpdates >= 100:
        LOG_ERROR('Too many subsequent updates of dependent records')
        return
    for handler in handlers:
        handler(dossierDescr, dossierBlockDescr, *args)

    if isFromOutside:
        dossierDescr._dependentUpdates = 0
