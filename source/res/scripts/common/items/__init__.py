# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/__init__.py
# Compiled at: 2011-10-21 19:10:55
import ResMgr
import struct
from types import IntType
from items import _xml
from constants import IS_CLIENT, ITEM_DEFS_PATH
if IS_CLIENT:
    from helpers import i18n
ITEM_TYPE_NAMES = ('reserved', 'vehicle', 'vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'tankman', 'optionalDevice', 'shell', 'equipment')
MAX_ITEM_TYPE_INDEX = len(ITEM_TYPE_NAMES) - 1
ITEM_TYPE_INDICES = dict(((x[1], x[0]) for x in enumerate(ITEM_TYPE_NAMES)))
SIMPLE_ITEM_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'optionalDevice', 'shell', 'equipment')
SIMPLE_ITEM_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in SIMPLE_ITEM_TYPE_NAMES))
VEHICLE_COMPONENT_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio')
VEHICLE_COMPONENT_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in SIMPLE_ITEM_TYPE_NAMES))

def init(preloadEverything):
    global _g_itemTypes
    _g_itemTypes = _readItemTypes()
    from items import vehicles
    vehicles.init(preloadEverything)
    from items import tankmen
    tankmen.init(preloadEverything)


def getTypeInfoByName(typeName):
    return _g_itemTypes[typeName]


def getTypeInfoByIndex(typeIndex):
    return _g_itemTypes[ITEM_TYPE_NAMES[typeIndex]]


def getTypeOfCompactDescr(compactDescr):
    if type(compactDescr) is IntType:
        typeID = compactDescr & 15
    else:
        typeID = struct.unpack('B', compactDescr[0:1]) & 15
    if typeID >= len(ITEM_TYPE_NAMES):
        raise Exception, "is not a 'compact descriptor'"
    return typeID


def _readItemTypes():
    xmlPath = ITEM_DEFS_PATH + 'item_types.xml'
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = {}
    for index, name in enumerate(ITEM_TYPE_NAMES):
        if name == 'reserved':
            continue
        itemSection = _xml.getSubsection(xmlCtx, section, name)
        ctx = (xmlCtx, name)
        tagNames = []
        tags = {}
        if itemSection.has_key('tags'):
            for tagSection in itemSection['tags'].values():
                tagName = intern(tagSection.name)
                if tags.has_key(tagName):
                    _xml.raiseWrongXml(xmlCtx, 'tags' + tagName, 'tag name is not unique')
                tagDescr = {'name': tagName,
                 'index': len(tagNames)}
                if IS_CLIENT:
                    tagDescr['userString'] = i18n.makeString(tagSection.readString('userString'))
                    tagDescr['description'] = i18n.makeString(tagSection.readString('description'))
                tags[tagName] = tagDescr
                tagNames.append(tagName)

        descr = {'index': index,
         'tags': tags,
         'tagNames': tuple(tagNames)}
        if IS_CLIENT:
            descr['userString'] = i18n.makeString(itemSection.readString('userString'))
            descr['description'] = i18n.makeString(itemSection.readString('description'))
        res[name] = descr

    section = None
    itemSection = None
    tagSection = None
    ResMgr.purge(xmlPath, True)
    return res
