# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/stock.py
from collections import defaultdict
from itertools import chain
from WeakMethod import WeakMethodProxy
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from helpers import dependency, i18n
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from shared_utils import CONST_CONTAINER
from soft_exception import SoftException
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from web_client_api import w2c, W2CSchema, Field
from web_client_api.shop import formatters

class ItemType(CONST_CONTAINER):
    VEHICLE = 'vehicle'
    EQUIPMENT = 'equipment'
    DEVICE = 'device'
    BOOSTER = 'booster'
    BATTLE_BOOSTER = 'battleBooster'
    MODULE = 'module'
    SHELL = 'shell'
    PREMIUM_PACK = 'premiumPack'


class PremiumPack(object):

    def __init__(self, duration, cost, defCost):
        self.__duration = duration
        self.__price = ItemPrice(Money(gold=cost), Money(gold=defCost))

    @property
    def buyPrice(self):
        return self.__price

    @property
    def duration(self):
        return self.__duration

    @property
    def userName(self):
        return i18n.makeString('#menu:premium/packet/days%s' % self.__duration)


_GUI_ITEMS_TYPE_MAP = {ItemType.VEHICLE: GUI_ITEM_TYPE.VEHICLE,
 ItemType.EQUIPMENT: GUI_ITEM_TYPE.EQUIPMENT,
 ItemType.DEVICE: GUI_ITEM_TYPE.OPTIONALDEVICE,
 ItemType.BATTLE_BOOSTER: GUI_ITEM_TYPE.BATTLE_BOOSTER,
 ItemType.MODULE: GUI_ITEM_TYPE.VEHICLE_MODULES,
 ItemType.SHELL: GUI_ITEM_TYPE.SHELL}
_ITEMS_CRITERIA_MAP = {ItemType.VEHICLE: {'inventory': REQ_CRITERIA.INVENTORY,
                    'premium': REQ_CRITERIA.VEHICLE.PREMIUM,
                    'ready': REQ_CRITERIA.VEHICLE.READY,
                    'sellable': REQ_CRITERIA.VEHICLE.CAN_SELL},
 ItemType.EQUIPMENT: {'inventory': REQ_CRITERIA.INVENTORY},
 ItemType.DEVICE: {'inventory': REQ_CRITERIA.INVENTORY},
 ItemType.BATTLE_BOOSTER: {'inventory': REQ_CRITERIA.INVENTORY},
 ItemType.MODULE: {'inventory': REQ_CRITERIA.INVENTORY},
 ItemType.BOOSTER: {'inventory': REQ_CRITERIA.BOOSTER.IN_ACCOUNT},
 ItemType.SHELL: {'inventory': REQ_CRITERIA.INVENTORY},
 ItemType.PREMIUM_PACK: {}}
_EXTRA_ITEMS_CRITERIA_MAP = {ItemType.VEHICLE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR,
 ItemType.EQUIPMENT: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ItemType.DEVICE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ItemType.BATTLE_BOOSTER: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ItemType.MODULE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ItemType.SHELL: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ItemType.BOOSTER: REQ_CRITERIA.BOOSTER.ENABLED | ~REQ_CRITERIA.HIDDEN}

def _parseCriteriaSpec(itemType, spec):
    typeCriteria = _ITEMS_CRITERIA_MAP[itemType]
    ids = sorted([ val.strip() for val in spec.split(',') ] if spec else [])
    normalizedIds = [ i.replace('!', '') for i in ids ]
    compoundCriteria = REQ_CRITERIA.EMPTY
    for critId, normalizedCritId in zip(ids, normalizedIds):
        try:
            criteria = typeCriteria[normalizedCritId]
            if critId.startswith('!'):
                criteria = ~criteria
            compoundCriteria |= criteria
        except KeyError:
            raise SoftException('item type "{}" does not support criteria "{}"'.format(itemType, critId))

    return compoundCriteria


class _GetItemsSchema(W2CSchema):
    type = Field(required=True, type=basestring, validator=lambda value, data: ItemType.hasValue(value))
    criteria = Field(required=False, type=basestring, validator=lambda value, data: _parseCriteriaSpec(data['type'], value))


