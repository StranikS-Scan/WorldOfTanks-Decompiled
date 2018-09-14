# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/customization/CustomizationHelper.py
import math
import Math
from CurrentVehicle import g_currentVehicle
from time import time
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.locale.VEHICLE_CUSTOMIZATION import VEHICLE_CUSTOMIZATION
from gui.shared import g_itemsCache
from account_shared import getIGRCustomizedVehCompDescr
from gui.Scaleform.genConsts.CUSTOMIZATION_ITEM_TYPE import CUSTOMIZATION_ITEM_TYPE
from gui.game_control import g_instance
from helpers import i18n
from items import vehicles
from debug_utils import LOG_WARNING, LOG_DEBUG

def getTimeLeft(itemId, customizationType, nationId):
    item = checkItemOnVehicle(itemId, customizationType)
    isInHangar = isItemInHangar(customizationType, itemId, nationId)
    result = -1
    countSecondsInDay = 86400
    isUsed = True
    if item is not None:
        if customizationType != CUSTOMIZATION_ITEM_TYPE.INSCRIPTION:
            id, timeApply, countDays = item
        else:
            id, timeApply, countDays, _ = item
        if countDays > 0:
            endOfTime = timeApply + countDays * countSecondsInDay
            result = endOfTime - time()
        else:
            result = 0
    elif isInHangar:
        isUsed = False
        hangarItem = getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.CI_TYPES[customizationType], itemId, nationId)
        countDays = 0 if hangarItem.get('isPermanent') else hangarItem.get('quantity', 0)
        result = countSecondsInDay * countDays
    return (result, isUsed)


def getTimeLeftText(timeLeft):
    ms = i18n.makeString
    if timeLeft:
        secondsInDay = 86400
        secondsInHour = 3600
        secondsInMinute = 60
        if timeLeft > secondsInDay:
            timeLeft = int(math.ceil(timeLeft / secondsInDay))
            dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_DAYS)
        elif timeLeft > secondsInHour:
            timeLeft = int(math.ceil(timeLeft / secondsInHour))
            dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_HOURS)
        else:
            timeLeft = int(math.ceil(timeLeft / secondsInMinute))
            dimension = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_TEMPORAL_MINUTES)
        result = '{0}: {1}'.format(dimension, timeLeft)
    else:
        result = ms(VEHICLE_CUSTOMIZATION.TIMELEFT_INFINITYSYMBOL)
    return result


def checkItemOnVehicle(id, customizationType):
    items = getItemsOnVehicle(customizationType)
    itemIdIndex = 0
    for curItem in items:
        if curItem[itemIdIndex] == id:
            return curItem

    return None


def getItemsOnVehicle(customizationType):
    curVehDescr = __getDescriptorOfCurrentVehicle()
    items = [curVehDescr.camouflages, curVehDescr.playerEmblems, curVehDescr.playerInscriptions]
    return items[customizationType]


def __getDescriptorOfCurrentVehicle():
    igrRoomType = g_instance.igr.getRoomType()
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
    veh = g_currentVehicle.item
    defaultVehCompDescr = veh.descriptor.makeCompactDescr()
    igrVehCompDescr = getIGRCustomizedVehCompDescr(igrLayout, veh.invID, igrRoomType, defaultVehCompDescr)
    igrDescr = vehicles.VehicleDescr(igrVehCompDescr)
    return igrDescr


def clearStoredCustomizationData():
    storedItems = dict(AccountSettings.getSettings('customization'))
    clearStoredItems = {}
    for key, storedTypedItems in storedItems.iteritems():
        typedNewStoredItems = []
        inventoryItems = getInventoryItemsFor(key)
        for item in inventoryItems:
            for storedItem in storedTypedItems:
                if key == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE and storedItem[1] == item.get('id') or key != CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE and storedItem[1] == item.get('nationId') and storedItem[2] == item.get('id'):
                    typedNewStoredItems.append(storedItem)

        clearStoredItems[key] = typedNewStoredItems

    AccountSettings.setSettings('customization', clearStoredItems)


