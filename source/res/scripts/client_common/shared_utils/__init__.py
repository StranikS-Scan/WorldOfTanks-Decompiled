# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/__init__.py
import weakref
import itertools
import types
import BigWorld
from debug_utils import LOG_ERROR, LOG_WARNING
ScalarTypes = (types.IntType,
 types.LongType,
 types.FloatType,
 types.BooleanType) + types.StringTypes
IntegralTypes = (types.IntType, types.LongType)

def makeTupleByDict(ntClass, data):
    unsupportedFields = set(data) - set(ntClass._fields)
    supported = {}
    for k, v in data.iteritems():
        if k not in unsupportedFields:
            supported[k] = v

    return ntClass(**supported)


class BoundMethodWeakref(object):

    def __init__(self, func):
        self.methodName = func.__name__
        assert not self.methodName.startswith('__'), 'BoundMethodWeakref: private methods are not supported'
        self.wrefCls = weakref.ref(func.__self__)

    def __call__(self, *args, **kwargs):
        ref = self.wrefCls()
        return getattr(ref, self.methodName)(*args, **kwargs) if ref is not None else None


def forEach(function, sequence):
    for e in sequence:
        function(e)


def isEmpty(sequence):
    try:
        next(sequence)
    except StopIteration:
        return True

    return False


def safeCancelCallback(callbackID):
    try:
        BigWorld.cancelCallback(callbackID)
    except ValueError:
        LOG_ERROR('Cannot cancel BigWorld callback: incorrect callback ID.')


def prettyPrint(dict, sort_keys=True, indent=4):
    import json
    return json.dumps(dict, sort_keys=sort_keys, indent=indent)


def findFirst(function_or_None, sequence, default=None):
    try:
        return next(itertools.ifilter(function_or_None, sequence))
    except StopIteration:
        return default


def first(sequence, default=None):
    return findFirst(None, sequence, default)


class CONST_CONTAINER(object):
    __keyByValue = None

    @classmethod
    def getIterator(cls):
        for k, v in cls.__dict__.iteritems():
            if not k.startswith('_') and type(v) in ScalarTypes:
                yield (k, v)

    @classmethod
    def getKeyByValue(cls, value):
        cls.__doInit()
        return cls.__keyByValue.get(value)

    @classmethod
    def hasKey(cls, key):
        return key in cls.__dict__

    @classmethod
    def hasValue(cls, value):
        cls.__doInit()
        return value in cls.__keyByValue

    @classmethod
    def ALL(cls):
        return tuple([ v for k, v in cls.getIterator() ])

    @classmethod
    def __doInit(cls):
        if cls.__keyByValue is None:
            cls.__keyByValue = dict(((v, k) for k, v in cls.getIterator()))
        return


def _getBitIndexesMap(capacity):
    map = {}
    for index in range(1, capacity + 1):
        key = (1 << index) - 1
        map[key] = index - 1

    return map


_INT64_SET_BITS_INDEXES_MAP = _getBitIndexesMap(64)

class BitmaskHelper(object):

    @classmethod
    def add(cls, mask, flag):
        if not mask & flag:
            mask |= flag
            return mask

    @classmethod
    def addIfNot(cls, mask, flag):
        if not mask & flag:
            mask |= flag
        return mask

    @classmethod
    def remove(cls, mask, flag):
        if mask & flag > 0:
            mask ^= flag
            return mask

    @classmethod
    def removeIfHas(cls, mask, flag):
        if mask & flag > 0:
            mask ^= flag
        return mask

    @classmethod
    def hasAllBitsSet(cls, number, mask):
        return number & mask == mask

    @classmethod
    def hasAnyBitSet(cls, number, mask):
        return number & mask > 0

    @classmethod
    def isBitSet(self, number, bitIndex):
        return number & 1 << bitIndex > 0

    @classmethod
    def getSetBitsCount(cls, mask):
        """
        Method goes through as many iterations as there are set bits. So if we have a 32-bit word
        with only the high bit set, then it will only go once through the loop.
        For details please see Brian Kernighan's algorithm.
        :param mask: Bit mask
        :return: Count of set bits
        """
        count = 0
        while mask:
            count += 1
            mask &= mask - 1

        return count

    @classmethod
    def getSetBitIndexes(cls, mask):
        return [ i for i in BitmaskHelper.iterateSetBitsIndexes(mask) ]

    @classmethod
    def iterateSetBitsIndexes(cls, number):
        """
        Generator that returns indexes of set bits of the given number. Does NOT depend on number
        bit capacity.
        NOTE: If known that bit capacity <= INT64, use iterateInt64SetBitsIndexes because
        it is faster on 25-30%.
        :param number: Bit mask
        :return: Indexes of set bits starting from 0
        """
        counter = 0
        while number:
            if number & 1:
                yield counter
            counter += 1
            number >>= 1

    @classmethod
    def iterateInt64SetBitsIndexes(cls, number):
        """
        Generator that returns indexes of set bits of the given INT64. Depends on number
        bit capacity (=64!). Generator goes through as many iterations as there are set bits.
        NOTE: It faster on 25-30% than iterateSetBitsIndexes!
        :param number: Bit mask
        :return: Indexes of set bits starting from 0
        """
        while number:
            submask = number - 1
            yield _INT64_SET_BITS_INDEXES_MAP[number ^ submask]
            number &= submask


class AlwaysValidObject(object):

    def __init__(self, name=''):
        self.__name = name

    def __getattr__(self, item):
        return self.__dict__[item] if item in self.__dict__ else AlwaysValidObject(self._makeName(self.__name, item))

    def __call__(self, *args, **kwargs):
        return AlwaysValidObject()

    def getName(self):
        return self.__name

    @classmethod
    def _makeName(cls, parentName, nodeName):
        return '%s/%s' % (parentName, nodeName)


def isDefaultDict(sourceDict, defaultDict):
    for k, v in defaultDict.iteritems():
        if k not in sourceDict:
            return False
        if sourceDict[k] != v:
            return False

    return True


def nextTick(func):
    """
    Moves function calling to the next frame
    """

    def wrapper(*args, **kwargs):
        BigWorld.callback(0.01, lambda : func(*args, **kwargs))

    return wrapper
