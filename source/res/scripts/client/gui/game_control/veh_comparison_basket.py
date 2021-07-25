# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/veh_comparison_basket.py
from collections import namedtuple, defaultdict
from itertools import imap
import typing
import BigWorld
import Event
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.SystemMessages import SM_TYPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.local_cache import FileLocalCache
from items import getTypeOfCompactDescr, ITEM_TYPE_NAMES, vehicles, EQUIPMENT_TYPES, ITEM_TYPES
from items.components.detachment_constants import NO_DETACHMENT_ID
from items.vehicles import VehicleDescr
from nation_change_helpers.client_nation_change_helper import getValidVehicleCDForNationChange
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.game_control import IVehicleComparisonBasket, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict, Any
    from gui.shared.gui_items.vehicle_modules import VehicleChassis
    from gui.shared.gui_items.vehicle_modules import VehicleModule
    from gui.shared.gui_items.artefacts import BattleBooster
MAX_VEHICLES_TO_COMPARE_COUNT = 20
_DEF_SHELL_INDEX = 0
_ChangedData = namedtuple('_ChangedData', ('addedIDXs', 'addedCDs', 'removedIDXs', 'removedCDs', 'isFullChanged'))
_COMPARE_INVALID_CRITERIA = ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.SECRET

def getVehicleCriteriaForComparing():
    return _COMPARE_INVALID_CRITERIA


def isValidVehicleForComparing(vehicle):
    return vehicle is not None and getVehicleCriteriaForComparing()(vehicle)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getSuitableChassis(vehicle, itemsCache=None):
    chassis = []
    for _, _, nodeCD, _ in vehicle.getUnlocksDescrs():
        itemTypeID = getTypeOfCompactDescr(nodeCD)
        if itemTypeID == GUI_ITEM_TYPE.CHASSIS:
            chassisCand = itemsCache.items.getItemByCD(nodeCD)
            if chassisCand.mayInstall(vehicle) and not chassisCand.isInstalled(vehicle):
                chassis.append(chassisCand)

    return chassis


def getInstalledModulesCDs(vehicle):
    outcome = []
    for guiItemType in GUI_ITEM_TYPE.VEHICLE_MODULES:
        if guiItemType == GUI_ITEM_TYPE.TURRET and not vehicle.hasTurrets:
            outcome.append(None)
        component = vehicle.descriptor.getComponentsByType(ITEM_TYPE_NAMES[guiItemType])
        outcome.append(component[0].compactDescr)

    return outcome


def _isVehHasCamouflage(vehicle):
    return bool(vehicle.getBonusCamo())


def _removeVehicleCamouflages(vehicle):
    descr = vehicle.descriptor
    for i in xrange(len(descr.camouflages)):
        descr.setCamouflage(i, None, 0, 0)

    return


def _getVehicleEquipment(vehicle):
    return vehicle.consumables.installed.getIntCDs(default=None)


def _makeStrCD(vehicle):
    return vehicle.descriptor.makeCompactDescr()


def _operationLocked(func):

    def funcWithMessage(self, *args, **kwargs):
        if not self.isLocked:
            return func(self, *args, **kwargs)
        SystemMessages.pushI18nMessage('#system_messages:vehicleCompare/disabled', type=SM_TYPE.Error)

    return funcWithMessage


def _ErrorNotification(func):

    def funcWithMessage(self, *args, **kwargs):
        if self.isEnabled() and self.isAvailable():
            return func(self, *args, **kwargs)
        SystemMessages.pushI18nMessage('#system_messages:vehicleCompare/disabled', type=SM_TYPE.Error)

    return funcWithMessage


def _indexCanBePerformed(func):

    def __wrapper(self, *args, **kwargs):
        index = args[0]
        vehCount = self.getVehiclesCount()
        if not 0 <= index < vehCount:
            LOG_WARNING('Item with requested index ({}), can not be performed! Vehicles count in basket: {}'.format(index, vehCount))
            return None
        else:
            return func(self, *args, **kwargs)

    return __wrapper


class CONFIGURATION_TYPES(object):
    BASIC = 'basic'
    CURRENT = 'current'
    CUSTOM = 'custom'


