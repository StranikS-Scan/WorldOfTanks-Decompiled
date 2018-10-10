# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/shop/stock.py
from collections import defaultdict
from functools import partial
from itertools import chain
from WeakMethod import WeakMethodProxy
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform import MENU
from gui.shared.gui_items.gui_item_economics import ItemPrice
from gui.shared.money import Money
from helpers import dependency, i18n
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from soft_exception import SoftException
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.shared import IItemsCache
from web_client_api import w2c, W2CSchema, Field
from web_client_api.shop import formatters
from web_client_api.common import ShopItemType

class PremiumPack(object):

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
        return i18n.makeString('#menu:premium/packet/days%s' % self.__duration)

    @property
    def shortDescriptionSpecial(self):
        return i18n.makeString(MENU.PREMIUM_PACKET_SHORTDESCRIPTIONSPECIAL)

    @property
    def longDescriptionSpecial(self):
        return i18n.makeString(MENU.PREMIUM_PACKET_LONGDESCRIPTIONSPECIAL)


_GUI_ITEMS_TYPE_MAP = {ShopItemType.VEHICLE: GUI_ITEM_TYPE.VEHICLE,
 ShopItemType.EQUIPMENT: GUI_ITEM_TYPE.EQUIPMENT,
 ShopItemType.DEVICE: GUI_ITEM_TYPE.OPTIONALDEVICE,
 ShopItemType.BATTLE_BOOSTER: GUI_ITEM_TYPE.BATTLE_BOOSTER,
 ShopItemType.MODULE: GUI_ITEM_TYPE.VEHICLE_MODULES,
 ShopItemType.SHELL: GUI_ITEM_TYPE.SHELL}
_ITEMS_CRITERIA_MAP = {ShopItemType.VEHICLE: {'inventory': REQ_CRITERIA.INVENTORY,
                        'premium': REQ_CRITERIA.VEHICLE.PREMIUM,
                        'ready': REQ_CRITERIA.VEHICLE.READY,
                        'sellable': REQ_CRITERIA.VEHICLE.CAN_SELL},
 ShopItemType.EQUIPMENT: {'inventory': REQ_CRITERIA.INVENTORY},
 ShopItemType.DEVICE: {'inventory': REQ_CRITERIA.INVENTORY},
 ShopItemType.BATTLE_BOOSTER: {'inventory': REQ_CRITERIA.INVENTORY},
 ShopItemType.MODULE: {'inventory': REQ_CRITERIA.INVENTORY},
 ShopItemType.BOOSTER: {'inventory': REQ_CRITERIA.BOOSTER.IN_ACCOUNT},
 ShopItemType.SHELL: {'inventory': REQ_CRITERIA.INVENTORY},
 ShopItemType.PREMIUM: {}}
_EXTRA_ITEMS_CRITERIA_MAP = {ShopItemType.VEHICLE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.VEHICLE.IS_PREMIUM_IGR,
 ShopItemType.EQUIPMENT: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ShopItemType.DEVICE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ShopItemType.BATTLE_BOOSTER: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ShopItemType.MODULE: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ShopItemType.SHELL: ~REQ_CRITERIA.HIDDEN | ~REQ_CRITERIA.SECRET,
 ShopItemType.BOOSTER: REQ_CRITERIA.BOOSTER.ENABLED | ~REQ_CRITERIA.HIDDEN}

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
    type = Field(required=True, type=basestring, validator=lambda value, data: ShopItemType.hasValue(value))
    criteria = Field(required=False, type=basestring, validator=lambda value, data: _parseCriteriaSpec(data['type'], value))
    fields = Field(required=False, type=list, validator=None)


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
        allowedFields = set(cmd.fields) if cmd.fields else None
        if not criteria.lookInInventory():
            criteria |= _EXTRA_ITEMS_CRITERIA_MAP.get(cmd.type, REQ_CRITERIA.EMPTY)
        result = [ self.__getFormatter(cmd.type, criteria).format(item, allowedFields) for item in self.__collectItems(cmd.type, criteria) ]
        return result

    def __getFormatter(self, itemType, criteria):
        key = self.__makeFormatterKey(itemType, criteria)
        fmt = self.__formattersMap.get(key)
        if fmt is not None:
            return fmt
        else:
            if itemType == ShopItemType.VEHICLE:
                fmt = formatters.makeVehicleFormatter(criteria.lookInInventory())
            elif itemType == ShopItemType.EQUIPMENT:
                fmt = formatters.makeEquipmentFormatter(partial(WeakMethodProxy(self.getFittedVehicles), ShopItemType.EQUIPMENT))
            elif itemType == ShopItemType.DEVICE:
                fmt = formatters.makeDeviceFormatter(partial(WeakMethodProxy(self.getCompatVehicles), ShopItemType.DEVICE), partial(WeakMethodProxy(self.getFittedVehicles), ShopItemType.DEVICE))
            elif itemType == ShopItemType.BOOSTER:
                fmt = formatters.makeBoosterFormatter()
            elif itemType == ShopItemType.BATTLE_BOOSTER:
                fmt = formatters.makeBattleBoosterFormatter(partial(WeakMethodProxy(self.getFittedVehicles), ShopItemType.BATTLE_BOOSTER))
            elif itemType == ShopItemType.MODULE:
                fmt = formatters.makeModuleFormatter()
            elif itemType == ShopItemType.PREMIUM:
                fmt = formatters.makePremiumPackFormatter()
            elif itemType == ShopItemType.SHELL:
                fmt = formatters.makeShellFormatter()
            self.__formattersMap[key] = fmt
            return fmt

    def __makeFormatterKey(self, itemType, criteria):
        entries = [itemType]
        if itemType == ShopItemType.VEHICLE and criteria.lookInInventory():
            entries.append('inventory')
        return ','.join(entries)

    def __collectItems(self, itemType, criteria):
        if itemType == ShopItemType.BOOSTER:
            return self.__collectBoosters(criteria)
        return self.__collectPremiumPacks() if itemType == ShopItemType.PREMIUM else self.__collectGuiItems(itemType, criteria)

    def __collectBoosters(self, criteria):
        return self.goodiesCache.getBoosters(criteria=criteria).itervalues()

    def __collectGuiItems(self, itemType, criteria):
        return self.itemsCache.items.getItems(_GUI_ITEMS_TYPE_MAP[itemType], criteria).itervalues()

    def __collectPremiumPacks(self):
        shop = self.itemsCache.items.shop
        defaultPrem = shop.defaults.premiumCost
        discountedPrem = shop.getPremiumCostWithDiscount()
        return [ PremiumPack(duration, discountedPrem.get(duration, cost), cost) for duration, cost in defaultPrem.iteritems() ]

    def getCompatVehicles(self, itemType, itemID):
        return self.__compatVehiclesCache[itemType][itemID]

    def getFittedVehicles(self, itemType, itemID):
        return self.__fittedVehiclesCache[itemType][itemID]

    def updateMappingCaches(self, *args):

        def collectAll(itemType):
            return ((itemType, item) for item in self.__collectItems(itemType, _EXTRA_ITEMS_CRITERIA_MAP[itemType]))

        types = [ShopItemType.DEVICE, ShopItemType.EQUIPMENT, ShopItemType.BATTLE_BOOSTER]
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
