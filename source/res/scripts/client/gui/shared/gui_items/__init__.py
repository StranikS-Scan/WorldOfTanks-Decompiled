# Embedded file name: scripts/client/gui/shared/gui_items/__init__.py
import nations
from collections import namedtuple
from debug_utils import *
from helpers import i18n, time_utils
from items import ITEM_TYPE_NAMES, vehicles, getTypeInfoByName, ITEM_TYPE_INDICES
from shared_utils import CONST_CONTAINER
from gui import nationCompareByIndex, GUI_SETTINGS
from gui.shared.economics import getActionPrc
from gui.shared.utils import ItemsParameters
from gui.shared.utils.functions import getShortDescr, stripShortDescrTags
CLAN_LOCK = 1
_ICONS_MASK = '../maps/icons/%(type)s/%(subtype)s%(unicName)s.png'
GUI_ITEM_TYPE_NAMES = tuple(ITEM_TYPE_NAMES) + tuple(['reserved'] * (16 - len(ITEM_TYPE_NAMES)))
GUI_ITEM_TYPE_NAMES += ('dossierAccount',
 'dossierVehicle',
 'dossierTankman',
 'achievement',
 'tankmanSkill')
GUI_ITEM_TYPE_INDICES = dict(((n, idx) for idx, n in enumerate(GUI_ITEM_TYPE_NAMES)))

class GUI_ITEM_TYPE(CONST_CONTAINER):
    VEHICLE = GUI_ITEM_TYPE_INDICES['vehicle']
    CHASSIS = GUI_ITEM_TYPE_INDICES['vehicleChassis']
    TURRET = GUI_ITEM_TYPE_INDICES['vehicleTurret']
    GUN = GUI_ITEM_TYPE_INDICES['vehicleGun']
    ENGINE = GUI_ITEM_TYPE_INDICES['vehicleEngine']
    FUEL_TANK = GUI_ITEM_TYPE_INDICES['vehicleFuelTank']
    RADIO = GUI_ITEM_TYPE_INDICES['vehicleRadio']
    TANKMAN = GUI_ITEM_TYPE_INDICES['tankman']
    OPTIONALDEVICE = GUI_ITEM_TYPE_INDICES['optionalDevice']
    SHELL = GUI_ITEM_TYPE_INDICES['shell']
    EQUIPMENT = GUI_ITEM_TYPE_INDICES['equipment']
    COMMON = tuple(ITEM_TYPE_INDICES.keys())
    ARTEFACTS = (EQUIPMENT, OPTIONALDEVICE)
    ACCOUNT_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierAccount']
    VEHICLE_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierVehicle']
    TANKMAN_DOSSIER = GUI_ITEM_TYPE_INDICES['dossierTankman']
    ACHIEVEMENT = GUI_ITEM_TYPE_INDICES['achievement']
    SKILL = GUI_ITEM_TYPE_INDICES['tankmanSkill']
    GUI = (ACCOUNT_DOSSIER,
     VEHICLE_DOSSIER,
     TANKMAN_DOSSIER,
     ACHIEVEMENT,
     SKILL)
    VEHICLE_MODULES = (GUN,
     TURRET,
     ENGINE,
     CHASSIS,
     RADIO)
    VEHICLE_COMPONENTS = VEHICLE_MODULES + ARTEFACTS + (SHELL,)


class ItemsCollection(dict):

    def filter(self, criteria):
        result = self.__class__()
        for intCD, item in self.iteritems():
            if criteria(item):
                result.update({intCD: item})

        return result

    def __repr__(self):
        return '%s<size:%d>' % (self.__class__.__name__, len(self.items()))


