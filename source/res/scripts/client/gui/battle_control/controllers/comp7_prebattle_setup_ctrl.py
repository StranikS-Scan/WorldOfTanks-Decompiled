# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/comp7_prebattle_setup_ctrl.py
import logging
import BigWorld
import CGF
import GenericComponents
import Math
import constants
from Event import Event, EventManager
from constants import ARENA_PERIOD, ARENA_GUI_TYPE
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info.interfaces import IComp7PrebattleSetupController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.gui_vehicle_builder import VehicleBuilder
from gui.veh_post_progression.sounds import playSound, Sounds
from helpers import dependency
from skeletons.dynamic_objects_cache import IBattleDynamicObjectsCache
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class _SceneController(object):
    __dynObjectsCache = dependency.descriptor(IBattleDynamicObjectsCache)

    def __init__(self):
        self.__spawnPoints = {}
        self.__config = self.__dynObjectsCache.getConfig(ARENA_GUI_TYPE.COMP7).getSpawnPointsConfig()
        self.__pendingSpawnPoints = {}

    def createSpawnPoint(self, vehicleID, positionNumber, status):
        if vehicleID in BigWorld.entities.keys():
            self.__createSpawnPointPrefab(BigWorld.entities[vehicleID], positionNumber, status)
        else:
            if not self.__pendingSpawnPoints:
                BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
            self.__pendingSpawnPoints[vehicleID] = {'positionNumber': positionNumber,
             'status': status}

    def updateSpawnPoint(self, vehicleID, newStatus):
        if vehicleID in self.__spawnPoints:
            areaComponent = self.__spawnPoints[vehicleID].findComponentByType(GenericComponents.TerrainSelectedAreaComponent)
            newColor = self.__getAreaColor(vehicleID, newStatus)
            areaComponent.setColor(newColor)
        elif vehicleID in self.__pendingSpawnPoints:
            self.__pendingSpawnPoints[vehicleID]['status'] = newStatus
        else:
            _logger.error('Spawn point for vehicle %d is lost and can not be updated', vehicleID)

    def clear(self):
        for go in self.__spawnPoints.values():
            CGF.removeGameObject(go)

        self.__spawnPoints.clear()
        self.__pendingSpawnPoints.clear()

    def __onVehicleEnterWorld(self, vehicle):
        if vehicle.id in self.__pendingSpawnPoints:
            spawnPointData = self.__pendingSpawnPoints.pop(vehicle.id)
            self.__createSpawnPointPrefab(vehicle, spawnPointData['positionNumber'], spawnPointData['status'])
            if not self.__pendingSpawnPoints:
                BigWorld.player().onVehicleEnteredWorld -= self.__onVehicleEnterWorld

    def __createSpawnPointPrefab(self, vehicle, positionNumber, status):
        visualPath = self.__config.getVisualPath(positionNumber)
        if not visualPath:
            return
        self.__spawnPoints[vehicle.id] = newGO = CGF.GameObject(vehicle.spaceID)
        newGO.createComponent(GenericComponents.TransformComponent, Math.Matrix(vehicle.matrix))
        newGO.createComponent(GenericComponents.TerrainSelectedAreaComponent, visualPath, self.__config.size, self.__config.overTerrainHeight, self.__getAreaColor(vehicle.id, status))
        newGO.activate()

    def __getAreaColor(self, vehicleID, status):
        isConfirmed = status == constants.VehicleSelectionPlayerStatus.CONFIRMED
        return self.__config.getColor(vehicleID == avatar_getter.getPlayerVehicleID(), isConfirmed)


