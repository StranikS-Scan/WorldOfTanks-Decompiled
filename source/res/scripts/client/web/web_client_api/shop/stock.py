# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/shop/stock.py
import itertools
import typing
from collections import namedtuple
from functools import partial
from WeakMethod import WeakMethodProxy
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.recruit_helper import getAllRecruitsInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from gui.shared.utils.requesters.ItemsRequester import PredicateCondition, REQ_CRITERIA, RequestCriteria
from helpers import dependency
from items import getTypeOfCompactDescr
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
from web.web_client_api import Field, W2CSchema, w2c
from web.web_client_api.common import ShopItemType
from web.web_client_api.shop import formatters
from web.web_client_api.shop.crew import ShopCrewCriteria, makeTankman
if typing.TYPE_CHECKING:
    from typing import Optional, Set
    from gui.shared.gui_items.gui_item import GUIItem

class _PremiumPack(object):

    def __init__(self, duration, cost, defCost):
        self.__duration = duration
        self.__price = ItemPrice(Money(gold=cost), Money(gold=defCost))

    @property
    def id(self):
        pass

    @property
    def buyPrice(self):
        return self.__price

    @property
    def duration(self):
        return self.__duration

    @property
    def userName(self):
        return backport.text(R.strings.menu.premium.packet.dyn('days{}'.format(self.__duration))())

    @property
    def shortDescriptionSpecial(self):
        return backport.text(R.strings.menu.premium.packet.shortDescriptionSpecial())

    @property
    def longDescriptionSpecial(self):
        return backport.text(R.strings.menu.premium.packet.longDescriptionSpecial())


_InventoryEnhancements = namedtuple('_InventoryEnhancements', ('id', 'count'))
_InstalledEnhancements = namedtuple('_InstalledEnhancements', ('vehIntCD', 'enhancements'))
_GUI_ITEMS_TYPE_MAP = {ShopItemType.VEHICLE: GUI_ITEM_TYPE.VEHICLE,
 ShopItemType.EQUIPMENT: GUI_ITEM_TYPE.EQUIPMENT,
 ShopItemType.DEVICE: GUI_ITEM_TYPE.OPTIONALDEVICE,
 ShopItemType.BATTLE_BOOSTER: GUI_ITEM_TYPE.BATTLE_BOOSTER,
 ShopItemType.MODULE: GUI_ITEM_TYPE.VEHICLE_MODULES,
 ShopItemType.SHELL: GUI_ITEM_TYPE.SHELL,
 ShopItemType.CREW_BOOKS: GUI_ITEM_TYPE.CREW_BOOKS,
 ShopItemType.PAINT: GUI_ITEM_TYPE.PAINT,
 ShopItemType.CAMOUFLAGE: GUI_ITEM_TYPE.CAMOUFLAGE,
 ShopItemType.MODIFICATION: GUI_ITEM_TYPE.MODIFICATION,
 ShopItemType.STYLE: GUI_ITEM_TYPE.STYLE,
 ShopItemType.DECAL: GUI_ITEM_TYPE.DECAL,
 ShopItemType.EMBLEM: GUI_ITEM_TYPE.EMBLEM,
 ShopItemType.INSCRIPTION: GUI_ITEM_TYPE.INSCRIPTION,
 ShopItemType.PROJECTION_DECAL: GUI_ITEM_TYPE.PROJECTION_DECAL}
