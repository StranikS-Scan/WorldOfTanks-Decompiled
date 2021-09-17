# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/veh_comparison_basket.py
from collections import namedtuple
from itertools import imap
import BigWorld
import Event
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.shared.gui_items.Tankman import CrewTypes
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.local_cache import FileLocalCache
from items import ITEM_TYPE_NAMES, vehicles, EQUIPMENT_TYPES, ITEM_TYPES
from items.vehicles import VehicleDescr
from nation_change_helpers.client_nation_change_helper import getValidVehicleCDForNationChange
from post_progression_common import VehicleState
from skeletons.gui.game_control import IVehicleComparisonBasket, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
PARAMS_AFFECTED_TANKMEN_SKILLS = ('camouflage',
 'brotherhood',
 'repair',
 'commander_eagleEye',
 'driver_virtuoso',
 'driver_badRoadsKing',
 'radioman_inventor',
 'radioman_finder')
MAX_VEHICLES_TO_COMPARE_COUNT = 20
_NO_CREW_SKILLS = set()
_DEF_SHELL_INDEX = 0
_ChangedData = namedtuple('_ChangedData', ('addedIDXs',
 'addedCDs',
 'removedIDXs',
 'removedCDs',
 'isFullChanged'))
_COMPARE_INVALID_CRITERIA = ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE | ~REQ_CRITERIA.SECRET

def getVehicleCriteriaForComparing():
    return _COMPARE_INVALID_CRITERIA


def isValidVehicleForComparing(vehicle):
    return vehicle is not None and getVehicleCriteriaForComparing()(vehicle)


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


def _getCrewSkills(vehicle):
    availableSkills = set(PARAMS_AFFECTED_TANKMEN_SKILLS)
    currentSkills = set()
    for _, tankman in vehicle.crew:
        if tankman is not None:
            currentSkills = currentSkills.union(set([ skill.name for skill in tankman.skills ]))

    return currentSkills.intersection(availableSkills)


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