class PerksData(object):
    __slots__ = ('points', 'instructorPoints')

    def __init__(self, points=None, instructorPoints=None):
        super(PerksData, self).__init__()
        self.points = defaultdict(int)
        if points:
            self.points.update(points)
        self.instructorPoints = defaultdict(int)
        if instructorPoints:
            self.instructorPoints.update(instructorPoints)

    @property
    def perks(self):
        result = self.points.copy()
        for perkID, point in self.instructorPoints.iteritems():
            result[perkID] += point

        return result

    def clone(self):
        return PerksData(self.points, self.instructorPoints)

    def __eq__(self, other):
        if self is other:
            return True
        return False if not isinstance(other, PerksData) else self.points == other.points and self.instructorPoints == other.instructorPoints

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return 'points:' + str(dict(self.points)) + ', instructorPoints:' + str(dict(self.instructorPoints))


class _VehCmpCache(FileLocalCache):
    VERSION = 4

    def __init__(self, databaseID, dataSetter, dataGetter):
        super(_VehCmpCache, self).__init__('veh_cmp_cache', ('basket_state', databaseID), async=True)
        self.__dataSetter = dataSetter
        self.__dataGetter = dataGetter

    def _getCache(self):
        vehsData = []
        for vehCompareData in self.__dataGetter():
            vehsData.append((vehCompareData.getVehicleStrCD(),
             vehCompareData.getEquipment(),
             vehCompareData.getPerks(),
             vehCompareData.getSelectedShellIndex(),
             vehCompareData.hasCamouflage(),
             vehCompareData.getBattleBooster()))

        return (self.VERSION, vehsData)

    def _setCache(self, data):
        if isinstance(data, (tuple, list)) and len(data) == 2:
            if self.VERSION == data[0]:
                self.__dataSetter(data[1])
        return data

    def clear(self):
        self.__dataSetter = None
        self.__dataGetter = None
        super(_VehCmpCache, self).clear()
        return


