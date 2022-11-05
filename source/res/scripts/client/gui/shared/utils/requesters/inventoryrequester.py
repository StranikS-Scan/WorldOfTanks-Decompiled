# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/InventoryRequester.py
import typing
from itertools import imap
from collections import namedtuple, defaultdict
from copy import deepcopy
import BigWorld
from adisp import adisp_async
from constants import CustomizationInvData, SkinInvData, VEHICLE_NO_INV_ID
from debug_utils import LOG_DEBUG
from items import vehicles, tankmen, getTypeOfCompactDescr, parseIntCompactDescr, makeIntCompactDescrByID
from items.components.c11n_components import C11N_PROGRESS_LEVEL_IDX, C11N_PROGRESS_PROGRESS_IDX, C11N_PROGRESS_VALUE_IDX
from items.components.c11n_constants import UNBOUND_VEH_KEY
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from nation_change.nation_change_helpers import activeInNationGroup
from post_progression_common import VehiclesPostProgression, VehicleState, EXT_DATA_SLOT_KEY, EXT_DATA_PROGRESSION_KEY
from skeletons.gui.shared.utils.requesters import IInventoryRequester
_DUMMY_VEH_POST_PROGRESSION = VehiclesPostProgression({VehiclesPostProgression.ROOT_KEY: {}})

