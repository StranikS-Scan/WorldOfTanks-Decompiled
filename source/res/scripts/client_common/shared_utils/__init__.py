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
        self.wrefCls = weakref.ref(func.__self__)

    def __call__(self, *args, **kwargs):
        return getattr(self.wrefCls(), self.methodName)(*args, **kwargs)


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


def prettyPrint(dict, sort_keys = True, indent = 4):
    import json
    return json.dumps(dict, sort_keys=sort_keys, indent=indent)


def findFirst(function_or_None, sequence, default = None):
    try:
        return next(itertools.ifilter(function_or_None, sequence))
    except StopIteration:
        return default


def first(sequence, default = None):
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


class BitmaskHelper(object):

    @classmethod
    def add(cls, mask, flag):
        if not mask & flag:
            mask |= flag
            return mask
        return -1

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
        return -1

    @classmethod
    def removeIfHas(cls, mask, flag):
        if mask & flag > 0:
            mask ^= flag
        return mask


class AlwaysValidObject(object):

    def __init__(self, name = ''):
        self.__name = name

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        return AlwaysValidObject(self._makeName(self.__name, item))

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