class ItemsWebApiMixin(object):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)

    def __init__(self):
        super(ItemsWebApiMixin, self).__init__()
        self.__formattersMap = {}
        self.__compatVehiclesCache = {}
        self.__fittedVehiclesCache = {}
        self.__cachesInitialized = False
        self.__inventoryUpdateHandler = WeakMethodProxy(self.updateMappingCaches)
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateHandler})

    def __del__(self):
        g_clientUpdateManager.removeCallback('inventory', self.__inventoryUpdateHandler)

    @w2c(_GetItemsSchema, 'get_items')
    def getItems(self, cmd):
        if not self.__cachesInitialized:
            self.updateMappingCaches()
        criteria = _parseCriteriaSpec(cmd.type, cmd.criteria)
        if not criteria.lookInInventory():
            criteria |= _EXTRA_ITEMS_CRITERIA_MAP.get(cmd.type, REQ_CRITERIA.EMPTY)
        return [ self.__getFormatter(cmd.type, criteria).format(item) for item in self.__collectItems(cmd.type, criteria) ]

    def __getFormatter(self, itemType, criteria):
        key = self.__makeFormatterKey(itemType, criteria)
        fmt = self.__formattersMap.get(key)
        if fmt is not None:
            return fmt
        else:
            if itemType == ItemType.VEHICLE:
                fmt = formatters.makeVehicleFormatter(criteria.lookInInventory())
            elif itemType == ItemType.EQUIPMENT:
                fmt = formatters.makeEquipmentFormatter(lambda itemID: self.__fittedVehiclesCache[ItemType.EQUIPMENT][itemID])
            elif itemType == ItemType.DEVICE:
                fmt = formatters.makeDeviceFormatter(lambda itemID: self.__compatVehiclesCache[ItemType.DEVICE][itemID], lambda itemID: self.__fittedVehiclesCache[ItemType.DEVICE][itemID])
            elif itemType == ItemType.BOOSTER:
                fmt = formatters.makeBoosterFormatter()
            elif itemType == ItemType.BATTLE_BOOSTER:
                fmt = formatters.makeBattleBoosterFormatter(lambda itemID: self.__fittedVehiclesCache[ItemType.BATTLE_BOOSTER][itemID])
            elif itemType == ItemType.MODULE:
                fmt = formatters.makeModuleFormatter()
            elif itemType == ItemType.PREMIUM_PACK:
                fmt = formatters.makePremiumPackFormatter()
            elif itemType == ItemType.SHELL:
                fmt = formatters.makeShellFormatter()
            self.__formattersMap[key] = fmt
            return fmt

    def __makeFormatterKey(self, itemType, criteria):
        entries = [itemType]
        if itemType == ItemType.VEHICLE and criteria.lookInInventory():
            entries.append('inventory')
        return ','.join(entries)

    def __collectItems(self, itemType, criteria):
        if itemType == ItemType.BOOSTER:
            return self.__collectBoosters(criteria)
        return self.__collectPremiumPacks() if itemType == ItemType.PREMIUM_PACK else self.__collectGuiItems(itemType, criteria)

    def __collectBoosters(self, criteria):
        return self.goodiesCache.getBoosters(criteria=criteria).itervalues()

    def __collectGuiItems(self, itemType, criteria):
        return self.itemsCache.items.getItems(_GUI_ITEMS_TYPE_MAP[itemType], criteria).itervalues()

    def __collectPremiumPacks(self):
        shop = self.itemsCache.items.shop
        defaultPrem = shop.defaults.premiumCost
        discountedPrem = shop.getPremiumCostWithDiscount()
        return [ PremiumPack(duration, discountedPrem.get(duration, cost), cost) for duration, cost in defaultPrem.iteritems() ]

    def updateMappingCaches(self, *args):

        def collectAll(itemType):
            return ((itemType, item) for item in self.__collectItems(itemType, _EXTRA_ITEMS_CRITERIA_MAP[itemType]))

        types = [ItemType.DEVICE, ItemType.EQUIPMENT, ItemType.BATTLE_BOOSTER]
        self.__compatVehiclesCache.clear()
        self.__compatVehiclesCache.update({itemType:defaultdict(list) for itemType in types})
        self.__fittedVehiclesCache.clear()
        self.__fittedVehiclesCache.update({itemType:defaultdict(list) for itemType in types})
        vehicles = self.itemsCache.items.getItems(GUI_ITEM_TYPE.VEHICLE, REQ_CRITERIA.INVENTORY).itervalues()
        typedItemPairs = list(chain.from_iterable((collectAll(itemType) for itemType in types)))
        for veh in vehicles:
            for itemType, item in typedItemPairs:
                if item.mayInstall(veh, 0)[0]:
                    self.__compatVehiclesCache[itemType][item.intCD].append(veh.intCD)
                if item.isInstalled(veh):
                    self.__fittedVehiclesCache[itemType][item.intCD].append(veh.intCD)

        self.__cachesInitialized = True
