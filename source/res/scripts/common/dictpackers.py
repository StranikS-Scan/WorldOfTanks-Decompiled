# Embedded file name: scripts/common/DictPackers.py
import copy
from debug_utils import *

def roundToInt(val):
    return int(round(val))


class DeltaPacker(object):

    def __init__(self, packPredicate = None):
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
                diff = v - s[index]
                ret[index + 1] = diff

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
        if isinstance(value, str):
            return value
        return value.pack()

    def unpack(self, value):
        return value


class DictPacker(object):

    def __init__(self, *metaData):
        self._metaData = tuple(metaData)

    def pack(self, dataDict):
        metaData = self._metaData
        l = [None] * len(metaData)
        for index, metaEntry in enumerate(metaData):
            try:
                name, transportType, default, packer, aggFunc = metaEntry
                default = copy.deepcopy(default)
                v = dataDict.get(name, default)
                if v is None:
                    pass
                elif v == default:
                    v = None
                elif packer is not None:
                    v = packer.pack(v)
                elif transportType is not None and type(v) is not transportType:
                    v = transportType(v)
                    if v == default:
                        v = None
                l[index] = v
            except Exception as e:
                LOG_ERROR('error while packing:', index, metaEntry, str(e))
                raise

        return l

    def unpack(self, dataList):
        ret = {}
        for index, meta in enumerate(self._metaData):
            val = dataList[index]
            name, _, default, packer, aggFunc = meta
            default = copy.deepcopy(default)
            if val is None:
                val = default
            elif packer is not None:
                val = packer.unpack(val)
            ret[name] = val

        return ret


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
        for index, value in enumerate(dataList):
            if value is not None:
                ret[self.__keys[index]] = value

        return ret


class MetaEntry(object):
    __slots__ = ('name', 'transportType', 'default', 'packer', 'aggFunc')

    def __init__(self, *data):
        self.name, self.transportType, default, self.packer, self.aggFunc = data
        self.default = copy.deepcopy(default)


class Meta(DictPacker):

    def __init__(self, *metaData):
        DictPacker.__init__(self, *metaData)
        self.__nameToIdx = dict(((value[0], index) for index, value in enumerate(self._metaData)))
        self.__names = set(self.__nameToIdx.keys())

    def names(self):
        return self.__names

    def indexOf(self, key):
        return self.__nameToIdx[key]

    def __add__(self, other):
        newMeta = self._metaData + other._metaData
        return Meta(*newMeta)

    def __iter__(self):
        return self._metaData.__iter__()

    def __len__(self):
        return len(self._metaData)

    def __getitem__(self, index):
        return MetaEntry(*self._metaData[index])