def getVehicleComponentsByType(vehicle, itemTypeIdx):
    """
    Returns collection of vehicle's installed items.
    
    @param vehicle: target vehicle
    @param itemTypeIdx: items.ITEM_TYPE_NAMES index
    
    @return: ItemsCollection instance
    """

    def packModules(modules):
        """ Helper function to pack item ot items list to the collection """
        if not isinstance(modules, list):
            modules = [modules]
        return ItemsCollection([ (module.intCD, module) for module in modules if module is not None ])

    if itemTypeIdx == vehicles._CHASSIS:
        return packModules(vehicle.chassis)
    if itemTypeIdx == vehicles._TURRET:
        return packModules(vehicle.turret)
    if itemTypeIdx == vehicles._GUN:
        return packModules(vehicle.gun)
    if itemTypeIdx == vehicles._ENGINE:
        return packModules(vehicle.engine)
    if itemTypeIdx == vehicles._FUEL_TANK:
        return packModules(vehicle.fuelTank)
    if itemTypeIdx == vehicles._RADIO:
        return packModules(vehicle.radio)
    if itemTypeIdx == vehicles._TANKMAN:
        from gui.shared.gui_items.Tankman import TankmenCollection
        return TankmenCollection([ (t.invID, t) for slotIdx, t in vehicle.crew ])
    if itemTypeIdx == vehicles._OPTIONALDEVICE:
        return packModules(vehicle.optDevices)
    if itemTypeIdx == vehicles._SHELL:
        return packModules(vehicle.shells)
    if itemTypeIdx == vehicles._EQUIPMENT:
        return packModules(vehicle.eqs)
    return ItemsCollection()


def getVehicleSuitablesByType(vehDescr, itemTypeId, turretPID = 0):
    """
    Returns all suitable items for given @vehicle.
    
    @param vehDescr: vehicle descriptor
    @param itemTypeId: requested items types
    @param turretPID: vehicle's turret id
    
    @return: (descriptors list, current vehicle's items compact descriptors list)
    """
    descriptorsList = list()
    current = list()
    if itemTypeId == vehicles._CHASSIS:
        current = [vehDescr.chassis['compactDescr']]
        descriptorsList = vehDescr.type.chassis
    elif itemTypeId == vehicles._ENGINE:
        current = [vehDescr.engine['compactDescr']]
        descriptorsList = vehDescr.type.engines
    elif itemTypeId == vehicles._RADIO:
        current = [vehDescr.radio['compactDescr']]
        descriptorsList = vehDescr.type.radios
    elif itemTypeId == vehicles._FUEL_TANK:
        current = [vehDescr.fuelTank['compactDescr']]
        descriptorsList = vehDescr.type.fuelTanks
    elif itemTypeId == vehicles._TURRET:
        current = [vehDescr.turret['compactDescr']]
        descriptorsList = vehDescr.type.turrets[turretPID]
    elif itemTypeId == vehicles._OPTIONALDEVICE:
        devs = vehicles.g_cache.optionalDevices()
        current = vehDescr.optionalDevices
        descriptorsList = [ dev for dev in devs.itervalues() if dev.checkCompatibilityWithVehicle(vehDescr)[0] ]
    elif itemTypeId == vehicles._EQUIPMENT:
        eqs = vehicles.g_cache.equipments()
        current = list()
        descriptorsList = [ eq for eq in eqs.itervalues() if eq.checkCompatibilityWithVehicle(vehDescr)[0] ]
    elif itemTypeId == vehicles._GUN:
        current = [vehDescr.gun['compactDescr']]
        for gun in vehDescr.turret['guns']:
            descriptorsList.append(gun)

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret['guns']:
                    descriptorsList.append(gun)

    elif itemTypeId == vehicles._SHELL:
        for shot in vehDescr.gun['shots']:
            current.append(shot['shell']['compactDescr'])

        for gun in vehDescr.turret['guns']:
            for shot in gun['shots']:
                descriptorsList.append(shot['shell'])

        for turret in vehDescr.type.turrets[turretPID]:
            if turret is not vehDescr.turret:
                for gun in turret['guns']:
                    for shot in gun['shots']:
                        descriptorsList.append(shot['shell'])

    return (descriptorsList, current)


class GUIItem(object):

    def __init__(self, proxy = None):
        pass

    def __repr__(self):
        return self.__class__.__name__


class HasIntCD(object):

    def __init__(self, intCompactDescr):
        self.intCompactDescr = intCompactDescr
        self.itemTypeID, self.nationID, self.innationID = self._parseIntCompDescr(self.intCompactDescr)

    def _parseIntCompDescr(self, intCompactDescr):
        return vehicles.parseIntCompactDescr(intCompactDescr)

    @property
    def intCD(self):
        return self.intCompactDescr

    @property
    def itemTypeName(self):
        return ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def nationName(self):
        return nations.NAMES[self.nationID]

    def __cmp__(self, other):
        if self is other:
            return 1
        res = nationCompareByIndex(self.nationID, other.nationID)
        if res:
            return res
        return 0