class _VehCompareData(object):

    def __init__(self, vehicleIntCD, vehicleStrCD, vehStockStrCD, isFromCache=False):
        super(_VehCompareData, self).__init__()
        self.__isInInventory = False
        self.__isFromCache = isFromCache
        self.__invVehStrCD = None
        self.__intCD = vehicleIntCD
        self.__strCD = vehicleStrCD
        self.__stockVehStrCD = vehStockStrCD
        self.__perks = self.getStockPerks()
        self.__inventoryPerks = self.getStockPerks()
        self.__equipment = self.getNoEquipmentLayout()
        self.__invEquipment = self.getNoEquipmentLayout()
        self.__invBattleBooster = None
        self.__battleBooster = None
        self.__selectedShellIndex = _DEF_SHELL_INDEX
        self.__invHasCamouflage = False
        self.__hasCamouflage = False
        return

    def setIsInInventory(self, value):
        self.__isInInventory = value

    def setSelectedShellIndex(self, idx):
        self.__selectedShellIndex = idx

    def setInvVehStrCD(self, value):
        self.__invVehStrCD = value

    def setPerks(self, perks):
        self.__perks = perks

    def setInventoryPerks(self, perks):
        self.__inventoryPerks = perks

    def setVehicleStrCD(self, strCD):
        self.__strCD = strCD

    def setBattleBooster(self, battleBooster):
        self.__battleBooster = battleBooster

    def setInvBattleBooster(self, battleBooster):
        self.__invBattleBooster = battleBooster

    def setEquipment(self, equipment):
        self.__equipment = equipment

    def setInvEquipment(self, equipment):
        self.__invEquipment = equipment

    def setHasCamouflage(self, value):
        self.__hasCamouflage = value

    def setInvHasCamouflage(self, value):
        self.__invHasCamouflage = value

    def getSelectedShellIndex(self):
        return self.__selectedShellIndex

    def getInventoryShellIndex(self):
        return _DEF_SHELL_INDEX

    def getInvEquipment(self):
        return self.__invEquipment

    def getInvPerks(self):
        return self.__inventoryPerks.clone()

    def getInvBattleBooster(self):
        return self.__invBattleBooster

    def getBattleBooster(self):
        return self.__battleBooster

    def getVehicleCD(self):
        return self.__intCD

    def getStockPerks(self):
        return PerksData()

    def getStockEquipment(self):
        equipmentIDs = self.getNoEquipmentLayout()
        self.__addBuiltInEquipment(equipmentIDs)
        return equipmentIDs

    def getConfigurationType(self):
        cType = CONFIGURATION_TYPES.CUSTOM
        if self.__selectedShellIndex != self.getInventoryShellIndex():
            return cType
        if self.__hasCamouflage != self.__invHasCamouflage:
            return cType
        if self.__strCD == self.__invVehStrCD:
            if self.__equipment == self.__invEquipment and self.__perks == self.__inventoryPerks:
                cType = CONFIGURATION_TYPES.CURRENT
        elif self.__strCD == self.__stockVehStrCD:
            if self.getEquipment() == self.getStockEquipment() and self.__perks == self.getStockPerks():
                cType = CONFIGURATION_TYPES.BASIC
        return cType

    def getVehicleStrCD(self):
        return self.__strCD

    def getInvVehStrCD(self):
        return self.__invVehStrCD

    def getStockVehStrCD(self):
        return self.__stockVehStrCD

    def getPerks(self):
        return self.__perks.clone()

    def getEquipment(self):
        equipmentIDs = self.__equipment[:]
        self.__addBuiltInEquipment(equipmentIDs)
        return equipmentIDs

    def isFromCache(self):
        return self.__isFromCache

    def hasCamouflage(self):
        return self.__hasCamouflage

    def invHasCamouflage(self):
        return self.__invHasCamouflage

    def isInInventory(self):
        return self.__isInInventory

    def clone(self):
        dataClone = _VehCompareData(self.getVehicleCD(), self.getVehicleStrCD(), self.getStockVehStrCD())
        dataClone.setIsInInventory(self.isInInventory())
        dataClone.setInvVehStrCD(self.getInvVehStrCD())
        dataClone.setPerks(self.getPerks())
        dataClone.setInventoryPerks(self.__inventoryPerks)
        dataClone.setEquipment(self.getEquipment())
        dataClone.setBattleBooster(self.getBattleBooster())
        dataClone.setInvEquipment(self.__invEquipment)
        dataClone.setInvBattleBooster(self.__invBattleBooster)
        dataClone.setHasCamouflage(self.__hasCamouflage)
        dataClone.setInvHasCamouflage(self.__invHasCamouflage)
        dataClone.setSelectedShellIndex(self.getSelectedShellIndex())
        return dataClone

    def getNoEquipmentLayout(self):
        vehicleType = self.__getVehicleType()
        eqCapacity = vehicleType.supplySlots.getAmountForType(ITEM_TYPES.equipment, EQUIPMENT_TYPES.regular)
        return [None] * eqCapacity

    def __addBuiltInEquipment(self, equipmentIDs):
        if not self.__isInInventory:
            vehicleType = self.__getVehicleType()
            builtInEquipmentIDs = vehicles.getBuiltinEqsForVehicle(vehicleType)
            for slotId, eqID in enumerate(builtInEquipmentIDs):
                equipmentIDs[slotId] = eqID

    def __getVehicleType(self):
        _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(self.__intCD)
        return vehicles.g_cache.vehicle(nationID, vehicleTypeID)


