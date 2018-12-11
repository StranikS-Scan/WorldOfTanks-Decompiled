# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/__init__.py
import nations
from items import _xml
from constants import IS_CLIENT, ITEM_DEFS_PATH
from soft_exception import SoftException
if IS_CLIENT:
    import ResMgr
    from helpers import i18n
else:
    from realm_utils import ResMgr
_g_itemTypes = None
ITEM_TYPE_NAMES = ('_reserved', 'vehicle', 'vehicleChassis', 'vehicleTurret', 'vehicleGun', 'vehicleEngine', 'vehicleFuelTank', 'vehicleRadio', 'tankman', 'optionalDevice', 'shell', 'equipment', 'customizationItem')

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
EQUIPMENT_TYPE_NAMES = ('regular', 'battleBoosters', 'battleAbilities')

class EQUIPMENT_TYPES(dict):

    def __init__(self):
        super(dict, self).__init__()
        for idx, name in enumerate(EQUIPMENT_TYPE_NAMES):
            self[name] = idx
            setattr(self, name, idx)


EQUIPMENT_TYPES = EQUIPMENT_TYPES()

class ItemsPrices(object):

    def __init__(self, prices=None):
        self._itemsPriceInfo = {}
        if prices:
            self.update(prices)

    def __getitem__(self, descriptor):
        info = self.getPrices(descriptor)
        return self._tuplePrice(info)

    def __setitem__(self, descriptor, prices):
        if isinstance(prices, tuple):
            info = {}
            if prices[0] != 0:
                info['credits'] = prices[0]
            if prices[1] != 0:
                info['gold'] = prices[1]
            if len(prices) > 2:
                info['crystal'] = prices[2]
            self._itemsPriceInfo[descriptor] = info
        elif isinstance(prices, dict):
            self._itemsPriceInfo[descriptor] = prices
        else:
            raise TypeError('price info could be tuple or dict!')

    def __delitem__(self, descriptor):
        del self._itemsPriceInfo[descriptor]

    def __contains__(self, key):
        return key in self._itemsPriceInfo

    def __len__(self):
        return len(self._itemsPriceInfo)

    def get(self, key, defaultValue=None):
        return self.__getitem__(key) if key in self._itemsPriceInfo else defaultValue

    def items(self):
        return [ (compDescr, self._tuplePrice(prices)) for compDescr, prices in self._itemsPriceInfo.iteritems() ]

    def update(self, other):
        for d, p in other.iteritems():
            self.__setitem__(d, p)

    def getSpecialItemPrices(self, currencyCode):
        return {compDescr:prices for compDescr, prices in self._itemsPriceInfo.iteritems() if currencyCode in prices}

    @staticmethod
    def _tuplePrice(priceInfo):
        return (priceInfo.get('credits', 0), priceInfo.get('gold', 0))

    def getPrices(self, descriptor):
        return self._itemsPriceInfo[descriptor]

    def tryGetPrice(self, descriptor, defaultValue=None):
        return self._itemsPriceInfo.get(descriptor, defaultValue)

    def getPrice(self, descriptor, currencyCode):
        return self._itemsPriceInfo[descriptor].get(currencyCode, 0)

    def getCrystalPrice(self, descriptor):
        return self._itemsPriceInfo[descriptor].get('crystal', 0)

    def hasPriceIn(self, descriptor, currencyCode):
        return currencyCode in self._itemsPriceInfo[descriptor]

    def __repr__(self):
        return repr(self._itemsPriceInfo)

    def intersect(self, other):
        otherStorage = other._itemsPriceInfo
        result = {}
        for k, v in self._itemsPriceInfo.iteritems():
            if k in otherStorage and otherStorage[k] != v:
                result[k] = v

        return ItemsPrices(result)