class HasStrCD(object):

    def __init__(self, strCompactDescr):
        self.strCompactDescr = strCompactDescr

    @property
    def strCD(self):
        return self.strCompactDescr


_RentalInfoProvider = namedtuple('RentalInfoProvider', ('rentExpiryTime',
 'compensations',
 'battlesLeft',
 'isRented'))
_RentalInfoProvider.__new__.__defaults__ = (0,
 (0, 0),
 0,
 False)

class RentalInfoProvider(_RentalInfoProvider):

    @property
    def timeLeft(self):
        return float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.rentExpiryTime)))


class FittingItem(GUIItem, HasIntCD):

    class TARGETS(object):
        CURRENT = 1
        IN_INVENTORY = 2
        OTHER = 3

    def __init__(self, intCompactDescr, proxy = None, isBoughtForCredits = False):
        GUIItem.__init__(self, proxy)
        HasIntCD.__init__(self, intCompactDescr)
        self.defaultPrice = (0, 0)
        self._buyPrice = (0, 0)
        self.sellPrice = (0, 0)
        self.defaultSellPrice = (0, 0)
        self.altPrice = None
        self.defaultAltPrice = None
        self.sellActionPrc = 0
        self.isHidden = False
        self.inventoryCount = 0
        self.sellForGold = False
        self.isUnlocked = False
        self.isBoughtForCredits = isBoughtForCredits
        self.rentInfo = RentalInfoProvider()
        if proxy is not None and proxy.isSynced():
            self.defaultPrice = proxy.shop.defaults.getItemPrice(self.intCompactDescr)
            if self.defaultPrice is None:
                self.defaultPrice = (0, 0)
            self._buyPrice, self.isHidden, self.sellForGold = proxy.shop.getItem(self.intCompactDescr)
            if self._buyPrice is None:
                self._buyPrice = (0, 0)
            self.defaultSellPrice = BigWorld.player().shop.getSellPrice(self.defaultPrice, proxy.shop.defaults.sellPriceModifiers(intCompactDescr), self.itemTypeID)
            self.sellPrice = BigWorld.player().shop.getSellPrice(self.buyPrice, proxy.shop.sellPriceModifiers(intCompactDescr), self.itemTypeID)
            self.inventoryCount = proxy.inventory.getItems(self.itemTypeID, self.intCompactDescr)
            if self.inventoryCount is None:
                self.inventoryCount = 0
            self.isUnlocked = self.intCD in proxy.stats.unlocks
            self.altPrice = self._getAltPrice(self.buyPrice, proxy.shop)
            self.defaultAltPrice = self._getAltPrice(self.defaultPrice, proxy.shop.defaults)
            self.sellActionPrc = -1 * getActionPrc(self.sellPrice, self.defaultSellPrice)
        return

    def _getAltPrice(self, buyPrice, proxy):
        return None

    @property
    def buyPrice(self):
        return self._buyPrice

    @property
    def actionPrc(self):
        return getActionPrc(self.altPrice or self.buyPrice, self.defaultAltPrice or self.defaultPrice)

    @property
    def isSecret(self):
        return False

    @property
    def isPremium(self):
        return self.buyPrice[1] > 0

    @property
    def isPremiumIGR(self):
        return False

    @property
    def isRentable(self):
        return False

    @property
    def isRented(self):
        return False

    @property
    def descriptor(self):
        return vehicles.getDictDescr(self.intCompactDescr)

    @property
    def isRemovable(self):
        return True

    @property
    def minRentPrice(self):
        return None

    @property
    def rentLeftTime(self):
        return 0

    @property
    def userType(self):
        return getTypeInfoByName(self.itemTypeName)['userString']

    @property
    def userName(self):
        return self.descriptor.get('userString', '')

    @property
    def longUserName(self):
        return self.userType + ' ' + self.userName

    @property
    def shortUserName(self):
        return self.descriptor.get('shortUserString', '')

    @property
    def shortDescription(self):
        return getShortDescr(self.descriptor.get('description', ''))

    @property
    def fullDescription(self):
        return stripShortDescrTags(self.descriptor.get('description', ''))

    @property
    def name(self):
        return self.descriptor.get('name', '')

    @property
    def level(self):
        return self.descriptor.get('level', 0)

    @property
    def isInInventory(self):
        return self.inventoryCount > 0

    def _getShortInfo(self, vehicle = None, expanded = False):
        try:
            description = i18n.makeString('#menu:descriptions/' + self.itemTypeName + ('Full' if expanded else ''))
            itemParams = dict(ItemsParameters.g_instance.getParameters(self.descriptor, vehicle.descriptor if vehicle is not None else None))
            if self.itemTypeName == vehicles._VEHICLE:
                itemParams['caliber'] = BigWorld.wg_getIntegralFormat(self.descriptor.gun['shots'][0]['shell']['caliber'])
            return description % itemParams
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return ''

        return

    def getShortInfo(self, vehicle = None, expanded = False):
        if not GUI_SETTINGS.technicalInfo:
            return ''
        return self._getShortInfo(vehicle, expanded)

    def getParams(self, vehicle = None):
        return dict(ItemsParameters.g_instance.get(self.descriptor, vehicle.descriptor if vehicle is not None else None))

    def getRentPackage(self, days = None):
        return None

    def getGUIEmblemID(self):
        return 'notFound'

    @property
    def icon(self):
        return _ICONS_MASK % {'type': self.itemTypeName,
         'subtype': '',
         'unicName': self.name.replace(':', '-')}

    @property
    def iconSmall(self):
        return _ICONS_MASK % {'type': self.itemTypeName,
         'subtype': 'small/',
         'unicName': self.name.replace(':', '-')}

    def getBuyPriceCurrency(self):
        if self.altPrice is not None:
            if self.altPrice[1] and not self.isBoughtForCredits:
                return 'gold'
        elif self.buyPrice[1]:
            return 'gold'
        return 'credits'

    def getSellPriceCurrency(self):
        if self.sellPrice[1]:
            return 'gold'
        return 'credits'

    def isInstalled(self, vehicle, slotIdx = None):
        return False

    def mayInstall(self, vehicle, slotIdx = None):
        return vehicle.descriptor.mayInstallComponent(self.intCD)

    def mayRemove(self, vehicle):
        return (True, '')

    def mayRent(self, money):
        return (False, '')

    def mayRentOrBuy(self, money):
        return self.mayPurchase(money)

    def mayPurchaseWithExchange(self, money, exchangeRate):
        priceCredits, _ = self.altPrice or self.buyPrice
        moneyCredits, moneyGold = money
        if priceCredits <= moneyGold * exchangeRate + moneyCredits:
            return True
        return False

    def mayPurchase(self, money):
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, 'center_unavailable')
        if self.itemTypeID not in (GUI_ITEM_TYPE.EQUIPMENT, GUI_ITEM_TYPE.OPTIONALDEVICE, GUI_ITEM_TYPE.SHELL) and not self.isUnlocked:
            return (False, 'unlock_error')
        if self.isHidden:
            return (False, 'isHidden')
        price = self.altPrice or self.buyPrice
        if price[0] == 0 and price[1] == 0:
            return (True, '')
        currency = ''
        if price[1]:
            currency = 'gold'
            if price[1] <= money[1]:
                return (True, '')
        if price[0]:
            currency = 'credit'
            if price[0] <= money[0]:
                return (True, '')
        return (False, '%s_error' % currency)

    def getTarget(self, vehicle):
        if self.isInstalled(vehicle):
            return self.TARGETS.CURRENT
        if self.isInInventory:
            return self.TARGETS.IN_INVENTORY
        return self.TARGETS.OTHER

    def getConflictedEquipments(self, vehicle):
        return ()

    def getInstalledVehicles(self, vehs):
        return set()

    def _sortByType(self, other):
        return 0

    def __cmp__(self, other):
        if other is None:
            return 1
        res = HasIntCD.__cmp__(self, other)
        if res:
            return res
        res = self._sortByType(other)
        if res:
            return res
        res = self.level - other.level
        if res:
            return res
        res = self.buyPrice[1] - other.buyPrice[1]
        if res:
            return res
        res = self.buyPrice[0] - other.buyPrice[0]
        if res:
            return res
        else:
            return cmp(self.userName, other.userName)

    def __eq__(self, other):
        if other is None:
            return False
        else:
            return self.intCompactDescr == other.intCompactDescr

    def __repr__(self):
        return '%s<intCD:%d, type:%s, nation:%d>' % (self.__class__.__name__,
         self.intCD,
         self.itemTypeName,
         self.nationID)


def getItemIconName(itemName):
    return '%s.png' % itemName.replace(':', '-')