_ITEMS_CRITERIA_MAP = {ShopItemType.VEHICLE: {'inventory': REQ_CRITERIA.INVENTORY,
                        'premium': REQ_CRITERIA.VEHICLE.PREMIUM,
                        'ready': REQ_CRITERIA.VEHICLE.READY,
                        'sellable': REQ_CRITERIA.VEHICLE.CAN_SELL,
                        'secret': REQ_CRITERIA.SECRET,
                        'hidden': REQ_CRITERIA.HIDDEN,
                        'is_premium_igr': REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR,
                        'trade_in': REQ_CRITERIA.VEHICLE.CAN_TRADE_IN,
                        'trade_off': REQ_CRITERIA.VEHICLE.CAN_TRADE_OFF,
                        'skip_multinational_copies': REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP,
                        'collectible': REQ_CRITERIA.COLLECTIBLE,
                        'earn_crystals': REQ_CRITERIA.VEHICLE.EARN_CRYSTALS,
                        'event_battle': REQ_CRITERIA.VEHICLE.EVENT_BATTLE},
 ShopItemType.CREW: {'premium': ShopCrewCriteria.PREMIUM},
 ShopItemType.EQUIPMENT: {'inventory': REQ_CRITERIA.INVENTORY,
                          'secret': REQ_CRITERIA.SECRET,
                          'hidden': REQ_CRITERIA.HIDDEN,
                          'builtin': REQ_CRITERIA.EQUIPMENT.BUILTIN},
 ShopItemType.DEVICE: {'inventory': REQ_CRITERIA.INVENTORY,
                       'secret': REQ_CRITERIA.SECRET,
                       'hidden': REQ_CRITERIA.HIDDEN},
 ShopItemType.BATTLE_BOOSTER: {'inventory': REQ_CRITERIA.INVENTORY,
                               'secret': REQ_CRITERIA.SECRET,
                               'hidden': REQ_CRITERIA.HIDDEN},
 ShopItemType.MODULE: {'inventory': REQ_CRITERIA.INVENTORY,
                       'secret': REQ_CRITERIA.SECRET,
                       'hidden': REQ_CRITERIA.HIDDEN},
 ShopItemType.BOOSTER: {'inventory': REQ_CRITERIA.BOOSTER.IN_ACCOUNT,
                        'hidden': REQ_CRITERIA.HIDDEN,
                        'enabled': REQ_CRITERIA.BOOSTER.ENABLED},
 ShopItemType.SHELL: {'inventory': REQ_CRITERIA.INVENTORY,
                      'secret': REQ_CRITERIA.SECRET,
                      'hidden': REQ_CRITERIA.HIDDEN},
 ShopItemType.PREMIUM: {},
 ShopItemType.PAINT: {},
 ShopItemType.CAMOUFLAGE: {},
 ShopItemType.MODIFICATION: {},
 ShopItemType.STYLE: {'on_account': REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT,
                      'inventory': REQ_CRITERIA.CUSTOMIZATION.ON_ACCOUNT},
 ShopItemType.DECAL: {},
 ShopItemType.EMBLEM: {},
 ShopItemType.INSCRIPTION: {},
 ShopItemType.PROJECTION_DECAL: {},
 ShopItemType.CREW_BOOKS: {},
 ShopItemType.ENHANCEMENT: {'inventory': REQ_CRITERIA.INVENTORY}}

class IdInListCriteria(RequestCriteria):

    def __call__(self, idList, itemType=None):
        getValue = (lambda item: item.groupName) if itemType == ShopItemType.CREW else (lambda item: item.intCD)

        def isValidItem(item):
            return not idList or getValue(item) in idList

        self._conditions = (PredicateCondition(isValidItem),)
        return self


ID_IN_LIST = IdInListCriteria()
_SHOP_CUSTOMIZATION_TYPES = (ShopItemType.PAINT,
 ShopItemType.CAMOUFLAGE,
 ShopItemType.MODIFICATION,
 ShopItemType.STYLE,
 ShopItemType.DECAL,
 ShopItemType.EMBLEM,
 ShopItemType.INSCRIPTION,
 ShopItemType.PROJECTION_DECAL)
_SHOP_ITEM_TYPE_MAP = {GUI_ITEM_TYPE.VEHICLE: ShopItemType.VEHICLE,
 GUI_ITEM_TYPE.EQUIPMENT: ShopItemType.EQUIPMENT,
 GUI_ITEM_TYPE.OPTIONALDEVICE: ShopItemType.DEVICE,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: ShopItemType.BATTLE_BOOSTER,
 GUI_ITEM_TYPE.SHELL: ShopItemType.SHELL,
 GUI_ITEM_TYPE.GUN: ShopItemType.MODULE,
 GUI_ITEM_TYPE.TURRET: ShopItemType.MODULE,
 GUI_ITEM_TYPE.ENGINE: ShopItemType.MODULE,
 GUI_ITEM_TYPE.CHASSIS: ShopItemType.MODULE,
 GUI_ITEM_TYPE.RADIO: ShopItemType.MODULE,
 GUI_ITEM_TYPE.CREW_BOOKS: ShopItemType.CREW_BOOKS}