class Comp7PrebattleSetupController(IComp7PrebattleSetupController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(Comp7PrebattleSetupController, self).__init__()
        self.__em = EventManager()
        self.__currentArenaPeriod = ARENA_PERIOD.IDLE
        self.__guiVehicle = None
        self.__started = False
        self.onVehiclesListUpdated = Event(self.__em)
        self.onVehicleChanged = Event(self.__em)
        self.onSelectionConfirmed = Event(self.__em)
        self.onTeammateSelectionStatuses = Event(self.__em)
        self.onBattleStarted = Event(self.__em)
        self.__sceneCtrl = _SceneController()
        return

    def startControl(self, battleCtx, arenaVisitor):
        self.__currentArenaPeriod = arenaVisitor.getArenaPeriod()
        self.__started = True

    def stopControl(self):
        self.__started = False
        self.__currentArenaPeriod = ARENA_PERIOD.IDLE
        self.__em.clear()
        self.__sceneCtrl.clear()

    def getControllerID(self):
        return BATTLE_CTRL_ID.COMP7_PREBATTLE_SETUP_CTRL

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self.__updatePeriod(period)

    def confirmVehicleSelection(self):
        avatar_getter.getInBattleVehicleSwitchComponent().confirmSelection()
        self.onSelectionConfirmed()

    def isSelectionConfirmed(self):
        return True if self.__currentArenaPeriod >= ARENA_PERIOD.BATTLE else avatar_getter.getInBattleVehicleSwitchComponent().isVehicleConfirmed

    def chooseVehicle(self, newCD):
        avatar_getter.getInBattleVehicleSwitchComponent().chooseVehicle(newCD)

    def setAvailableVehicles(self, vehiclesList):
        self.onVehiclesListUpdated(vehiclesList)

    @staticmethod
    def getVehiclesList():
        switchComponent = avatar_getter.getInBattleVehicleSwitchComponent()
        return switchComponent.vehicleSpawnList if switchComponent else []

    def updateVehicleInfo(self, vehicleInfo):
        if vehicleInfo is not None and self.__currentArenaPeriod < ARENA_PERIOD.BATTLE and self.__started:
            prevSetups = self.__guiVehicle.setupLayouts.groups if self.__guiVehicle else None
            prevCD = self.__guiVehicle.intCD if self.__guiVehicle else None
            self.__guiVehicle = self.__makeGUIVehicle(vehicleInfo)
            if prevSetups != self.__guiVehicle.setupLayouts.groups or prevCD != self.__guiVehicle.intCD:
                if prevCD == self.__guiVehicle.intCD:
                    self.__sessionProvider.shared.ammo.updateForNewSetup(self.__guiVehicle.descriptor.gun, self.__guiVehicle.shells.installed.getItems())
                    playSound(Sounds.GAMEPLAY_SETUP_SWITCH)
            self.onVehicleChanged(self.__guiVehicle)
        return

    def getCurrentVehicleInfo(self, extendWithDataFromList=False):
        switchComponent = avatar_getter.getInBattleVehicleSwitchComponent()
        if switchComponent:
            info = switchComponent.spawnInfoForVehicle
            if extendWithDataFromList:
                return self.__extendWithDataFromList(info)
            return info
        return {}

    def updateSpawnPoints(self, spawnPoints):
        if self.__currentArenaPeriod >= ARENA_PERIOD.BATTLE:
            return
        confirmationStatuses = avatar_getter.getArena().teamInfo.TeamInfoInBattleVehicleSwitch.statuses or {}
        for vehicleId, position in spawnPoints.iteritems():
            status = confirmationStatuses.get(vehicleId, constants.VehicleSelectionPlayerStatus.NOT_CONFIRMED)
            self.__sceneCtrl.createSpawnPoint(vehicleId, position, status)

    def updateConfirmationStatuses(self, newStatuses):
        if self.__currentArenaPeriod >= ARENA_PERIOD.BATTLE:
            return
        self.onTeammateSelectionStatuses(newStatuses)
        for vehID, status in newStatuses.iteritems():
            self.__sceneCtrl.updateSpawnPoint(vehID, status)

    def getCurrentGUIVehicle(self):
        if self.__guiVehicle is None:
            vehicleInfo = self.getCurrentVehicleInfo(extendWithDataFromList=True)
            if vehicleInfo is not None:
                self.__guiVehicle = self.__makeGUIVehicle(vehicleInfo)
        return self.__guiVehicle

    def switchPrebattleSetup(self, groupID, layoutIdx):
        vehicleIntCD = self.getCurrentGUIVehicle().intCD
        avatar_getter.getInBattleVehicleSwitchComponent().switchSetup(vehicleIntCD, groupID, layoutIdx)

    def isVehicleStateIndicatorAllowed(self):
        return self.__currentArenaPeriod == ARENA_PERIOD.BATTLE

    def getVehicleHealth(self, vehicle):
        if self.__currentArenaPeriod < ARENA_PERIOD.BATTLE:
            vehHealth = self.__sessionProvider.arenaVisitor.getArenaVehicles().get(vehicle.id, {}).get('maxHealth')
            if vehHealth is not None:
                return vehHealth
        return vehicle.health

    def __extendWithDataFromList(self, info):
        for vehicleInfo in self.getVehiclesList():
            if vehicleInfo['compDescr'] == info['compDescr']:
                newInfo = dict(info)
                newInfo.update(vehicleInfo)
                return newInfo

        return info

    def __updatePeriod(self, period):
        previousArenaPeriod = self.__currentArenaPeriod
        self.__currentArenaPeriod = period
        if period >= ARENA_PERIOD.BATTLE > previousArenaPeriod:
            self.onBattleStarted()
            self.__sceneCtrl.clear()

    @staticmethod
    def __makeGUIVehicle(vehicleInfo):
        builder = VehicleBuilder()
        strCD = vehicleInfo['compDescr']
        builder.setStrCD(strCD)
        builder.setShells(strCD, vehicleInfo['vehSetups'])
        builder.setCrew(vehicleInfo['crewCompactDescrs'])
        builder.setAmmunitionSetups(vehicleInfo['vehSetups'], vehicleInfo['vehSetupsIndexes'])
        builder.setRoleSlot(vehicleInfo['customRoleSlotTypeId'])
        builder.setPostProgressionState(vehicleInfo['vehPostProgression'], vehicleInfo['vehDisabledSetupSwitches'])
        return builder.getResult()
