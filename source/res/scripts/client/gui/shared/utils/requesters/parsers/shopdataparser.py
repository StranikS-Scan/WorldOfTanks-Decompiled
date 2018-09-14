# Embedded file name: scripts/client/gui/shared/utils/requesters/parsers/ShopDataParser.py
import weakref
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils import ParametersCache
from items import vehicles
import nations

class ShopDataParser(object):

    def __init__(self, data = None):

        def wrapper(method):
            obj = weakref.proxy(self)

            def caller(*args):
                return getattr(obj, method)(*args)

            return caller

        self.__modulesGetters = {GUI_ITEM_TYPE.VEHICLE: vehicles.g_list.getList,
         GUI_ITEM_TYPE.CHASSIS: vehicles.g_cache.chassis,
         GUI_ITEM_TYPE.ENGINE: vehicles.g_cache.engines,
         GUI_ITEM_TYPE.RADIO: vehicles.g_cache.radios,
         GUI_ITEM_TYPE.TURRET: vehicles.g_cache.turrets,
         GUI_ITEM_TYPE.GUN: vehicles.g_cache.guns,
         GUI_ITEM_TYPE.SHELL: vehicles.g_cache.shells,
         GUI_ITEM_TYPE.EQUIPMENT: wrapper('getEquipments'),
         GUI_ITEM_TYPE.OPTIONALDEVICE: wrapper('getOptionalDevices')}
        self.data = data or {}

    def __del__(self):
        self.__modulesGetters.clear()
        self.__modulesGetters = None
        return

    def getEquipments(self, nationID):
        allEquipments = vehicles.g_cache.equipments()
        return self.__filterByNation(allEquipments, ParametersCache.g_instance.getEquipmentParameters, nationID)

    def getOptionalDevices(self, nationID):
        allOptDevices = vehicles.g_cache.optionalDevices()
        return self.__filterByNation(allOptDevices, ParametersCache.g_instance.getOptionalDeviceParameters, nationID)

    def getItemsIterator(self, nationID = None, itemTypeID = None):
        hiddenInShop = self.data.get('notInShopItems', [])
        sellForGold = self.data.get('vehiclesToSellForGold', [])
        prices = self.getPrices()
        for intCD in self.__getListOfCompDescrs(nationID, itemTypeID):
            if intCD in prices:
                yield (intCD,
                 prices[intCD],
                 intCD in hiddenInShop,
                 intCD in sellForGold)

    def getPrices(self):
        return self.data.get('itemPrices', {})

    def getHiddenItems(self, nationID = None):
        hiddenItems = self.data.get('notInShopItems', set([]))
        result = set([])
        for intCD in self.__getListOfCompDescrs(nationID):
            if intCD in hiddenItems:
                result.add(intCD)

        return result

    def getSellForGoldItems(self):
        return self.data.get('vehiclesToSellForGold', set([]))

    def getPrice(self, intCD):
        return self.getPrices().get(intCD, (0, 0))

    def isHidden(self, intCD):
        return intCD in self.getHiddenItems()

    def isSellForGold(self, intCD):
        return intCD in self.getSellForGoldItems()

    def __getListOfCompDescrs(self, nationID = None, itemTypeID = None):
        itemTypes = [itemTypeID]
        if itemTypeID is None:
            itemTypes = self.__modulesGetters.keys()
        itemNations = [nationID]
        if nationID is None:
            itemNations = nations.INDICES.values()
        result = set()
        for nIdx in itemNations:
            for typeIdx in itemTypes:
                if typeIdx in self.__modulesGetters:
                    getter = self.__modulesGetters[typeIdx]
                    result |= set((v['compactDescr'] for v in getter(nIdx).itervalues()))

        return result

    def __filterByNation(self, items, getParameters, nationID):
        if nationID == nations.NONE_INDEX or nationID is None:
            return items
        else:
            result = {}
            for key, value in items.iteritems():
                params = getParameters(value)
                if nationID in params['nations']:
                    result[key] = value

            return result
