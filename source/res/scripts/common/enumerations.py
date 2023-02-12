# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/enumerations.py
import types
from soft_exception import SoftException

class EnumException(SoftException):
    pass


class EnumItem(object):
    __slots__ = ('__name', '__index')

    def __init__(self, name, index, *args, **kwargs):
        super(EnumItem, self).__init__()
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
    __slots__ = ('__function',)

    def __init__(self, name, index, func, *args, **kwargs):
        super(CallabbleEnumItem, self).__init__(name, index, func, *args, **kwargs)
        self.__function = func

    def __call__(self, *args, **kwargs):
        return self.__function(*args, **kwargs)


class AttributeEnumItem(EnumItem):
    __slots__ = ('__data',)

    def __init__(self, name, index, data, *args, **kwargs):
        super(AttributeEnumItem, self).__init__(name, index, data, *args, **kwargs)
        self.__data = data

    def get(self, attr, defval=None):
        return self.__data.get(attr, defval)

    def __getattr__(self, attr):
        if attr not in self.__data:
            raise AttributeError('Must be %s' % ', '.join(self.__data))
        return self.__data[attr]


class Enumeration(object):
    __slots__ = ('__doc__', '__lookup', '__idxLookup')

    def __init__(self, name, enumList, instance=EnumItem):
        super(Enumeration, self).__init__()
        self.__doc__ = name
        self.__lookup = {}
        self.__idxLookup = {}
        self.__appendEnumItems(enumList, instance)

    def __getattr__(self, attr):
        if attr not in self.__lookup:
            raise AttributeError("Attr '%s' must be in (%s)" % (attr, ', '.join(self.__lookup)))
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

    def inject(self, enumList, instance=EnumItem):
        self.__appendEnumItems(enumList, instance)

    def __appendEnumItems(self, enumList, instance):
        uniqueNames = set(self.__lookup.iterkeys())
        if isinstance(enumList, dict):
            for idx, enumItem in enumList.iteritems():
                self.__appendEnumItem(idx, enumItem, instance, uniqueNames)

        else:
            i = max(self.__idxLookup.iterkeys()) + 1 if self.__idxLookup else 0
            for e in enumList:
                self.__appendEnumItem(i, e, instance, uniqueNames)
                i += 1

        uniqueNames.clear()

    def __appendEnumItem(self, idx, enumItem, instance, uniqueNames):
        if isinstance(enumItem, types.TupleType):
            x = enumItem[0:1]
        else:
            x = enumItem
        if not isinstance(x, types.StringType):
            raise EnumException('enum name is not a string: {}'.format(x))
        if x in uniqueNames:
            raise EnumException('enum name is not unique: ' + x)
        if idx in self.__idxLookup:
            raise EnumException('index %s is not unique: ' % (idx,))
        uniqueNames.add(x)
        args = (x, idx) + tuple(enumItem[1:])
        item = instance(*args)
        self.__lookup[x] = item
        self.__idxLookup[item.index()] = item