def updateVisitedItems(customizationName, visitedIds):
    if not g_currentVehicle.isPresent():
        return
    storedItems = dict(AccountSettings.getSettings('customization'))
    if not isinstance(visitedIds, set):
        LOG_WARNING('visitedIds will be in an list')
    updatedVisitedIds = []
    for item in visitedIds:
        if isinstance(item, int):
            updatedVisitedIds.append((g_currentVehicle.item.intCD, item))
        else:
            updatedVisitedIds.append((g_currentVehicle.item.intCD,) + item)

    curItems = {customizationName: updatedVisitedIds}
    curTypeItems = __integrateDicts(curItems, storedItems)
    AccountSettings.setSettings('customization', curTypeItems)


def getVisitedIDs(customizationName):
    result = []
    data = dict(AccountSettings.getSettings('customization'))
    if customizationName in data:
        result = data[customizationName]
    return result


def __integrateDicts(fromDict, toDict):
    for key, value in fromDict.iteritems():
        if key in toDict:
            if isinstance(value, dict) and isinstance(toDict[key], dict):
                toDict[key] = __integrateDicts(toDict[key], value)
            elif isinstance(value, list) and isinstance(toDict[key], list):
                if value != toDict[key]:
                    data = set(value)
                    data.update(set(toDict[key]))
                    toDict[key] = list(data)
            else:
                LOG_WARNING('incorrect type of data in data with key: ' + key)
        else:
            toDict[key] = value

    return toDict


def getInventoryItemsFor(type = None, isPermanent = None):
    inventoryRequester = g_itemsCache.items.inventory
    unassignedCI = inventoryRequester.getItemsData('customizations')
    res = []
    if isPermanent is not None:
        res.extend(__getCiFromDict(unassignedCI, isPermanent, type))
    else:
        res.extend(__getCiFromDict(unassignedCI, True, type))
        res.extend(__getCiFromDict(unassignedCI, False, type))
    return res


def __getCiFromDict(sourceDict, isPermanent, type = None):
    res = []
    for vehTypeCompDesr, ciItems in sourceDict.get(isPermanent, {}).iteritems():
        types = ciItems.keys() if type is None else [type]
        for t in types:
            for rawKey, rawValue in ciItems.get(t, {}).iteritems():
                res.append(__createCiItem(rawKey, rawValue, type, isPermanent, vehTypeCompDesr))

    return res


def __createCiItem(rawKey, rawValue, type, isPermanent, vehTypeCompDesr):
    return {'id': rawKey if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else rawKey[1],
     'type': type,
     'nationId': None if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else rawKey[0],
     'isPermanent': isPermanent,
     'vehTypeCompDesr': vehTypeCompDesr,
     'quantity': rawValue}


def checkIsNewItem(type, itemID, nationId = None):
    if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
        return itemID in getNewIdsByType(type, nationId)
    else:
        return (nationId, itemID) in getNewIdsByType(type, nationId)


def getNewIdsByType(type, nationId = None):
    visitedItems = getVisitedIDs(type)
    filteredVisitedItems = []
    filteredItems = []
    if g_currentVehicle.isPresent():
        for item in visitedItems:
            if item[0] == g_currentVehicle.item.intCD:
                filteredVisitedItems.append(item[1:] if len(item) > 2 else item[1])

        items = getInventoryItemsFor(type)
        filteredItems = filter(lambda item: item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD, items)
    if type != CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
        filteredItems = filter(lambda item: item['nationId'] == nationId, filteredItems)
    result = []
    for item in filteredItems:
        result.append(item.get('id') if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else (nationId, item.get('id')))

    result = set(result)
    return result.difference(set(filteredVisitedItems))


def isIdInDefaultSetup(type, itemID, position = None):
    res = False
    defaultElements, _, _ = getCustomizationElements(type, 0)
    for item in defaultElements:
        if item[0] == itemID and (position is None or defaultElements.index(item) == position):
            res = True
            break

    return res