class InventoryRequester(AbstractSyncDataRequester, IInventoryRequester):
    VEH_DATA = namedtuple('VEH_DATA', ('compDescr', 'descriptor', 'invID', 'crew'))
    ITEM_DATA = namedtuple('ITEM_DATA', ('compDescr', 'descriptor', 'count'))
    TMAN_DATA = namedtuple('TMAN_DATA', ('compDescr', 'descriptor', 'vehicle', 'invID'))
    OUTFIT_DATA = namedtuple('OUTFIT_DATA', ('compDescr', 'flags'))
    CUSTOMIZATION_PROGRESS_DATA = namedtuple('CUSTOMIZATION_PROGRESS_DATA', ('currentLevel', 'currentProgressOnLevel', 'maxProgressOnLevel'))

    def __init__(self):
        super(InventoryRequester, self).__init__()
        self.__itemsCache = defaultdict(dict)
        self.__itemsPreviousCache = defaultdict(dict)
        self.__vehsCDsByID = {}
        self.__vehsIDsByCD = {}
        self.__newC11nItems = {}
        self.__newC11nItemsByVehicleCache = {}
        self.__c11nProgressionData = {}
        self.__c11nProgressionForVehicle = {}
        self.__vehPostProgression = _DUMMY_VEH_POST_PROGRESSION

    def clear(self):
        self.__itemsCache.clear()
        self.__itemsPreviousCache.clear()
        self.__vehsCDsByID.clear()
        self.__vehsIDsByCD.clear()
        self.__c11nProgressionData.clear()
        self.__c11nProgressionForVehicle.clear()
        self.__vehPostProgression = _DUMMY_VEH_POST_PROGRESSION
        super(InventoryRequester, self).clear()

    def invalidateItem(self, itemTypeID, invIdx):
        cache = self.__itemsCache[itemTypeID]
        if itemTypeID == 29:
            print invIdx
        if invIdx in cache:
            self.__itemsPreviousCache[itemTypeID][invIdx] = cache[invIdx]
            del cache[invIdx]
            return True
        if itemTypeID == GUI_ITEM_TYPE.CUSTOMIZATION:
            self.updateC11nItemNoveltyData(invIdx)
            self.updateC11nProgressionDataForItem(invIdx)
        return False

    def getC11nItemAppliedVehicles(self, itemCD):
        _, itemType, itemId = parseIntCompactDescr(itemCD)
        path = (GUI_ITEM_TYPE.CUSTOMIZATION,
         CustomizationInvData.DRESSED,
         itemType,
         itemId)
        vehs = self.getCacheValueByPath(path, defaultValue={})
        return vehs.keys()

    def getC11nItemAppliedOnVehicleCount(self, itemCD, vehicleIntCD):
        _, itemType, itemId = parseIntCompactDescr(itemCD)
        path = (GUI_ITEM_TYPE.CUSTOMIZATION,
         CustomizationInvData.DRESSED,
         itemType,
         itemId,
         vehicleIntCD)
        count = self.getCacheValueByPath(path, defaultValue=0)
        return count

    def initC11nItemsNoveltyData(self):
        self.__newC11nItems.clear()
        self.__newC11nItemsByVehicleCache.clear()
        customizationInvData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        newItemsInvData = customizationInvData.get(CustomizationInvData.NOVELTY_DATA, {})
        for cType, itemsData in newItemsInvData.iteritems():
            for itemId, itemData in itemsData.iteritems():
                if itemData is not None:
                    intCD = makeIntCompactDescrByID('customizationItem', cType, itemId)
                    self.__newC11nItems[intCD] = itemData

        return

    def updateC11nItemNoveltyData(self, itemIntCD):
        itemData = self.__getNewCustomizationsItemsData(itemIntCD)
        if itemData:
            self.__newC11nItems[itemIntCD] = itemData
            itemDescriptor = vehicles.getItemByCompactDescr(itemIntCD)
            for vehCD, vehData in self.__newC11nItemsByVehicleCache.iteritems():
                counter = 0
                vehicleType = vehicles.getVehicleType(vehCD)
                if not itemDescriptor.filter or itemDescriptor.filter.matchVehicleType(vehicleType):
                    counter += itemData.get(UNBOUND_VEH_KEY, 0)
                    counter += itemData.get(vehCD, 0)
                if counter:
                    vehData[itemIntCD] = counter
                vehData.pop(itemIntCD, None)

        else:
            self.__newC11nItems.pop(itemIntCD, None)
            for vehData in self.__newC11nItemsByVehicleCache.itervalues():
                vehData.pop(itemIntCD, None)

        return

    def getC11nItemNoveltyData(self, itemIntCD):
        return self.__newC11nItems.get(itemIntCD, {})

    def getC11nItemsNoveltyCounters(self, vehicleType):
        vehicleIntCD = vehicleType.compactDescr
        newC11nItems = self.__newC11nItemsByVehicleCache.get(vehicleIntCD)
        if newC11nItems is not None:
            return newC11nItems
        else:
            self.__newC11nItemsByVehicleCache[vehicleIntCD] = self.__getC11nItemNoveltyDataForVehicle(vehicleType)
            return self.__newC11nItemsByVehicleCache[vehicleIntCD]

    def updateC11nProgressionDataForItem(self, itemIntCD):
        if not self.__c11nProgressionData:
            self.updateC11nProgressionData()
            return
        if itemIntCD in self.__c11nProgressionData:
            del self.__c11nProgressionData[itemIntCD]
        customizationInvData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        itemsInvData = customizationInvData.get(CustomizationInvData.PROGRESSION, {})
        _, cType, idx = parseIntCompactDescr(itemIntCD)
        if cType in itemsInvData:
            typeInvData = itemsInvData[cType]
            if idx in typeInvData:
                itemData = typeInvData[idx]
                self.__updateC11nProgressionDataForItem(itemIntCD, itemData)

    def updateC11nProgressionData(self):
        self.__c11nProgressionData = {}
        customizationInvData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        itemsInvData = customizationInvData.get(CustomizationInvData.PROGRESSION, {})
        for cType, typeInvData in itemsInvData.iteritems():
            for idx, itemData in typeInvData.iteritems():
                itemIntCD = makeIntCompactDescrByID('customizationItem', cType, idx)
                self.__updateC11nProgressionDataForItem(itemIntCD, itemData)

    def getC11nProgressionDataForItem(self, itemIntCD):
        if not self.__c11nProgressionData:
            self.updateC11nProgressionData()
        return self.__c11nProgressionData.get(itemIntCD)

    def getC11nProgressionDataForVehicle(self, vehicleIntCD):
        if not self.__c11nProgressionData:
            self.updateC11nProgressionData()
        result = {}
        vehicleType = vehicles.getVehicleType(vehicleIntCD)
        for itemIntCD, progressionData in self.__c11nProgressionForVehicle.get(UNBOUND_VEH_KEY, {}).iteritems():
            itemDescriptor = vehicles.getItemByCompactDescr(itemIntCD)
            if not itemDescriptor.filter or itemDescriptor.filter.matchVehicleType(vehicleType):
                result[itemIntCD] = progressionData

        result.update(self.__c11nProgressionForVehicle.get(vehicleIntCD, {}))
        return result

    def getC11nProgressionData(self, itemIntCD, vehicleIntCD):
        itemData = self.getC11nProgressionDataForItem(itemIntCD)
        if itemData is not None:
            vehData = itemData.get(vehicleIntCD)
            if vehData is not None:
                return vehData
            return itemData.get(0)
        else:
            return

    def getC11nOutfitsFromPool(self, vehicleIntCD):
        path = (GUI_ITEM_TYPE.CUSTOMIZATION, CustomizationInvData.OUTFITS_POOL, vehicleIntCD)
        poolData = self.getCacheValueByPath(path, defaultValue=[])
        return deepcopy(poolData)

    def getItemsData(self, itemTypeID):
        invData = self.getCacheValue(itemTypeID, {})
        for invID in invData.get('compDescr', {}).iterkeys():
            self.__makeItem(itemTypeID, invID)

        return self.__itemsCache[itemTypeID]

    def getItemData(self, typeCompDescr):
        itemTypeID = getTypeOfCompactDescr(typeCompDescr)
        return self.getVehicleData(self.__vehsIDsByCD.get(typeCompDescr, -1)) if itemTypeID == GUI_ITEM_TYPE.VEHICLE else self.__makeSimpleItem(typeCompDescr)

    def getTankmanData(self, tmanInvID):
        return self.__makeTankman(tmanInvID)

    def getVehicleData(self, vehInvID):
        return self.__makeVehicle(vehInvID)

    def getOutfitData(self, intCD, season):
        return self.__makeOutfit(intCD, season)

    def getPreviousItem(self, itemTypeID, invDataIdx):
        return self.__itemsPreviousCache[itemTypeID].get(invDataIdx)

    def getItems(self, itemTypeIdx, dataIdx=None):
        if itemTypeIdx == GUI_ITEM_TYPE.VEHICLE:
            return self.__getVehiclesData(dataIdx)
        if itemTypeIdx == GUI_ITEM_TYPE.TANKMAN:
            return self.__getTankmenData(dataIdx)
        if itemTypeIdx == GUI_ITEM_TYPE.CUSTOMIZATION:
            return self.__getCustomizationsData(dataIdx)
        return self.__getCrewSkinsData(dataIdx) if itemTypeIdx == GUI_ITEM_TYPE.CREW_SKINS else self.__getItemsData(itemTypeIdx, dataIdx)

    def getC11nSerialNumber(self, itemCD):
        _, itemType, itemID = parseIntCompactDescr(itemCD)
        path = (GUI_ITEM_TYPE.CUSTOMIZATION,
         CustomizationInvData.SERIAL_NUMBERS,
         itemType,
         itemID,
         'serial_number')
        return self.getCacheValueByPath(path)

    def getFreeSlots(self, vehiclesSlots):

        def checker(vehData):
            flag = vehData.get('extraSettings', 0)
            return activeInNationGroup(flag)

        vehcielsData = self.__getVehiclesData() or {}
        activeVehicles = sum(imap(checker, vehcielsData.itervalues()))
        return vehiclesSlots - activeVehicles

    def getInventoryEnhancements(self):
        return self.getCacheValue('enhancements', {})

    def getInstalledEnhancements(self):
        return self.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {}).get('enhancements', {})

    def getIventoryVehiclesCDs(self):
        return self.__vehsCDsByID.values()

    def getInvIDsIterator(self):
        return self.__vehsCDsByID.iterkeys()

    def getVehPostProgression(self, vehIntCD):
        return self.__vehPostProgression.getVehicleState(vehIntCD)

    def getVehExtData(self, vehIntCD):
        return {EXT_DATA_SLOT_KEY: self.getDynSlotTypeID(vehIntCD),
         EXT_DATA_PROGRESSION_KEY: self.getVehPostProgression(vehIntCD)}

    def getVehPostProgressionFeaturesListByCD(self, vehIntCD):
        return self.__vehPostProgression.getVehicleFeaturesList(vehIntCD)

    def getDynSlotTypeID(self, vehIntCD):
        return self.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {}).get('customRoleSlots', {}).get(vehIntCD, 0)

    @adisp_async
    def _requestCache(self, callback=None):
        BigWorld.player().inventory.getCache(lambda resID, value: self._response(resID, value, callback))

    def _response(self, resID, invData, callback=None):
        self.__vehsCDsByID = {}
        if invData is not None:
            for invID, vCompDescr in invData[GUI_ITEM_TYPE.VEHICLE]['compDescr'].iteritems():
                self.__vehsCDsByID[invID] = vehicles.makeIntCompactDescrByID('vehicle', *vehicles.parseVehicleCompactDescr(vCompDescr))

            self.__vehPostProgression = VehiclesPostProgression(invData[GUI_ITEM_TYPE.VEHICLE])
        else:
            self.__vehPostProgression = _DUMMY_VEH_POST_PROGRESSION
        self.__vehsIDsByCD = dict(((v, k) for k, v in self.__vehsCDsByID.iteritems()))
        super(InventoryRequester, self)._response(resID, invData, callback)
        return

    def __getItemsData(self, itemTypeIdx, compactDescr=None):
        result = self.getCacheValue(itemTypeIdx)
        return result.get(compactDescr) if result is not None and compactDescr is not None else result

    def __makeItem(self, itemTypeID, invDataIdx):
        return self.__getMaker(itemTypeID)(invDataIdx)

    def __getMaker(self, itemTypeID):
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            return self.__makeVehicle
        return self.__makeTankman if itemTypeID == GUI_ITEM_TYPE.TANKMAN else self.__makeSimpleItem

    def __makeVehicle(self, vehInvID):
        if vehInvID not in self.__vehsCDsByID:
            return
        else:
            typeCompDescr = self.__vehsCDsByID[vehInvID]
            cache = self.__itemsCache[GUI_ITEM_TYPE.VEHICLE]
            if typeCompDescr in cache:
                return cache[typeCompDescr]
            itemsInvData = self.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {})

            def value(key, default=None):
                return itemsInvData.get(key, {}).get(vehInvID, default)

            compactDescr = value('compDescr')
            if compactDescr is None:
                return
            try:
                item = cache[typeCompDescr] = self.VEH_DATA(value('compDescr'), vehicles.VehicleDescr(compactDescr=compactDescr), vehInvID, value('crew', []))
            except Exception:
                LOG_DEBUG('Error while building vehicle from inventory', vehInvID, typeCompDescr)
                return

            return item

    def __makeTankman(self, tmanInvID):
        cache = self.__itemsCache[GUI_ITEM_TYPE.TANKMAN]
        if tmanInvID in cache:
            return cache[tmanInvID]
        else:
            itemsInvData = self.getCacheValue(GUI_ITEM_TYPE.TANKMAN, {})

            def value(key, default=None):
                return itemsInvData.get(key, {}).get(tmanInvID, default)

            compactDescr = value('compDescr')
            if compactDescr is None:
                return
            item = cache[tmanInvID] = self.TMAN_DATA(compactDescr, tankmen.TankmanDescr(compactDescr), value('vehicle', VEHICLE_NO_INV_ID), tmanInvID)
            return item

    def __makeSimpleItem(self, typeCompDescr):
        itemTypeID = getTypeOfCompactDescr(typeCompDescr)
        cache = self.__itemsCache[itemTypeID]
        if typeCompDescr in cache:
            return cache[typeCompDescr]
        else:
            itemsInvData = self.getCacheValue(itemTypeID, {})
            if typeCompDescr not in itemsInvData:
                return None
            data = self.ITEM_DATA(typeCompDescr, vehicles.getItemByCompactDescr(typeCompDescr), itemsInvData[typeCompDescr])
            item = cache[typeCompDescr] = data
            return item

    def __makeOutfit(self, intCD, season):
        cache = self.__itemsCache[GUI_ITEM_TYPE.OUTFIT]
        if (intCD, season) in cache:
            return cache[intCD, season]
        else:
            invData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
            outfitsData = invData.get(CustomizationInvData.OUTFITS, {})
            vehicleOutfits = outfitsData.get(intCD, {})
            if season not in vehicleOutfits:
                return None
            outfitCD = cache[intCD, season] = vehicleOutfits[season]
            return outfitCD

    def __getTankmenData(self, inventoryID=None):
        tankmanItemsData = self.__getItemsData(vehicles._TANKMAN)
        if tankmanItemsData is None:
            return
        elif inventoryID is not None:
            return self.__getTankmanData(tankmanItemsData, inventoryID)
        else:
            result = dict()
            for invID in tankmanItemsData.get('compDescr', dict()).iterkeys():
                result[invID] = self.__getTankmanData(tankmanItemsData, invID)

            return result

    def __getTankmanData(self, tankmanItemsData, invID):
        if invID not in tankmanItemsData['compDescr'].keys():
            return
        else:
            result = dict()
            for key, values in tankmanItemsData.iteritems():
                value = values.get(invID)
                if value is not None:
                    result[key] = value

            return result

    def __getVehiclesData(self, inventoryID=None):
        vehItemsData = self.__getItemsData(vehicles._VEHICLE)
        if vehItemsData is None:
            return
        elif inventoryID is not None:
            return self.__getVehicleData(vehItemsData, inventoryID)
        else:
            result = dict()
            for invID in vehItemsData.get('compDescr', dict()).iterkeys():
                result[invID] = self.__getVehicleData(vehItemsData, invID)

            return result

    def __getVehicleData(self, vehItemsData, invID):
        if invID not in vehItemsData['compDescr'].keys():
            return
        else:
            result = dict()
            for key, values in vehItemsData.iteritems():
                value = values.get(invID)
                if value is not None:
                    result[key] = value

            return result

    def __getCustomizationsData(self, intCD):
        _, cType, idx = parseIntCompactDescr(intCD)
        customizationInvData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        itemsInvData = customizationInvData.get(CustomizationInvData.ITEMS, {})
        typeInvData = itemsInvData.get(cType, {})
        return typeInvData.get(idx, {})

    def __getNewCustomizationsItemsData(self, intCD):
        _, cType, idx = parseIntCompactDescr(intCD)
        customizationInvData = self.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        itemsInvData = customizationInvData.get(CustomizationInvData.NOVELTY_DATA, {})
        typeInvData = itemsInvData.get(cType, {})
        return typeInvData.get(idx, [])

    def __getC11nItemNoveltyDataForVehicle(self, vehicleType):
        vehCache = {}
        for itemCD, itemData in self.__newC11nItems.iteritems():
            counter = 0
            itemDescriptor = vehicles.getItemByCompactDescr(itemCD)
            if not itemDescriptor.filter or itemDescriptor.filter.matchVehicleType(vehicleType):
                counter += itemData.get(UNBOUND_VEH_KEY, 0)
                counter += itemData.get(vehicleType.compactDescr, 0)
            if counter:
                vehCache[itemCD] = counter

        return vehCache

    def __updateC11nProgressionDataForItem(self, itemIntCD, itemData):
        if itemData is not None:
            c11nProgressionData = {}
            for vehicleIntCD, vehData in itemData.iteritems():
                progressionData = self.CUSTOMIZATION_PROGRESS_DATA(currentLevel=vehData[C11N_PROGRESS_LEVEL_IDX], currentProgressOnLevel=vehData[C11N_PROGRESS_PROGRESS_IDX], maxProgressOnLevel=vehData[C11N_PROGRESS_VALUE_IDX])
                c11nProgressionData[vehicleIntCD] = progressionData
                self.__c11nProgressionForVehicle.setdefault(vehicleIntCD, {})[itemIntCD] = progressionData

            self.__c11nProgressionData[itemIntCD] = c11nProgressionData
        else:
            self.__c11nProgressionData.pop(itemIntCD, None)
        return

    def __getCrewSkinsData(self, idx):
        crewSkinsInvData = self.getCacheValue(GUI_ITEM_TYPE.CREW_SKINS, {})
        itemsInvData = crewSkinsInvData.get(SkinInvData.ITEMS, {})
        return itemsInvData.get(idx, 0) if idx is not None else itemsInvData
