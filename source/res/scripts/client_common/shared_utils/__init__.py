# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/__init__.py
import collections
import time
import itertools
import logging
import types
import weakref
from functools import partial
import typing
import BigWorld
from adisp import adisp_async
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple, Type, TypeVar, Union
    T = TypeVar('T')
    R = TypeVar('R')
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Callable, Iterable, List, Optional, Tuple, TypeVar, Union
    T = TypeVar('T')
    R = TypeVar('R')
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
        _logger.error('Cannot cancel BigWorld callback: incorrect callback ID.')


def prettyPrint(dictValue, sort_keys=True, indent=4):
    import json
    return json.dumps(dictValue, sort_keys=sort_keys, indent=indent)


def findFirst(function_or_None, sequence, default=None):
    return next(itertools.ifilter(function_or_None, sequence), default)


def first(sequence, default=None):
    return findFirst(None, sequence, default)


def safeIndexOf(item, collection, default=None):
    return collection.index(item) if item in collection else default


def collapseIntervals(sequence):
    result = []
    prevElement = []
    for periodStart, periodEnd in sorted(sequence):
        if prevElement and periodStart <= prevElement[1]:
            prevElement[1] = periodEnd
        prevElement = [periodStart, periodEnd]
        result.append(prevElement)

    return result


def getSafeFromCollection(lst, ndx, default=None):
    return lst[ndx] if 0 <= ndx < len(lst) else default


def allEqual(sequence, accessor=None):
    iterable = iter(sequence)
    try:
        first_ = next(iterable)
    except StopIteration:
        return True

    return all((accessor(first_) == accessor(rest) for rest in iterable)) if accessor else all((first_ == rest for rest in iterable))


class CONST_CONTAINER(object):
    __keyByValue = None

    @classmethod
    def getIterator(cls):
        attrs = itertools.chain.from_iterable([ c.__dict__.iteritems() for c in itertools.chain([cls], cls.__bases__) ])
        for k, v in attrs:
            if not k.startswith('_') and type(v) in ScalarTypes:
                yield (k, v)

    @classmethod
    def getKeyByValue(cls, value):
        cls.__doInit()
        return cls.__keyByValue.get(value)

    @classmethod
    def hasKey(cls, key):
        return key in dir(cls)

    @classmethod
    def hasValue(cls, value):
        cls.__doInit()
        return value in cls.__keyByValue

    @classmethod
    def ALL(cls):
        return tuple([ v for _, v in cls.getIterator() ])

    @classmethod
    def __doInit(cls):
        if cls.__keyByValue is None:
            cls.__keyByValue = dict(((v, k) for k, v in cls.getIterator()))
        return


def _getBitIndexesMap(capacity):
    result = {}
    for index in range(1, capacity + 1):
        key = (1 << index) - 1
        result[key] = index - 1

    return result


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
    def isBitSet(cls, number, bitIndex):
        return number & 1 << bitIndex > 0

    @classmethod
    def getSetBitsCount(cls, mask):
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
        counter = 0
        while number:
            if number & 1:
                yield counter
            counter += 1
            number >>= 1

    @classmethod
    def iterateInt64SetBitsIndexes(cls, number):
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


def updateDict(sourceDict, diffDict):
    for k, v in diffDict.iteritems():
        if isinstance(v, collections.Mapping):
            r = updateDict(sourceDict.get(k, {}), v)
            sourceDict[k] = r
        sourceDict[k] = diffDict[k]

    return sourceDict


def isDefaultDict(sourceDict, defaultDict):
    for k, v in defaultDict.iteritems():
        if k not in sourceDict:
            return False
        if sourceDict[k] != v:
            return False

    return True


def nextTick(func):

    def wrapper(*args, **kwargs):
        BigWorld.callback(0.01, lambda : func(*args, **kwargs))

    return wrapper


@adisp_async
def awaitNextFrame(callback):
    BigWorld.callback(0.0, partial(callback, None))
    return


def timeit(method):

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        rt = te - ts
        _logger.info('%s elapsed time: %s sec', method.__name__, rt)
        return result

    return timed


def inPercents(fraction, digitsToRound=1):
    return round(fraction * 100, digitsToRound)
