# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/resource_helper.py
from contextlib import contextmanager
import ResMgr
from collections import namedtuple
import types
from debug_utils import LOG_CURRENT_EXCEPTION

class RESOURCE_ITEM_TYPE(object):
    BOOL = 'bool'
    INTEGER = 'int'
    FLOAT = 'float'
    STRING = 'string'
    URL = 'url'
    VECTOR2 = 'vector2'
    VECTOR3 = 'vector3'
    VECTOR4 = 'vector4'
    LIST = 'list'
    DICT = 'dict'
    SEQ_PAIRS = 'seq-pairs'


class ResourceError(Exception):

    def __init__(self, ctx, message):
        super(ResourceError, self).__init__()
        self.ctx = ctx
        self.message = message

    def __str__(self):
        return 'Error in {0:>s}. {1:>s}'.format(self.ctx, self.message)


class ResourceCtx(object):

    def __init__(self, filePath, xpath = None):
        super(ResourceCtx, self).__init__()
        self.__filePath = filePath
        if xpath is None:
            self.__xpath = []
        elif type(xpath) is types.ListType:
            self.__xpath = xpath
        else:
            raise ValueError, 'xpath must be list.'
        return

    def next(self, section):
        xpath = self.__xpath[:]
        if type(section) in types.StringTypes:
            xpath.append(section)
        else:
            xpath.append(section.name)
        return ResourceCtx(self.__filePath, xpath)

    def prev(self):
        return ResourceCtx(self.__filePath, self.__xpath[:-1])

    def __str__(self):
        path = self.__xpath[:]
        path.insert(0, self.__filePath)
        return '/'.join(path)


def getRoot(filePath, msg = '', safe = False):
    section = ResMgr.openSection(filePath)
    ctx = ResourceCtx(filePath)
    if section is None and safe:
        raise ResourceError(ctx, msg or 'File {0} is not found.'.format(filePath))
    return (ctx, section)


@contextmanager
def root_generator(filePath):
    try:
        ctx, section = getRoot(filePath)
    except ResourceError as error:
        raise error
    else:
        try:
            yield (ctx, section)
        except:
            LOG_CURRENT_EXCEPTION()
        finally:
            ResMgr.purge(filePath, True)


def getSubSection(ctx, section, name, safe = False):
    subSection = section[name]
    if subSection is None and not safe:
        raise ResourceError(ctx, 'Section {0} is not found.'.format(name))
    return (ctx.next(name), subSection)


def getIterator(xmlCtx, section):
    if section is None:
        raise ResourceError(xmlCtx, 'Section is not found')
    for _, subSection in section.items():
        yield (xmlCtx.next(subSection), subSection)

    return


def _readItemAttr(xmlCtx, section, attr, default = None, keys = None):
    if keys is None:
        keys = section.keys()
    if attr not in keys:
        value = default
        if default is None:
            raise ResourceError(xmlCtx, 'Attribute {0} is not found.'.format(attr))
    else:
        value = section[attr].asString
    return value


def _readItemName(xmlCtx, section, keys = None):
    return _readItemAttr(xmlCtx, section, 'name', default='', keys=keys)


def _readItemType(xmlCtx, section, keys = None):
    return _readItemAttr(xmlCtx, section, 'type', default='string', keys=keys)


_ResourceItem = namedtuple('_Item', ('type', 'name', 'value'))

