# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/enumerations.py
from debug_utils import deprecated, LOG_DEBUG
import types, exceptions

class EnumException(exceptions.Exception):
    pass


class EnumItem(object):

    def __init__(self, name, index, *args, **kwargs):
        self.__name = name
        self.__index = index

    def index(self):
        return self.__index

    def name(self):
        return self.__name

    def __repr__(self):
        return self.name()

    def __eq__(self, other):
        return other and self.__name == other.name() and self.__index == other.index()


class CallabbleEnumItem(EnumItem):

    def __init__(self, name, index, func, *args, **kwargs):
        super(CallabbleEnumItem, self).__init__(name, index, func, *args, **kwargs)
        self.__function = func

    def __call__(self, *args, **kwargs):
        return self.__function(*args, **kwargs)


class AttributeEnumItem(EnumItem):

    def __init__(self, name, index, data, *args, **kwargs):
        super(AttributeEnumItem, self).__init__(name, index, data, *args, **kwargs)
        self.__data = data

    def get(self, attr, defval = None):
        return self.__data.get(attr, defval)

    def __getattr__(self, attr):
        if not self.__data.has_key(attr):
            raise AttributeError, 'Must be %s' % ', '.join(self.__data)
        return self.__data[attr]


class Enumeration:

    def __init__(self, name, enumList, instance = EnumItem):
        self.__doc__ = name
        lookup = {}
        idxLookup = {}
        uniqueNames = []

        def appendEnumItem(idx, enumItem):
            if type(enumItem) == types.TupleType:
                x = enumItem[0:1]
            else:
                x = enumItem
            if type(x) != types.StringType:
                raise EnumException, 'enum name is not a string: ' + x
            if x in uniqueNames:
                raise EnumException, 'enum name is not unique: ' + x
            if idx in idxLookup:
                raise EnumException, 'index %s is not unique: ' % (idx,)
            uniqueNames.append(x)
            args = (x, idx) + tuple(enumItem[1:])
            item = instance(*args)
            lookup[x] = item
            idxLookup[item.index()] = item

        if isinstance(enumList, dict):
            for idx, enumItem in enumList.items():
                appendEnumItem(idx, enumItem)

        else:
            i = 0
            for e in enumList:
                appendEnumItem(i, e)
                i += 1

        self.__lookup = lookup
        self.__idxLookup = idxLookup

    def __getattr__(self, attr):
        if attr not in self.__lookup:
            raise AttributeError, "Attr '%s' must be in (%s)" % (attr, ', '.join(self.__lookup))
        return self.__lookup[attr]

    def __getitem__(self, idx):
        return self.__idxLookup.get(idx, None)

    def __iter__(self):
        return iter(self.__lookup)

    def all(self):
        return self.__lookup.values()

    def keys(self):
        return self.__lookup.keys()

    def of(self, name):
        return self.__getattr__(name)

    def lookup(self, name):
        return self.__lookup.get(name, None)