class VehComparisonBasket(IVehicleComparisonBasket):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)
    detachmentCache = dependency.descriptor(IDetachmentCache)

    def __init__(self):
        super(VehComparisonBasket, self).__init__()
        self.__isLocked = False
        self.__vehicles = []
        self.__isFull = False
        self.onChange = Event.Event()
        self.onParametersChange = Event.Event()
        self.onSwitchChange = Event.Event()
        self.onNationChange = Event.Event()
        self.__isEnabled = True
        self.__cache = None
        return

    def onConnected(self):
        self.__vehicles = []

    def onLobbyStarted(self, ctx):
        self.__isEnabled = self.lobbyContext.getServerSettings().isVehicleComparingEnabled() and not self.bootcampController.isInBootcamp()

    def onLobbyInited(self, event):
        if self.isEnabled() and self.isAvailable() and not self.isLocked:
            if self.__cache is None:
                self.__cache = self._createCache()
                if self.__cache is not None:
                    self.__cache.read()
        self.__initHandlers()
        return

    def onAvatarBecomePlayer(self):
        self.__disposeHandlers()

    def onDisconnected(self):
        self.writeCache()
        self.__disposeCache()
        self.__vehicles = []
        self.__isFull = False
        self.__disposeHandlers()
        super(VehComparisonBasket, self).onDisconnected()

    def fini(self):
        self.writeCache()
        self.__disposeCache()
        self.__vehicles = None
        self.onChange.clear()
        self.onParametersChange.clear()
        self.onSwitchChange.clear()
        self.onNationChange.clear()
        super(VehComparisonBasket, self).fini()
        return

    @_ErrorNotification
    @_indexCanBePerformed
    def applyNewParameters(self, index, vehicle, perks, selectedShellIndex=0):
        vehCompareData = self.__vehicles[index]
        if vehCompareData.getVehicleCD() != vehicle.intCD:
            raise SoftException('Int-type compact descriptor are different')
        isChanged = False
        copyVehicle = Vehicle(_makeStrCD(vehicle), proxy=self.itemsCache.items)
        copyVehicle.setOutfits(vehicle)
        hasCamouflage = _isVehHasCamouflage(copyVehicle)
        if hasCamouflage:
            _removeVehicleCamouflages(copyVehicle)
        vehCompareData.setHasCamouflage(hasCamouflage)
        newStrCD = _makeStrCD(copyVehicle)
        if vehCompareData.getVehicleStrCD() != newStrCD:
            isChanged = True
            vehCompareData.setVehicleStrCD(newStrCD)
        if vehicle.battleBoosters.installed.getCapacity() > 0:
            newBattleBooster = vehicle.battleBoosters.installed[0]
            if vehCompareData.getBattleBooster() != newBattleBooster:
                isChanged = True
                vehCompareData.setBattleBooster(newBattleBooster)
        newEqs = _getVehicleEquipment(vehicle)
        if vehCompareData.getEquipment() != newEqs:
            isChanged = True
            vehCompareData.setEquipment(newEqs)
        if vehCompareData.getSelectedShellIndex() != selectedShellIndex:
            vehCompareData.setSelectedShellIndex(selectedShellIndex)
            isChanged = True
        if vehCompareData.getPerks() != perks:
            vehCompareData.setPerks(perks)
            isChanged = True
        if isChanged:
            self.onParametersChange((index,))
        else:
            LOG_DEBUG('Modules has not been applied because they are not different.')

    @_ErrorNotification
    def addVehicle(self, vehicleCompactDesr, initParameters=None):
        if not isinstance(vehicleCompactDesr, (int, float)):
            raise SoftException('Int-type compact descriptor is invalid: '.format(vehicleCompactDesr))
        if self.__canBeAdded():
            vehicleCompactDesr = getValidVehicleCDForNationChange(vehicleCompactDesr)
            vehCmpData = self._createVehCompareData(vehicleCompactDesr, initParameters)
            if vehCmpData:
                self.__vehicles.append(vehCmpData)
                self.__applyChanges(addedIDXs=[len(self.__vehicles) - 1], addedCDs=[vehicleCompactDesr])
                return True
        return False

    @_ErrorNotification
    def addVehicles(self, vehCDs):
        newVehsCount = len(vehCDs)
        currVehsCount = len(self.__vehicles)
        if newVehsCount + currVehsCount <= MAX_VEHICLES_TO_COMPARE_COUNT:
            self.__vehicles.extend(map(self._createVehCompareData, vehCDs))
            self.__applyChanges(addedIDXs=range(currVehsCount, currVehsCount + newVehsCount), addedCDs=vehCDs)
        else:
            LOG_DEBUG("Couldn't add vehicles in the comparison basket, basket is full!")

    @_ErrorNotification
    @_indexCanBePerformed
    def revertVehicleByIdx(self, index):
        vehicle = self.__vehicles[index]
        vehicle.setVehicleStrCD(vehicle.getInvVehStrCD() if vehicle.isInInventory() else vehicle.getStockVehStrCD())
        vehicle.setEquipment(vehicle.getInvEquipment())
        vehicle.setBattleBooster(vehicle.getInvBattleBooster())
        vehicle.setHasCamouflage(vehicle.invHasCamouflage())
        vehicle.setPerks(vehicle.getInvPerks())
        vehicle.setSelectedShellIndex(_DEF_SHELL_INDEX)
        self.onParametersChange((index,))

    @_operationLocked
    @_ErrorNotification
    @_indexCanBePerformed
    def removeVehicleByIdx(self, index):
        vehCompareData = self.__vehicles[index]
        removedVehCD = vehCompareData.getVehicleCD()
        del self.__vehicles[index]
        self.__applyChanges(removedIDXs=[index], removedCDs=[removedVehCD])

    @_operationLocked
    @_ErrorNotification
    def removeAllVehicles(self):
        removedCDs = []
        for vehCompareData in self.__vehicles:
            removedCDs.append(vehCompareData.getVehicleCD())

        self.__vehicles = []
        self.__applyChanges(removedIDXs=range(len(removedCDs) - 1, -1, -1), removedCDs=removedCDs)

    @property
    def maxVehiclesToCompare(self):
        return MAX_VEHICLES_TO_COMPARE_COUNT

    def isFull(self):
        return self.__isFull

    def isReadyToAdd(self, vehicle):
        return not self.isLocked and self.isAvailable() and not self.isFull() and isValidVehicleForComparing(vehicle)

    @property
    def isLocked(self):
        return self.__isLocked

    @isLocked.setter
    def isLocked(self, value):
        self.__isLocked = value
        self.onSwitchChange()

    def isAvailable(self):
        return True

    def isEnabled(self):
        return self.__isEnabled

    @_ErrorNotification
    @_indexCanBePerformed
    def cloneVehicle(self, index):
        if self.__canBeAdded():
            target = self.__vehicles[index]
            self.__vehicles.append(target.clone())
            self.__applyChanges(addedIDXs=[len(self.__vehicles) - 1], addedCDs=[target.getVehicleCD()])

    def getVehiclesCDs(self):
        return [ vehCompareData.getVehicleCD() for vehCompareData in self.__vehicles ]

    def getVehiclesPropertiesIter(self, getter):
        return imap(getter, self.__vehicles)

    def getVehiclesCount(self):
        return len(self.__vehicles)

    @_indexCanBePerformed
    def getVehicleAt(self, index):
        return self.__vehicles[index]

    def writeCache(self):
        if self.__cache:
            self.__cache.write()

    def _createVehCompareData(self, intCD, initParameters=None):
        vehCmpData = None
        initParameters = initParameters or {}
        defStrCD = initParameters.get('strCD')
        fromCache = initParameters.get('isFromCache')
        defPerks = initParameters.get('perks')
        defEquipment = initParameters.get('equipment')
        defShellIndex = initParameters.get('shellIndex')
        defHasCamouflage = initParameters.get('hasCamouflage')
        defBattleBooster = initParameters.get('battleBooster')
        try:
            vehicle = self.itemsCache.items.getItemByCD(intCD)
            copyVehicle = Vehicle(_makeStrCD(vehicle), proxy=self.itemsCache.items)
            hasCamouflage = _isVehHasCamouflage(copyVehicle)
            if hasCamouflage:
                _removeVehicleCamouflages(copyVehicle)
            stockVehicle = self.itemsCache.items.getStockVehicle(intCD)
            vehCmpData = _VehCompareData(intCD, defStrCD or _makeStrCD(copyVehicle), _makeStrCD(stockVehicle), fromCache)
            self.__updateInventoryEquipment(vehCmpData, vehicle)
            self.__updateInventoryBattleBooster(vehCmpData, vehicle)
            self.__updateInventoryData(vehCmpData, vehicle)
            self.__updateInventoryPerks(vehCmpData, vehicle)
            if defPerks is not None:
                vehCmpData.setPerks(defPerks)
            else:
                vehCmpData.setPerks(vehCmpData.getInvPerks())
            if defEquipment is not None:
                vehCmpData.setEquipment(defEquipment)
            elif vehicle.isInInventory:
                vehCmpData.setEquipment(_getVehicleEquipment(vehicle))
            else:
                vehCmpData.setEquipment(vehCmpData.getNoEquipmentLayout())
            if defHasCamouflage is not None:
                vehCmpData.setHasCamouflage(defHasCamouflage)
            else:
                vehCmpData.setHasCamouflage(hasCamouflage)
            if defBattleBooster is not None:
                vehCmpData.setBattleBooster(defBattleBooster)
            elif vehicle.isInInventory and vehicle.battleBoosters.installed.getCapacity() > 0:
                vehCmpData.setBattleBooster(vehicle.battleBoosters.installed[0])
            else:
                vehCmpData.setBattleBooster(None)
            if defShellIndex:
                vehCmpData.setSelectedShellIndex(defShellIndex)
        except Exception:
            LOG_ERROR('Vehicle could not been added properly, intCD = {}'.format(intCD))
            LOG_CURRENT_EXCEPTION()

        return vehCmpData

    def _createCache(self):
        databaseID = BigWorld.player().databaseID if BigWorld.player() else None
        return _VehCmpCache(databaseID, self._applyVehiclesFromCache, self._getVehiclesIterator) if databaseID is not None else None

    def _applyVehiclesFromCache(self, data):
        if not data:
            return
        vehCDs = []
        for strCD, equipment, perks, shellIndex, hasCamouflage, battleBooster in data:
            intCD = VehicleDescr(strCD).type.compactDescr
            vehCmpData = self._createVehCompareData(intCD, initParameters={'strCD': strCD,
             'isFromCache': True,
             'perks': perks,
             'equipment': equipment,
             'shellIndex': shellIndex,
             'hasCamouflage': hasCamouflage,
             'battleBooster': battleBooster})
            if vehCmpData:
                self.__vehicles.append(vehCmpData)
                vehCDs.append(intCD)

        if vehCDs:
            self.__applyChanges(addedIDXs=range(0, len(vehCDs)), addedCDs=vehCDs)

    def _getVehiclesIterator(self):
        for vehCmpData in self.__vehicles:
            yield vehCmpData

    def __applyChanges(self, addedIDXs=None, addedCDs=None, removedIDXs=None, removedCDs=None):
        oldVal = self.__isFull
        self.__isFull = len(self.__vehicles) == MAX_VEHICLES_TO_COMPARE_COUNT
        self.onChange(_ChangedData(addedIDXs, addedCDs, removedIDXs, removedCDs, self.__isFull != oldVal))

    def __initHandlers(self):
        g_clientUpdateManager.addCallbacks({'inventory.15.compDescr': self.__onDetachmentUpdated})
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def __disposeHandlers(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        settings = self.lobbyContext.getServerSettings()
        if settings:
            settings.onServerSettingsChange -= self.__onServerSettingChanged

    def __onDetachmentUpdated(self, diff):
        detachmentIDs = diff.keys()
        for vehCompareData in self.__vehicles:
            vehicle = self.itemsCache.items.getItemByCD(vehCompareData.getVehicleCD())
            if vehicle.getLinkedDetachmentID() in detachmentIDs:
                self.__updateInventoryPerks(vehCompareData, vehicle)

    def __onCacheResync(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        else:
            changedIDXs = set()
            nationChangedIDxs = set()
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                vehDiff = diff[GUI_ITEM_TYPE.VEHICLE]
                diffKeys = diff.keys()
                isModulesOrDeviceChanged = set(diffKeys).intersection(set(GUI_ITEM_TYPE.VEHICLE_MODULES + (GUI_ITEM_TYPE.OPTIONALDEVICE,)))
                isEquipmentChanged = GUI_ITEM_TYPE.EQUIPMENT in diffKeys
                isBattleBoosterChanged = GUI_ITEM_TYPE.BATTLE_BOOSTER in diffKeys
                isCamouflageChanged = GUI_ITEM_TYPE.CUSTOMIZATION in diffKeys or GUI_ITEM_TYPE.OUTFIT in diffKeys
                isDetachmentChanged = GUI_ITEM_TYPE.DETACHMENT in diffKeys or GUI_ITEM_TYPE.INSTRUCTOR in diffKeys
                for changedVehCD in vehDiff:
                    for idx, vehCompareData in enumerate(self.__vehicles):
                        if changedVehCD == vehCompareData.getVehicleCD():
                            vehicle = self.itemsCache.items.getItemByCD(changedVehCD)
                            isCachedVehInInv = vehicle.isInInventory
                            if vehCompareData.isInInventory() != isCachedVehInInv:
                                self.__updateInventoryData(vehCompareData, vehicle)
                                self.__updateInventoryEquipment(vehCompareData, vehicle)
                                self.__updateInventoryBattleBooster(vehCompareData, vehicle)
                                self.__updateInventoryPerks(vehCompareData, vehicle)
                                changedIDXs.add(idx)
                            else:
                                if isModulesOrDeviceChanged:
                                    self.__updateInventoryData(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if isEquipmentChanged:
                                    self.__updateInventoryEquipment(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if isBattleBoosterChanged:
                                    self.__updateInventoryBattleBooster(vehCompareData, vehicle)
                                if isCamouflageChanged:
                                    self.__updateInventoryData(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if isDetachmentChanged:
                                    self.__updateInventoryPerks(vehCompareData, vehicle)
                            vehicleCompactDesr = getValidVehicleCDForNationChange(changedVehCD)
                            if vehicleCompactDesr != changedVehCD:
                                vehCmpData = self._createVehCompareData(vehicleCompactDesr, initParameters={'perks': vehCompareData.getPerks()})
                                self.__vehicles[idx] = vehCmpData
                                nationChangedIDxs.add(idx)

            if changedIDXs:
                self.onParametersChange(changedIDXs)
            if nationChangedIDxs:
                self.onNationChange(nationChangedIDxs)
            return

    @classmethod
    def __updateInventoryBattleBooster(cls, vehCompareData, vehicle):
        if vehicle.isInInventory and vehicle.battleBoosters.installed.getCapacity() > 0:
            vehCompareData.setInvBattleBooster(vehicle.battleBoosters.installed[0])
        else:
            vehCompareData.setInvBattleBooster(None)
        return

    @classmethod
    def __updateInventoryEquipment(cls, vehCompareData, vehicle):
        if vehicle.isInInventory:
            vehCompareData.setInvEquipment(_getVehicleEquipment(vehicle))
        else:
            vehCompareData.setInvEquipment(vehCompareData.getNoEquipmentLayout())

    @classmethod
    def __updateInventoryData(cls, vehCompareData, vehicle):
        isInInventory = vehicle.isInInventory
        vehCompareData.setIsInInventory(isInInventory)
        copyVehicle = Vehicle(_makeStrCD(vehicle), proxy=cls.itemsCache.items)
        hasCamouflage = _isVehHasCamouflage(copyVehicle)
        vehCompareData.setInvHasCamouflage(hasCamouflage)
        if hasCamouflage:
            _removeVehicleCamouflages(copyVehicle)
        vehCompareData.setInvVehStrCD(_makeStrCD(copyVehicle) if isInInventory else None)
        return

    @classmethod
    def __updateInventoryPerks(cls, vehCompareData, vehicle):
        if vehicle.isInInventory and vehicle.getLinkedDetachmentID() != NO_DETACHMENT_ID:
            perks = PerksData()
            detInvID = vehicle.getLinkedDetachmentID()
            detachment = cls.detachmentCache.getDetachment(detInvID)
            for perkID, perkPoints in detachment.build.iteritems():
                perks.points[perkID] += perkPoints

            for instructorInvID in detachment.getInstructorsIDs(skipNone=True, skipDuplicated=True):
                instructorPerks = cls.detachmentCache.getInstructor(instructorInvID).bonusPerks
                for perkID, perkPoints in instructorPerks.iteritems():
                    perks.instructorPoints[perkID] += perkPoints

            vehCompareData.setInventoryPerks(perks)
        else:
            vehCompareData.setInventoryPerks(PerksData())

    def __onServerSettingChanged(self, diff):
        if 'isVehiclesCompareEnabled' in diff:
            self.__isEnabled = bool(diff['isVehiclesCompareEnabled'])
            self.onSwitchChange()

    def __canBeAdded(self):
        if self.isFull():
            LOG_DEBUG("Couldn't add vehicle into the comparison basket, basket is full!")
            return False
        return True

    def __disposeCache(self):
        if self.__cache is not None:
            self.__cache.clear()
            self.__cache = None
        return