def _parseCriteriaSpec(itemType, spec, idList=None):
    typeCriteria = _ITEMS_CRITERIA_MAP[itemType]
    ids = sorted([ val.strip() for val in spec ] if spec else [])
    normalizedIds = [ i.replace('!', '') for i in ids ]
    compoundCriteria = REQ_CRITERIA.EMPTY | ID_IN_LIST(idList, itemType) if idList else REQ_CRITERIA.EMPTY
    for critId, normalizedCritId in zip(ids, normalizedIds):
        try:
            criteria = typeCriteria[normalizedCritId]
            if critId.startswith('!'):
                criteria = ~criteria
            compoundCriteria |= criteria
        except KeyError:
            raise SoftException('item type "{}" does not support criteria "{}"'.format(itemType, critId))

    return compoundCriteria


class _GetItemsByCdSchema(W2CSchema):
    cds = Field(required=True, type=list)
    fields = Field(required=False, type=list)


class _GetItemByCdSchema(W2CSchema):
    cd = Field(required=True, type=int)
    fields = Field(required=False, type=list)


class _GetItemsSchema(W2CSchema):
    type = Field(required=True, type=basestring, validator=lambda value, data: ShopItemType.hasValue(value))
    criteria = Field(required=False, type=list, validator=lambda value, data: _parseCriteriaSpec(data['type'], value))
    fields = Field(required=False, type=list)
    id_list = Field(required=False, type=list)