def init(preloadEverything, pricesToCollect=None):
    global _g_itemTypes
    _g_itemTypes = _readItemTypes()
    if pricesToCollect is not None:
        pricesToCollect['itemPrices'] = ItemsPrices()
        pricesToCollect['vehiclesRentPrices'] = {}
        pricesToCollect['notInShopItems'] = set()
        pricesToCollect['vehiclesNotToBuy'] = set()
        pricesToCollect['vehiclesToSellForGold'] = set()
        pricesToCollect['vehicleSellPriceFactors'] = {}
        pricesToCollect['vehicleCamouflagePriceFactors'] = {}
        pricesToCollect['camouflagePriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopCamouflages'] = [ set() for x in nations.NAMES ]
        pricesToCollect['inscriptionGroupPriceFactors'] = [ {} for x in nations.NAMES ]
        pricesToCollect['notInShopInscriptionGroups'] = [ set() for x in nations.NAMES ]
        pricesToCollect['playerEmblemGroupPriceFactors'] = {}
        pricesToCollect['notInShopPlayerEmblemGroups'] = set()
    from items import stun
    stun.init()
    from items import vehicles
    vehicles.init(preloadEverything, pricesToCollect)
    from items import avatars
    avatars.init()
    from items import tankmen
    tankmen.init(preloadEverything)
    from items import ny19, collectibles
    collectibles.init()
    ny19.init()
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
                raise SoftException("value is not a 'compact descriptor'")
    else:
        itemTypeID = ord(compactDescr[0]) & 15
        if itemTypeID == 0:
            itemTypeID = ord(compactDescr[1])
    if itemTypeID >= len(ITEM_TYPE_NAMES):
        raise SoftException("value is not a 'compact descriptor'")
    return itemTypeID


def makeIntCompactDescrByID(itemTypeName, nationID, itemID):
    itemTypeID = ITEM_TYPES[itemTypeName]
    if itemTypeID <= 15:
        header = itemTypeID + (nationID << 4)
        return (itemID << 8) + header
    if itemTypeID <= 255:
        header = 0 + (nationID << 4)
        return (itemTypeID << 24) + (itemID << 8) + header


def parseIntCompactDescr(compactDescr):
    itemTypeID = compactDescr & 15
    if itemTypeID == 0:
        itemTypeID = compactDescr >> 24 & 255
    return (itemTypeID, compactDescr >> 4 & 15, compactDescr >> 8 & 65535)


def allianceFromVehicleCD(compactDescr):
    _, nation, _ = parseIntCompactDescr(compactDescr)
    return nations.NATION_TO_ALLIANCE_IDS_MAP[nation]


def getVehicleAlliance(vehTypeCompDescr):
    return nations.ALLIANCES_TAGS_ORDER[allianceFromVehicleCD(vehTypeCompDescr)]


def isFromSameAlliance(typeCD1, typeCD2):
    return allianceFromVehicleCD(typeCD1) == allianceFromVehicleCD(typeCD2)


def clearXMLCache():
    _xml.clearCaches()


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

        itemType = {'index': index,
         'tags': tags,
         'tagNames': tuple(tagNames)}
        if IS_CLIENT:
            itemType['userString'] = i18n.makeString(itemSection.readString('userString'))
            itemType['description'] = i18n.makeString(itemSection.readString('description'))
        res[name] = itemType

    section = None
    itemSection = None
    tagSection = None
    ResMgr.purge(xmlPath, True)
    return res


def decodeEnum(value, enum):
    result = []
    splitted = value.split()
    for item in splitted:
        try:
            itemValue = int(item)
        except:
            itemValue = getattr(enum, item, None)
            if not isinstance(itemValue, int):
                raise SoftException("Invalid item '{0}'".format(item))
            if itemValue is None or itemValue not in enum.RANGE:
                raise SoftException("Unsupported item '{0}'".format(item))

        if itemValue in result:
            raise SoftException('Duplicated item {0} with value {1}'.format(item, itemValue))
        result.append(itemValue)

    return (reduce(int.__or__, result, 0), tuple(splitted))