def getItemFromHangar(type, itemID, nationId, position = None):
    if itemID is None:
        return
    else:
        igrRoomType = g_instance.igr.getRoomType()
        defaultElements, igrElements, dosierElements = getCustomizationElements(CUSTOMIZATION_ITEM_TYPE.CI_TYPES.index(type), igrRoomType)
        inventoryElements = getInventoryItemsFor(type)
        inventoryCount = 0
        temporalInventoryItem = None
        permanentInventoryItem = None
        inventoryVehTypeCompDesr = None
        for item in inventoryElements:
            vehTypeCompDesr = item.get('vehTypeCompDesr')
            if item.get('id') == itemID and (vehTypeCompDesr is None or vehTypeCompDesr == g_currentVehicle.item.intCD):
                if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE or item.get('nationId') == nationId:
                    if item.get('isPermanent'):
                        permanentInventoryItem = item
                        inventoryCount += item.get('quantity')
                        if inventoryVehTypeCompDesr is None:
                            inventoryVehTypeCompDesr = vehTypeCompDesr
                    else:
                        temporalInventoryItem = item

        if itemID in dosierElements:
            return __createCiItem(itemID if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else (nationId, itemID), inventoryCount + 1, type, True, g_currentVehicle.item.intCD)
        if temporalInventoryItem:
            return temporalInventoryItem
        if permanentInventoryItem:
            permanentInventoryItem['quantity'] = inventoryCount
            return permanentInventoryItem
        isDefault = False
        for item in igrElements:
            if item[0] == itemID and (item[2] == 0 or igrRoomType != 0 and (position is None or position is not None and igrElements[position] == item)):
                isDefault = True

        for item in defaultElements:
            if item[0] == itemID and (item[2] == 0 or igrRoomType != 0 and (position is None or position is not None and defaultElements[position] == item)):
                isDefault = True

        if isDefault:
            return __createCiItem(itemID if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else (nationId, itemID), inventoryCount, type, True, inventoryVehTypeCompDesr)
        return
        return


def areItemsInHangar(type, itemIDs, nationId):
    if itemIDs is None:
        return False
    else:
        defaultElements, igrElements, dosierElements = getCustomizationElements(type, 0)
        elementType = CUSTOMIZATION_ITEM_TYPE.CI_TYPES[type]
        inventoryElements = getInventoryItemsFor(elementType)
        for itemID in itemIDs:
            if itemID in dosierElements:
                return True
            for item in inventoryElements:
                if item.get('id') == itemID and (item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD):
                    if elementType == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE or item.get('nationId') == nationId:
                        return True

        return False


def isItemInHangar(type, itemID, nationId, position = None):
    if itemID is None:
        return False
    else:
        igrRoomType = g_instance.igr.getRoomType()
        defaultElements, igrElements, dosierElements = getCustomizationElements(type, igrRoomType)
        elementType = CUSTOMIZATION_ITEM_TYPE.CI_TYPES[type]
        inventoryElements = getInventoryItemsFor(elementType)
        if itemID in dosierElements:
            return True
        isInInventory = False
        for item in inventoryElements:
            if item.get('id') == itemID and (item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD):
                if elementType == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE or item.get('nationId') == nationId:
                    isInInventory = True
                    break

        if isInInventory:
            return True
        for item in igrElements:
            if item[0] == itemID and (item[2] == 0 or igrRoomType != 0 and (position is None or position is not None and igrElements[position] == item)):
                return True

        for item in defaultElements:
            if item[0] == itemID and (item[2] == 0 or igrRoomType != 0 and (position is None or position is not None and defaultElements[position] == item)):
                return True

        return False


def getCustomizationElements(type, igrType):
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
    veh = g_currentVehicle.item
    defaultVehCompDescr = veh.descriptor.makeCompactDescr()
    igrVehCompDescr = getIGRCustomizedVehCompDescr(igrLayout, veh.invID, igrType, defaultVehCompDescr)
    igrDescr = vehicles.VehicleDescr(igrVehCompDescr)
    dossier = g_itemsCache.items.getVehicleDossier(veh.intCD)
    if type == CUSTOMIZATION_ITEM_TYPE.CAMOUFLAGE:
        return (veh.descriptor.camouflages, igrDescr.camouflages, dossier.getBlock('camouflages'))
    elif type == CUSTOMIZATION_ITEM_TYPE.EMBLEM:
        return (veh.descriptor.playerEmblems, igrDescr.playerEmblems, dossier.getBlock('emblems'))
    elif type == CUSTOMIZATION_ITEM_TYPE.INSCRIPTION:
        return (veh.descriptor.playerInscriptions, igrDescr.playerInscriptions, dossier.getBlock('inscriptions'))
    else:
        return (None, None, None)
        return None


def getUpdatedDescriptor(vehDescr):
    igrRoomType = g_instance.igr.getRoomType()
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
    igrVehCompDescr = getIGRCustomizedVehCompDescr(igrLayout, g_currentVehicle.item.invID, igrRoomType, vehDescr.makeCompactDescr())
    return vehicles.VehicleDescr(igrVehCompDescr)