class ItemsWebApiMixin(object):
    __itemsCache = dependency.descriptor(IItemsCache)
    __goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(ItemsWebApiMixin, self).__init__()
        self.__formattersMap = {}

    @w2c(_GetItemsByCdSchema, 'get_items_by_cd')
    def getItemsByCD(self, cmd):
        allowedFields = cmd.fields and set(cmd.fields)
        return {cd:self.__getItemByCD(cd, allowedFields) for cd in cmd.cds}

    @w2c(_GetItemByCdSchema, 'get_item_by_cd')
    def getItemByCD(self, cmd):
        allowedFields = cmd.fields and set(cmd.fields)
        return self.__getItemByCD(cmd.cd, allowedFields)

    @w2c(_GetItemsSchema, 'get_items')
    def getItems(self, cmd):
        criteria = _parseCriteriaSpec(cmd.type, cmd.criteria, cmd.id_list)
        allowedFields = set(cmd.fields) if cmd.fields else None
        return [ self.__getFormatter(cmd.type, criteria).format(item, allowedFields) for item in self.__collectItems(cmd.type, criteria) ]

    def __getFormatter(self, itemType, criteria):
        key = self.__makeFormatterKey(itemType, criteria)
        fmt = self.__formattersMap.get(key)
        if fmt is not None:
            return fmt
        else:
            if itemType == ShopItemType.VEHICLE:
                fmt = formatters.makeVehicleFormatter(criteria.lookInInventory())
            elif itemType == ShopItemType.CREW:
                fmt = formatters.makeShopTankmanFormatter()
            elif itemType == ShopItemType.EQUIPMENT:
                fmt = formatters.makeEquipmentFormatter(partial(WeakMethodProxy(self.__getFittedVehicles), ShopItemType.EQUIPMENT))
            elif itemType == ShopItemType.DEVICE:
                fmt = formatters.makeDeviceFormatter(partial(WeakMethodProxy(self.__getCompatVehicles), ShopItemType.DEVICE), partial(WeakMethodProxy(self.__getFittedVehicles), ShopItemType.DEVICE))
            elif itemType == ShopItemType.BOOSTER:
                fmt = formatters.makeBoosterFormatter()
            elif itemType == ShopItemType.BATTLE_BOOSTER:
                fmt = formatters.makeBattleBoosterFormatter(partial(WeakMethodProxy(self.__getFittedVehicles), ShopItemType.BATTLE_BOOSTER))
            elif itemType == ShopItemType.MODULE:
                fmt = formatters.makeModuleFormatter()
            elif itemType == ShopItemType.PREMIUM:
                fmt = formatters.makePremiumPackFormatter()
            elif itemType == ShopItemType.SHELL:
                fmt = formatters.makeShellFormatter()
            elif itemType in _SHOP_CUSTOMIZATION_TYPES:
                fmt = formatters.makeCustomizationFormatter()
            elif itemType == ShopItemType.ENHANCEMENT:
                if criteria.lookInInventory():
                    fmt = formatters.makeInventoryEnhancementsFormatter()
                else:
                    fmt = formatters.makeInstalledEnhancementsFormatter()
            elif itemType in ShopItemType.CREW_BOOKS:
                fmt = formatters.makeCrewBooksFormatter()
            self.__formattersMap[key] = fmt
            return fmt

    def __makeFormatterKey(self, itemType, criteria):
        entries = [itemType]
        if itemType == ShopItemType.VEHICLE and criteria.lookInInventory():
            entries.append('inventory')
        elif itemType == ShopItemType.ENHANCEMENT:
            if criteria.lookInInventory():
                entries.append('inventory')
            else:
                entries.append('installed')
        return ','.join(entries)

    def __getItemByCD(self, cd, allowedFields=None):
        try:
            itemType = getTypeOfCompactDescr(cd)
            item = self.__itemsCache.items.getItemByCD(cd)
            if itemType not in _SHOP_ITEM_TYPE_MAP:
                return None
            return self.__getFormatter(_SHOP_ITEM_TYPE_MAP[itemType], REQ_CRITERIA.EMPTY).format(item, allowedFields)
        except (IndexError, KeyError, SoftException):
            return None

        return None

    def __collectItems(self, itemType, criteria):
        if itemType == ShopItemType.CREW:
            return self.__collectCrew(criteria)
        if itemType == ShopItemType.BOOSTER:
            return self.__collectBoosters(criteria)
        if itemType == ShopItemType.PREMIUM:
            return self.__collectPremiumPacks()
        if itemType == ShopItemType.ENHANCEMENT:
            if criteria.lookInInventory():
                return self.__collectInventoryEnhancements()
            return self.__collectInstalledEnhancements()
        return self.__collectGuiItems(itemType, criteria)

    def __collectBoosters(self, criteria):
        return self.__goodiesCache.getBoosters(criteria=criteria).itervalues()

    def __collectGuiItems(self, itemType, criteria):
        return self.__itemsCache.items.getItems(_GUI_ITEMS_TYPE_MAP[itemType], criteria).itervalues()

    def __collectPremiumPacks(self):
        shop = self.__itemsCache.items.shop
        defaultPrem = shop.defaults.premiumCost
        discountedPrem = shop.getPremiumCostWithDiscount()
        return (_PremiumPack(duration, discountedPrem.get(duration, cost), cost) for duration, cost in defaultPrem.iteritems())

    def __collectInventoryEnhancements(self):
        inventory = self.__itemsCache.items.inventory
        fromInventory = inventory.getInventoryEnhancements()
        inventoryEnhancements = {}
        for enhancements in fromInventory.itervalues():
            for enhancementID, count in enhancements.iteritems():
                inventoryEnhancements[enhancementID] = count

        return (_InventoryEnhancements(enhancementID, count) for enhancementID, count in inventoryEnhancements.iteritems())

    def __collectInstalledEnhancements(self):
        inventory = self.__itemsCache.items.inventory
        fromVehicles = inventory.getInstalledEnhancements()
        installedEnhancements = {}
        for vehs in fromVehicles.itervalues():
            for vehInvID, enhancements in vehs.iteritems():
                vehInfo = self.__itemsCache.items.getVehicle(vehInvID)
                if vehInfo:
                    installedEnhancements[vehInfo.intCD] = enhancements

        return (_InstalledEnhancements(vehIntCD, enhancements) for vehIntCD, enhancements in installedEnhancements.iteritems())

    def __collectCrew(self, criteria):
        return (tankman for tankman in (makeTankman(crewItem) for crewItem in itertools.chain(self.__itemsCache.items.getTankmen().itervalues(), self.__itemsCache.items.getDismissedTankmen().itervalues(), getAllRecruitsInfo())) if criteria(tankman))

    def __getCompatVehicles(self, itemType, itemID):
        cache = self.__itemsCache.compatVehiclesCache.getCompatCache(self.__itemsCache)
        return cache[_GUI_ITEMS_TYPE_MAP[itemType]][itemID]

    def __getFittedVehicles(self, itemType, itemID):
        cache = self.__itemsCache.compatVehiclesCache.getFittedCache(self.__itemsCache)
        return cache[_GUI_ITEMS_TYPE_MAP[itemType]][itemID]
