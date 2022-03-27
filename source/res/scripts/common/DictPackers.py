# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/DictPackers.py
import copy
from debug_utils import LOG_ERROR
from binascii import crc32
from functools import partial

def roundToInt(val):
    return int(round(val))


class DeltaPacker(object):

    def __init__(self, packPredicate=None):
        self.packPredicate = packPredicate

    def pack(self, seq):
        if len(seq) == 0:
            return seq
        else:
            ret = [None] * len(seq)
            s = sorted(seq)
            if self.packPredicate:
                p = self.packPredicate
                s = [ p(v) for v in s ]
            ret[0] = s[0]
            for index, v in enumerate(s[1:]):
                ret[index + 1] = v - s[index]

            return ret

    def unpack(self, seq):
        if len(seq) == 0:
            return seq
        else:
            ret = [None] * len(seq)
            ret[0] = seq[0]
            for index in xrange(1, len(seq)):
                ret[index] = ret[index - 1] + seq[index]

            return ret


class ValueReplayPacker:

    def pack(self, value):
        return value if isinstance(value, str) else value.pack()

    def unpack(self, value):
        return value


class DictPacker(object):

    def __init__(self, *metaData):
        self._metaData = tuple(metaData)
        self._checksum = self.checksum(self._metaData)

    def pack(self, dataDict):
        metaData = self._metaData
        l = [None] * (len(metaData) + 1)
        l[0] = self._checksum
        for index, metaEntry in enumerate(metaData):
            try:
                name, transportType, default, packer, aggFunc = metaEntry
                v = dataDict.get(name, default)
                if v is None:
                    pass
                elif v == default:
                    v = None
                elif packer is not None:
                    v = packer.pack(v)
                elif transportType is not None and not isinstance(v, transportType):
                    v = transportType(v)
                    if v == default:
                        v = None
                l[index + 1] = v
            except Exception as e:
                LOG_ERROR('error while packing:', index, metaEntry, str(e))
                raise

        return l

    def unpack(self, dataList):
        ret = {}
        if len(dataList) == 0 or dataList[0] != self._checksum:
            return
        else:
            getDefaultValue = self.getDefaultValue
            for index, meta in enumerate(self._metaData):
                val = dataList[index + 1]
                name, _, _, packer, _ = meta
                if val is None:
                    val = getDefaultValue(index)
                elif packer is not None:
                    val = packer.unpack(val)
                ret[name] = val

            return ret

    def getChecksum(self):
        return self._checksum

    def getDefaultValue(self, index):
        _, _, default, _, _ = self._metaData[index]
        return copy.deepcopy(default)

    @staticmethod
    def checksum(metaData):
        meta_descriptor = []
        for entry in tuple(metaData):
            name, entry_type, default, packer, aggregatorName = entry
            meta_descriptor.append(''.join([name,
             str(entry_type),
             str(default),
             str(type(packer)),
             str(aggregatorName)]))

        return crc32(''.join(meta_descriptor))


class SimpleDictPacker(object):

    def __init__(self, packPredicate, keys):
        self.__packPredicate = packPredicate
        self.__keys = tuple(keys)

    def pack(self, dataDict):
        packPredicate = self.__packPredicate
        ret = [None] * len(self.__keys)
        for index, key in enumerate(self.__keys):
            val = dataDict.get(key, None)
            if val is not None:
                val = packPredicate(val)
            ret[index] = val

        return ret

    def unpack(self, dataList):
        ret = {}
        keys = self.__keys
        for index, value in enumerate(dataList):
            if value is not None:
                ret[keys[index]] = value

        return ret


class Meta(DictPacker):

    def __init__(self, *metaData):
        DictPacker.__init__(self, *metaData)
        self.__nameToData = {name:(index,
         transportType,
         default,
         packer,
         aggFunc) for index, (name, transportType, default, packer, aggFunc) in enumerate(self._metaData)}
        self.__names = set(self.__nameToData.keys())
        self.__initDefaults()

    def names(self):
        return self.__names

    def defaults(self):
        result = self.__defaultsImmutable.copy()
        for key, value in self.__defaultsMutable.iteritems():
            result[key] = value()

        return result

    def indexOf(self, name):
        return self.__nameToData[name][0]

    def nameOf(self, index):
        return self._metaData[index][0]

    def getDataByName(self, name):
        return self.__nameToData[name]

    def getDefaultValue(self, index):
        name, _, _, _, _ = self._metaData[index]
        return self.getDefaultValueByName(name)

    def getDefaultValueByName(self, name):
        return self.__defaultsImmutable[name] if name in self.__defaultsImmutable else self.__defaultsMutable[name]()

    def __add__(self, other):
        newMeta = self._metaData + other._metaData
        return Meta(*newMeta)

    def __iter__(self):
        return self._metaData.__iter__()

    def __len__(self):
        return len(self._metaData)

    def __initDefaults(self):
        self.__defaultsImmutable = defaultsImmutable = {}
        self.__defaultsMutable = defaultsMutable = {}
        for name, transportType, default, _, _ in self._metaData:
            mutableType = getMutability(transportType, default)
            if mutableType == 'immutable':
                defaultsImmutable[name] = default
            if mutableType == 'mutableList':
                defaultsMutable[name] = partial(lambda x: x[:], default)
            if mutableType == 'mutableDeep':
                defaultsMutable[name] = partial(copy.deepcopy, default)
            if mutableType == 'mutableCopy':
                defaultsMutable[name] = partial(lambda x: x.copy(), default)
            raise KeyError(mutableType)


def getMutability(transportType, default):
    if transportType in (int,
     float,
     str,
     bool,
     None):
        return 'immutable'
    else:
        if transportType in (list, tuple, set):
            if all((getMutability(type(value), value) == 'immutable' for value in default)):
                if transportType == list:
                    return 'mutableList'
                if transportType == tuple:
                    return 'immutable'
                return 'mutableCopy'
        return 'mutableDeep' if default or transportType != dict else 'mutableCopy'