def readBoolItem(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readBool('value')
    else:
        value = section.asBool
    return _ResourceItem(RESOURCE_ITEM_TYPE.BOOL, _readItemName(xmlCtx, section), value)


def readIntItem(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readInt('value')
    else:
        value = section.asInt
    return _ResourceItem(RESOURCE_ITEM_TYPE.INTEGER, _readItemName(xmlCtx, section), value)


def readFloatItem(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readFloat('value')
    else:
        value = section.asFloat
    return _ResourceItem(RESOURCE_ITEM_TYPE.FLOAT, _readItemName(xmlCtx, section), value)


def readStringItem(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readString('value')
    else:
        value = section.asString
    return _ResourceItem(RESOURCE_ITEM_TYPE.STRING, _readItemName(xmlCtx, section), value)


def readVector2Item(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readVector2('value')
    else:
        value = section.asVector2
    return _ResourceItem(RESOURCE_ITEM_TYPE.VECTOR2, _readItemName(xmlCtx, section), value)


def readVector3Item(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readVector3('value')
    else:
        value = section.asVector3
    return _ResourceItem(RESOURCE_ITEM_TYPE.VECTOR3, _readItemName(xmlCtx, section), value)


def readVector4Item(xmlCtx, section):
    if 'value' in section.keys():
        value = section.readVector4('value')
    else:
        value = section.asVector4
    return _ResourceItem(RESOURCE_ITEM_TYPE.VECTOR4, _readItemName(xmlCtx, section), value)


def readList(xmlCtx, section, valueName = 'value'):
    result = []
    name = _readItemName(xmlCtx, section)
    subCtx, subSection = getSubSection(xmlCtx, section, valueName)
    for nextCtx, nextSection in getIterator(subCtx, subSection):
        result.append(readItem(nextCtx, nextSection).value)

    return _ResourceItem(RESOURCE_ITEM_TYPE.LIST, name, result)


def readDict(xmlCtx, section, valueName = 'value'):
    result = {}
    name = _readItemName(xmlCtx, section)
    subCtx, subSection = getSubSection(xmlCtx, section, valueName)
    for nextCtx, nextSection in getIterator(subCtx, subSection):
        item = readItem(nextCtx, nextSection)
        if not item.name:
            raise ResourceError(nextCtx, '{0}: name is required in each item'.format(name))
        result[item.name] = item.value

    return _ResourceItem(RESOURCE_ITEM_TYPE.DICT, name, result)


def readSeqPairs(xmlCtx, section, valueName = 'value'):
    result = []
    name = _readItemName(xmlCtx, section)
    subCtx, subSection = getSubSection(xmlCtx, section, valueName)
    for nextCtx, nextSection in getIterator(subCtx, subSection):
        item = readItem(nextCtx, nextSection)
        result.append((item.name, item.value))

    return _ResourceItem(RESOURCE_ITEM_TYPE.SEQ_PAIRS, name, tuple(result))


_ITEM_VALUE_READERS = {RESOURCE_ITEM_TYPE.BOOL: readBoolItem,
 RESOURCE_ITEM_TYPE.INTEGER: readIntItem,
 RESOURCE_ITEM_TYPE.FLOAT: readFloatItem,
 RESOURCE_ITEM_TYPE.STRING: readStringItem,
 RESOURCE_ITEM_TYPE.URL: readStringItem,
 RESOURCE_ITEM_TYPE.VECTOR2: readVector2Item,
 RESOURCE_ITEM_TYPE.VECTOR3: readVector3Item,
 RESOURCE_ITEM_TYPE.VECTOR4: readVector4Item,
 RESOURCE_ITEM_TYPE.LIST: readList,
 RESOURCE_ITEM_TYPE.DICT: readDict,
 RESOURCE_ITEM_TYPE.SEQ_PAIRS: readSeqPairs}

def readItem(ctx, section, name = 'item'):
    if section.name != name:
        raise ResourceError(ctx, 'Resource {0} is invalid'.format(section.name))
    keys = section.keys()
    itemType = _readItemType(ctx, section, keys=keys)
    name = _readItemName(ctx, section, keys=keys)
    if itemType in _ITEM_VALUE_READERS:
        reader = _ITEM_VALUE_READERS[itemType]
        assert reader, 'Reader of type {0} must be defined'.format(itemType)
        item = reader(ctx, section)
    else:
        raise ResourceError(ctx, '"{0}: type {1} is invalid.'.format(name, itemType))
    return item
