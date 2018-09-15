# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/parsers/ShopDataParser.py
import weakref
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_parameters import params
from gui.shared.money import Money
from items import vehicles, EQUIPMENT_TYPES, ItemsPrices
from items.components.c11n_constants import DecalType
import nations

class ShopDataParser(object):

    def __init__(self, data=None):

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
         GUI_ITEM_TYPE.BATTLE_BOOSTER: wrapper('getBattleBoosters'),
         GUI_ITEM_TYPE.OPTIONALDEVICE: wrapper('getOptionalDevices'),
         GUI_ITEM_TYPE.PAINT: wrapper('getPaints'),
         GUI_ITEM_TYPE.CAMOUFLAGE: wrapper('getCamouflages'),
         GUI_ITEM_TYPE.MODIFICATION: wrapper('getModifications'),
         GUI_ITEM_TYPE.DECAL: wrapper('getDecals'),
         GUI_ITEM_TYPE.EMBLEM: wrapper('getEmblems'),
         GUI_ITEM_TYPE.INSCRIPTION: wrapper('getInscriptions'),
         GUI_ITEM_TYPE.STYLE: wrapper('getStyles')}
        self.data = data or {}

    def __del__(self):
        self.__modulesGetters.clear()
        self.__modulesGetters = None
        return

    def getPaints(self, _):
        return vehicles.g_cache.customization20().paints

    def getCamouflages(self, _):
        return vehicles.g_cache.customization20().camouflages

    def getModifications(self, _):
        return vehicles.g_cache.customization20().modifications

    def getDecals(self, _):
        return vehicles.g_cache.customization20().decals

    def getEmblems(self, _):
        decals = vehicles.g_cache.customization20().decals
        return {intCD:decal for intCD, decal in decals.iteritems() if decal.type == DecalType.EMBLEM}

    def getInscriptions(self, _):
        decals = vehicles.g_cache.customization20().decals
        return {intCD:decal for intCD, decal in decals.iteritems() if decal.type == DecalType.INSCRIPTION}

    def getStyles(self, _):
        return vehicles.g_cache.customization20().styles

    def getEquipments(self, nationID):
        allEquipments = vehicles.g_cache.equipments()
        return self.__filterByNationAndEqType(allEquipments, params.EquipmentParams, nationID, EQUIPMENT_TYPES.regular)

    def getBattleBoosters(self, nationID):
        allEquipments = vehicles.g_cache.equipments()
        return self.__filterByNationAndEqType(allEquipments, params.EquipmentParams, nationID, EQUIPMENT_TYPES.battleBoosters)

    def getOptionalDevices(self, nationID):
        allOptDevices = vehicles.g_cache.optionalDevices()
        return self.__filterByNationAndEqType(allOptDevices, params.OptionalDeviceParams, nationID)

    def getItemsIterator(self, nationID=None, itemTypeID=None):
        prices = self.getPrices()
        for intCD in self.__getListOfCompDescrs(nationID, itemTypeID):
            if intCD in prices:
                yield intCD

    def getPrices(self):
        return self.data.get('itemPrices', ItemsPrices())

    def getHiddenItems(self, nationID=None):
        hiddenItems = self.data.get('notInShopItems', set([]))
        result = set([])
        for intCD in self.__getListOfCompDescrs(nationID):
            if intCD in hiddenItems:
                result.add(intCD)

        return result

    def getSellForGoldItems(self):
        return self.data.get('vehiclesToSellForGold', set([]))

    def getPrice(self, intCD):
        return Money.makeFromMoneyTuple(self._getRawPrice(intCD))

    def isHidden(self, intCD):
        return intCD in self.getHiddenItems()

    def isSellForGold(self, intCD):
        return intCD in self.getSellForGoldItems()

    def _getRawPrice(self, intCD):
        return self.getPrices().get(intCD, ())

    def __getListOfCompDescrs(self, nationID=None, itemTypeID=None):
        if itemTypeID is None:
            itemTypes = self.__modulesGetters.keys()
        elif not isinstance(itemTypeID, list):
            itemTypes = [itemTypeID]
        else:
            itemTypes = itemTypeID
        itemNations = [nationID]
        if nationID is None:
            itemNations = nations.INDICES.values()
        result = set()
        for nIdx in itemNations:
            for typeIdx in itemTypes:
                if typeIdx in self.__modulesGetters:
                    getter = self.__modulesGetters[typeIdx]
                    result |= set((v.compactDescr for v in getter(nIdx).itervalues()))

        return result

    @staticmethod
    def __filterByNationAndEqType(items, getParameters, nationID, eqType=None):
        ignoreNation = nationID == nations.NONE_INDEX or nationID is None
        ignoreEquipmentType = eqType is None
        if ignoreNation and ignoreEquipmentType:
            return items
        else:
            result = {}
            for key, value in items.iteritems():
                itemParams = getParameters(value)
                conditionNation = True if ignoreNation else nationID in itemParams.nations
                conditionType = True if ignoreEquipmentType else eqType == itemParams.equipmentType
                if conditionNation and conditionType:
                    result[key] = value

            return result
