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
from debug_utils import LOG_WARNING

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
        hangarItem = getItemFromHangar(CUSTOMIZATION_ITEM_TYPE.CI_TYPES[customizationType], itemId)
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
    items = [__getDescriptorOfCurrentVehicle().camouflages, __getDescriptorOfCurrentVehicle().playerEmblems, __getDescriptorOfCurrentVehicle().playerInscriptions]
    return items[customizationType]


def __getDescriptorOfCurrentVehicle():
    igrRoomType = g_instance.igr.getRoomType()
    igrLayout = g_itemsCache.items.inventory.getIgrCustomizationsLayout()
    veh = g_currentVehicle.item
    defaultVehCompDescr = veh.descriptor.makeCompactDescr()
    igrVehCompDescr = getIGRCustomizedVehCompDescr(igrLayout, veh.invID, igrRoomType, defaultVehCompDescr)
    igrDescr = vehicles.VehicleDescr(igrVehCompDescr)
    return igrDescr


def updateVisitedItems(customizationName, visitedIds):
    if not isinstance(visitedIds, set):
        LOG_WARNING('visitedIds will be in an list')
    visitedItems = dict(AccountSettings.getSettings('customization'))
    curItems = {customizationName: visitedIds}
    curTypeItems = __integrateDicts(curItems, visitedItems)
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
            elif isinstance(value, set) and (isinstance(toDict[key], set) or isinstance(toDict[key], tuple)):
                data = value
                data.update(toDict[key])
                toDict[key] = tuple(data)
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
    items = getInventoryItemsFor(type)
    filtered = filter(lambda item: item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD, items)
    if type != CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
        filtered = filter(lambda item: item['nationId'] == nationId, filtered)
    result = []
    for item in filtered:
        result.append(item.get('id') if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else (nationId, item.get('id')))

    result = set(result)
    return result.difference(visitedItems)


def isIdInDefaultSetup(type, itemID, position = None):
    res = False
    defaultElements, _, _ = getCustomizationElements(type, 0)
    for item in defaultElements:
        if item[0] == itemID and (position is None or defaultElements.index(item) == position):
            res = True
            break

    return res


def getItemFromHangar(type, itemID):
    if itemID is None:
        return
    else:
        dossier = g_itemsCache.items.getVehicleDossier(g_currentVehicle.item.intCD)
        dosierElements = dossier.getBlock(type)
        inventoryElements = getInventoryItemsFor(type)
        if itemID in dosierElements:
            return __createCiItem(itemID if type == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE else [None, itemID], 0, type, True, g_currentVehicle.item.intCD)
        for item in inventoryElements:
            if item.get('id') == itemID and (item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD):
                return item

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
                    if elementType == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
                        return True
                    else:
                        return item.get('nationId') == nationId

        return


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
        for item in inventoryElements:
            if item.get('id') == itemID and (item['vehTypeCompDesr'] is None or item['vehTypeCompDesr'] == g_currentVehicle.item.intCD):
                if elementType == CUSTOMIZATION_ITEM_TYPE.EMBLEM_TYPE:
                    return True
                else:
                    return item.get('nationId') == nationId

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