class _VehCmpCache(FileLocalCache):
    VERSION = 4

    def __init__(self, databaseID, dataSetter, dataGetter):
        super(_VehCmpCache, self).__init__('veh_cmp_cache', ('basket_state', databaseID), async=True)
        self.__dataSetter = dataSetter
        self.__dataGetter = dataGetter

    def _getCache(self):
        vehsData = []
        for vehCompareData in self.__dataGetter():
            dynSlotType = vehCompareData.getDynSlotType()
            vehsData.append((vehCompareData.getVehicleStrCD(),
             vehCompareData.getEquipment(),
             vehCompareData.getCrewData(),
             vehCompareData.getSelectedShellIndex(),
             vehCompareData.hasCamouflage(),
             vehCompareData.getBattleBooster(),
             vehCompareData.getPostProgressionState().toRawData(),
             dynSlotType.slotID if dynSlotType is not None else None))

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

    def __init__(self, vehicleIntCD, vehicleStrCD, vehStockStrCD, isFromCache=False, rentalIsOver=False):
        super(_VehCompareData, self).__init__()
        self.__isInInventory = False
        self.__isFromCache = isFromCache
        self.__invVehStrCD = None
        self.__rentalIsOver = rentalIsOver
        self.__crewLvl = CrewTypes.SKILL_100
        self.__inventoryCrewLvl = CrewTypes.SKILL_100
        self.__crewSkills = self.getStockCrewSkills()
        self.__inventoryCrewSkills = self.getStockCrewSkills()
        self.__intCD = vehicleIntCD
        self.__strCD = vehicleStrCD
        self.__stockVehStrCD = vehStockStrCD
        self.__equipment = self.getNoEquipmentLayout()
        self.__battleBooster = None
        self.__invEquipment = self.getNoEquipmentLayout()
        self.__selectedShellIndex = _DEF_SHELL_INDEX
        self.__invHasCamouflage = False
        self.__hasCamouflage = False
        self.__hasBattleBooster = False
        self.__dynSlotType = None
        self.__invDynSlotType = None
        self.__postProgressionState = None
        self.__invPostProgressionState = VehicleState()
        return

    def setIsInInventory(self, value):
        self.__isInInventory = value

    def setSelectedShellIndex(self, idx):
        self.__selectedShellIndex = idx

    def setInvVehStrCD(self, value):
        self.__invVehStrCD = value

    def setRentalIsOver(self, value):
        self.__rentalIsOver = value

    def setCrewData(self, crewLvl, skills):
        if crewLvl not in CrewTypes.ALL:
            raise SoftException('Unsupported crew level type: {}'.format(crewLvl))
        self.__crewLvl = crewLvl
        self.__crewSkills = skills

    def setInventoryCrewData(self, crewLvl, value):
        if crewLvl not in CrewTypes.ALL:
            raise SoftException('Unsupported crew level type: {}'.format(crewLvl))
        self.__inventoryCrewSkills = value
        self.__inventoryCrewLvl = crewLvl

    def setVehicleStrCD(self, strCD):
        self.__strCD = strCD

    def setBattleBooster(self, battleBooster):
        self.__battleBooster = battleBooster

    def setEquipment(self, equipment):
        self.__equipment = equipment

    def setInvEquipment(self, equipment):
        self.__invEquipment = equipment

    def setHasCamouflage(self, value):
        self.__hasCamouflage = value

    def setHasBattleBooster(self, value):
        self.__hasBattleBooster = value

    def setInvHasCamouflage(self, value):
        self.__invHasCamouflage = value

    def setDynSlotType(self, value):
        self.__dynSlotType = value

    def setInvDynSlotType(self, value):
        self.__invDynSlotType = value

    def setPostProgressionState(self, value):
        self.__postProgressionState = value

    def setInvPostProgressionState(self, value):
        self.__invPostProgressionState = value

    def getSelectedShellIndex(self):
        return self.__selectedShellIndex

    def getInventoryShellIndex(self):
        return _DEF_SHELL_INDEX

    def getInventoryCrewData(self):
        return (self.__inventoryCrewLvl, self.__inventoryCrewSkills.copy())

    def getInventoryCrewLvl(self):
        return self.__inventoryCrewLvl

    def getInvEquipment(self):
        return self.__invEquipment

    def getBattleBooster(self):
        return self.__battleBooster

    def getVehicleCD(self):
        return self.__intCD

    def getStockCrewLvl(self):
        return CrewTypes.SKILL_100

    def getStockCrewSkills(self):
        return _NO_CREW_SKILLS.copy()

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
        if self.__dynSlotType != self.__invDynSlotType:
            return cType
        if self.__postProgressionState != self.__invPostProgressionState:
            return cType
        if self.__strCD == self.__invVehStrCD:
            if self.__equipment == self.__invEquipment and self.__crewLvl == self.__inventoryCrewLvl and self.__crewSkills == self.__inventoryCrewSkills:
                cType = CONFIGURATION_TYPES.CURRENT
        elif self.__strCD == self.__stockVehStrCD and self.getEquipment() == self.getStockEquipment() and self.__crewLvl == self.getStockCrewLvl():
            if self.__crewSkills == self.getStockCrewSkills():
                cType = CONFIGURATION_TYPES.BASIC
        return cType

    def getVehicleStrCD(self):
        return self.__strCD

    def getInvVehStrCD(self):
        return self.__invVehStrCD

    def getStockVehStrCD(self):
        return self.__stockVehStrCD

    def getCrewData(self):
        return (self.__crewLvl, self.__crewSkills.copy())

    def getEquipment(self):
        equipmentIDs = self.__equipment[:]
        self.__addBuiltInEquipment(equipmentIDs)
        return equipmentIDs

    def getDynSlotType(self):
        return self.__dynSlotType

    def getInvDynSlotType(self):
        return self.__invDynSlotType

    def getPostProgressionState(self):
        return self.__postProgressionState

    def getInvPostProgressionState(self):
        return self.__invPostProgressionState

    def isFromCache(self):
        return self.__isFromCache

    def isRentalOver(self):
        return self.__rentalIsOver

    def hasCamouflage(self):
        return self.__hasCamouflage

    def hasBattleBooster(self):
        return self.__hasBattleBooster

    def invHasCamouflage(self):
        return self.__invHasCamouflage

    def isInInventory(self):
        return self.__isInInventory

    def clone(self):
        dataClone = _VehCompareData(self.getVehicleCD(), self.getVehicleStrCD(), self.getStockVehStrCD(), self.isRentalOver())
        dataClone.setIsInInventory(self.isInInventory())
        dataClone.setInvVehStrCD(self.getInvVehStrCD())
        dataClone.setCrewData(*self.getCrewData())
        dataClone.setInventoryCrewData(self.__inventoryCrewLvl, self.__inventoryCrewSkills)
        dataClone.setEquipment(self.getEquipment())
        dataClone.setInvEquipment(self.__invEquipment)
        dataClone.setHasCamouflage(self.__hasCamouflage)
        dataClone.setHasBattleBooster(self.__hasBattleBooster)
        dataClone.setInvHasCamouflage(self.__invHasCamouflage)
        dataClone.setSelectedShellIndex(self.getSelectedShellIndex())
        dataClone.setDynSlotType(self.__dynSlotType)
        dataClone.setInvDynSlotType(self.__invDynSlotType)
        dataClone.setPostProgressionState(self.__postProgressionState)
        dataClone.setInvPostProgressionState(self.__invPostProgressionState)
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
    def applyNewParameters(self, index, vehicle, crewLvl, crewSkills, selectedShellIndex=0):
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
        if crewLvl != CrewTypes.SKILL_100 and crewLvl != CrewTypes.CURRENT:
            crewSkills = _NO_CREW_SKILLS.copy()
        if vehCompareData.getCrewData() != (crewLvl, crewSkills):
            vehCompareData.setCrewData(crewLvl, crewSkills)
            isChanged = True
        if vehCompareData.getSelectedShellIndex() != selectedShellIndex:
            vehCompareData.setSelectedShellIndex(selectedShellIndex)
            isChanged = True
        if vehCompareData.getDynSlotType() != vehicle.optDevices.dynSlotType:
            vehCompareData.setDynSlotType(vehicle.optDevices.dynSlotType)
            isChanged = True
        if vehCompareData.getPostProgressionState() != vehicle.postProgression.getState(implicitCopy=False):
            vehCompareData.setPostProgressionState(vehicle.postProgression.getState())
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
        vehicle.setHasCamouflage(vehicle.invHasCamouflage())
        vehicle.setCrewData(*vehicle.getInventoryCrewData())
        vehicle.setSelectedShellIndex(_DEF_SHELL_INDEX)
        vehicle.setDynSlotType(vehicle.getInvDynSlotType())
        vehicle.setPostProgressionState(vehicle.getInvPostProgressionState())
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
        defCrewData = initParameters.get('crewData')
        defEquipment = initParameters.get('equipment')
        defShellIndex = initParameters.get('shellIndex')
        defHasCamouflage = initParameters.get('hasCamouflage')
        defBattleBooster = initParameters.get('battleBooster')
        defDynSlotType = initParameters.get('dynSlotType')
        defPostProgressionState = initParameters.get('postProgressionState')
        try:
            vehicle = self.itemsCache.items.getItemByCD(intCD)
            copyVehicle = Vehicle(_makeStrCD(vehicle), proxy=self.itemsCache.items)
            hasCamouflage = _isVehHasCamouflage(copyVehicle)
            if hasCamouflage:
                _removeVehicleCamouflages(copyVehicle)
            stockVehicle = self.itemsCache.items.getStockVehicle(intCD)
            vehCmpData = _VehCompareData(intCD, defStrCD or _makeStrCD(copyVehicle), _makeStrCD(stockVehicle), fromCache, vehicle.rentalIsOver)
            self.__updateInventoryEquipment(vehCmpData, vehicle)
            self.__updateInventoryData(vehCmpData, vehicle)
            self.__updateInventoryCrewData(vehCmpData, vehicle)
            self.__updatePostProgression(vehCmpData, vehicle, defDynSlotType, defPostProgressionState)
            if defCrewData is not None:
                vehCmpData.setCrewData(*defCrewData)
            elif vehicle.isInInventory:
                vehCmpData.setCrewData(CrewTypes.CURRENT, _getCrewSkills(vehicle))
            else:
                vehCmpData.setCrewData(CrewTypes.SKILL_100, _NO_CREW_SKILLS.copy())
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
        else:
            vehCDs = []
            for strCD, equipment, crew, shellIndex, hasCamouflage, booster, postProgression, dynSlotID in data:
                intCD = VehicleDescr(strCD).type.compactDescr
                vehCmpData = self._createVehCompareData(intCD, initParameters={'strCD': strCD,
                 'isFromCache': True,
                 'crewData': crew,
                 'equipment': equipment,
                 'shellIndex': shellIndex,
                 'hasCamouflage': hasCamouflage,
                 'battleBooster': booster,
                 'postProgressionState': VehicleState(postProgression),
                 'dynSlotType': vehicles.g_cache.supplySlots().slotDescrs[dynSlotID] if dynSlotID else None})
                if vehCmpData:
                    self.__vehicles.append(vehCmpData)
                    vehCDs.append(intCD)

            if vehCDs:
                self.__applyChanges(addedIDXs=range(0, len(vehCDs)), addedCDs=vehCDs)
            return

    def _getVehiclesIterator(self):
        for vehCmpData in self.__vehicles:
            yield vehCmpData

    def __applyChanges(self, addedIDXs=None, addedCDs=None, removedIDXs=None, removedCDs=None):
        oldVal = self.__isFull
        self.__isFull = len(self.__vehicles) == MAX_VEHICLES_TO_COMPARE_COUNT
        self.onChange(_ChangedData(addedIDXs, addedCDs, removedIDXs, removedCDs, self.__isFull != oldVal))

    def __initHandlers(self):
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def __disposeHandlers(self):
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        settings = self.lobbyContext.getServerSettings()
        if settings:
            settings.onServerSettingsChange -= self.__onServerSettingChanged

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
                for changedVehCD in vehDiff:
                    for idx, vehCompareData in enumerate(self.__vehicles):
                        if changedVehCD == vehCompareData.getVehicleCD():
                            vehicle = self.itemsCache.items.getItemByCD(changedVehCD)
                            isCachedVehInInv = vehicle.isInInventory
                            isRentalChanged = vehicle.rentalIsOver != vehCompareData.isRentalOver()
                            if vehCompareData.isInInventory() != isCachedVehInInv:
                                self.__updateInventoryData(vehCompareData, vehicle)
                                self.__updateInventoryEquipment(vehCompareData, vehicle)
                                self.__updateInventoryCrewData(vehCompareData, vehicle)
                                self.__updatePostProgression(vehCompareData, vehicle)
                                if not isCachedVehInInv:
                                    crewLevel, crewSkills = vehCompareData.getCrewData()
                                    if crewLevel == CrewTypes.CURRENT:
                                        vehCompareData.setCrewData(CrewTypes.SKILL_100, crewSkills)
                                changedIDXs.add(idx)
                            else:
                                if isModulesOrDeviceChanged:
                                    self.__updateInventoryData(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if isEquipmentChanged:
                                    self.__updateInventoryEquipment(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if GUI_ITEM_TYPE.TANKMAN in diffKeys:
                                    self.__updateInventoryCrewData(vehCompareData, vehicle)
                                if GUI_ITEM_TYPE.CUSTOMIZATION in diffKeys or GUI_ITEM_TYPE.OUTFIT in diffKeys:
                                    self.__updateInventoryData(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                                if GUI_ITEM_TYPE.VEH_POST_PROGRESSION in diffKeys or isRentalChanged:
                                    vehCompareData.setRentalIsOver(vehicle.rentalIsOver)
                                    self.__updatePostProgression(vehCompareData, vehicle)
                                    changedIDXs.add(idx)
                            vehicleCompactDesr = getValidVehicleCDForNationChange(changedVehCD)
                            if vehicleCompactDesr != changedVehCD:
                                vehCmpData = self._createVehCompareData(vehicleCompactDesr)
                                self.__vehicles[idx] = vehCmpData
                                nationChangedIDxs.add(idx)

            if changedIDXs:
                self.onParametersChange(changedIDXs)
            if nationChangedIDxs:
                self.onNationChange(nationChangedIDxs)
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
    def __updateInventoryCrewData(cls, vehCompareData, vehicle):
        if vehicle.isInInventory:
            vehCompareData.setInventoryCrewData(CrewTypes.CURRENT, _getCrewSkills(vehicle))
        else:
            vehCompareData.setInventoryCrewData(CrewTypes.SKILL_100, _NO_CREW_SKILLS.copy())

    @classmethod
    def __updatePostProgression(cls, vehCmpData, vehicle, dynSlotType=None, progressState=None):
        invState = vehicle.postProgression.getState() if vehicle.isPostProgressionActive else VehicleState()
        invDynSlotType = vehicle.optDevices.dynSlotType if vehicle.isRoleSlotActive else None
        vehCmpData.setInvPostProgressionState(invState)
        vehCmpData.setInvDynSlotType(invDynSlotType)
        progressState = progressState if progressState is not None else vehCmpData.getPostProgressionState()
        progressState = progressState if progressState is not None else invState
        dynSlotType = dynSlotType if dynSlotType is not None else vehCmpData.getDynSlotType()
        dynSlotType = dynSlotType if dynSlotType is not None else invDynSlotType
        postProgressionState = progressState if vehicle.isPostProgressionExists else VehicleState()
        vehCmpData.setDynSlotType(dynSlotType if vehicle.isRoleSlotExists(postProgressionState) else None)
        vehCmpData.setPostProgressionState(postProgressionState)
        return

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
