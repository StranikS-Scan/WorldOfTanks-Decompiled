# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/__init__.py
import ResMgr
import nations
from items import _xml
from constants import IS_CLIENT, ITEM_DEFS_PATH
if IS_CLIENT:
    from helpers import i18n
ITEM_TYPE_NAMES = ('_reserved', 'vehicle', 'vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'tankman', 'optionalDevice', 'shell', 'equipment')

class ITEM_TYPES(dict):

    def __init__(self):
        super(dict, self).__init__()
        for idx, name in enumerate(ITEM_TYPE_NAMES):
            if not name.startswith('_'):
                self[name] = idx
                setattr(self, name, idx)


ITEM_TYPES = ITEM_TYPES()
ITEM_TYPE_INDICES = ITEM_TYPES
SIMPLE_ITEM_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'optionalDevice', 'shell', 'equipment')
SIMPLE_ITEM_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in SIMPLE_ITEM_TYPE_NAMES))
VEHICLE_COMPONENT_TYPE_NAMES = ('vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio')
VEHICLE_COMPONENT_TYPE_INDICES = tuple((ITEM_TYPE_INDICES[x] for x in VEHICLE_COMPONENT_TYPE_NAMES))

def init(preloadEverything, pricesToCollect=None):
    global _g_itemTypes
    _g_itemTypes = _readItemTypes()
    if pricesToCollect is not None:
        pricesToCollect['itemPrices'] = {}
        pricesToCollect['vehiclesRentPrices'] = {}
        pricesToCollect['notInShopItems'] = set()
        pricesToCollect['vehiclesNotToBuy'] = set()
        pricesToCollect['vehiclesToSellForGold'] = set()
        pricesToCollect['vehicleSellPriceFactors'] = {}
        pricesToCollect['vehicleCamouflagePriceFactors'] = {}
        pricesToCollect['vehicleHornPriceFactors'] = {}
        pricesToCollect['hornPrices'] = {}
        pricesToCollect['camouflagePriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopCamouflages'] = [ set() for x in nations.NAMES ]
        pricesToCollect['inscriptionGroupPriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopInscriptionGroups'] = [ set() for x in nations.NAMES ]
        pricesToCollect['playerEmblemGroupPriceFactors'] = {}
        pricesToCollect['notInShopPlayerEmblemGroups'] = set()
    from items import vehicles
    vehicles.init(preloadEverything, pricesToCollect)
    from items import tankmen
    tankmen.init(preloadEverything)
    from . import qualifiers
    qualifiers.init()
    return


def getTypeInfoByName(typeName):
    return _g_itemTypes[typeName]


def getTypeInfoByIndex(typeIndex):
    return _g_itemTypes[ITEM_TYPE_NAMES[typeIndex]]


def getTypeOfCompactDescr(compactDescr):
    cdType = type(compactDescr)
    if cdType is int or cdType is long:
        itemTypeID = int(compactDescr & 15)
        if itemTypeID == 0:
            itemTypeID = int(compactDescr >> 24 & 255)
            if 0 != itemTypeID <= 15:
                raise Exception("value is not a 'compact descriptor'")
    else:
        itemTypeID = ord(compactDescr[0]) & 15
        if itemTypeID == 0:
            itemTypeID = ord(compactDescr[1])
    if itemTypeID >= len(ITEM_TYPE_NAMES):
        raise Exception("value is not a 'compact descriptor'")
    return itemTypeID


def makeIntCompactDescrByID(itemTypeName, nationID, itemID):
    assert 0 <= itemID <= 65535
    assert 0 <= nationID <= 15
    itemTypeID = ITEM_TYPES[itemTypeName]
    if itemTypeID <= 15:
        header = itemTypeID + (nationID << 4)
        return (itemID << 8) + header
    if itemTypeID <= 255:
        header = 0 + (nationID << 4)
        return (itemTypeID << 24) + (itemID << 8) + header
    assert False


def parseIntCompactDescr(compactDescr):
    itemTypeID = compactDescr & 15
    if itemTypeID == 0:
        itemTypeID = compactDescr >> 24 & 255
    return (itemTypeID, compactDescr >> 4 & 15, compactDescr >> 8 & 65535)


def _readItemTypes():
    xmlPath = ITEM_DEFS_PATH + 'item_types.xml'
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = {}
    for index, name in enumerate(ITEM_TYPE_NAMES):
        if name.startswith('_'):
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
