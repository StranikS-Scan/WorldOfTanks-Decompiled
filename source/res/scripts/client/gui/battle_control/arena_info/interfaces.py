# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/interfaces.py
import typing
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control.view_components import ViewComponentsController
if typing.TYPE_CHECKING:
    from EmptyEntity import EmptyEntity
    from items.vehicles import VehicleDescr
    from gui.shared.gui_items.Vehicle import Vehicle
    from vehicle_systems.appearance_cache import VehicleAppearanceCacheInfo
    from vehicle_systems.CompoundAppearance import CompoundAppearance
    from points_of_interest.components import PoiStateComponent

class IArenaController(IBattleController):
    __slots__ = ('__weakref__',)

    def getControllerID(self):
        pass

    def getCtrlScope(self):
        raise NotImplementedError('Routine "getCtrlScope" must be implemented')

    def startControl(self, battleCtx, arenaVisitor):
        pass

    def stopControl(self):
        pass


class IArenaLoadController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.LOAD

    def spaceLoadStarted(self):
        pass

    def spaceLoadCompleted(self):
        pass

    def updateSpaceLoadProgress(self, progress):
        pass

    def arenaLoadCompleted(self):
        pass


class IContactsController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS

    def invalidateUsersTags(self):
        pass

    def invalidateUserTags(self, user):
        pass


class IArenaVehiclesController(IArenaLoadController, IContactsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD | _SCOPE.CONTACTS

    def invalidateArenaInfo(self):
        pass

    def invalidateVehiclesInfo(self, arenaDP):
        pass

    def invalidateVehiclesStats(self, arenaDP):
        pass

    def updateVehiclesStats(self, updated, arenaDP):
        pass

    def addVehicleInfo(self, vo, arenaDP):
        pass

    def updateVehiclesInfo(self, updated, arenaDP):
        pass

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        pass

    def invalidatePlayerStatus(self, flags, vo, arenaDP):
        pass

    def invalidateFogOfWarHiddenVehiclesFlag(self, flag):
        pass

    def invalidateFogOfWarEnabledFlag(self, flag):
        pass

    def updateTriggeredChatCommands(self, chatCommands, arenaDP):
        pass


class ITeamsBasesController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.TEAMS_BASES

    def invalidateTeamBasePoints(self, baseTeam, baseID, points, timeLeft, invadersCnt, capturingStopped):
        pass

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        pass

    def removeTeamsBases(self):
        pass


class IArenaPeriodController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.PERIOD

    def setPeriodInfo(self, period, endTime, length, additionalInfo):
        pass

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        pass


class IPersonalInvitationsController(IArenaController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.INVITATIONS

    def invalidateInvitationsStatuses(self, vos, arenaDP):
        pass


class IVehiclesAndPersonalInvitationsController(IArenaVehiclesController, IPersonalInvitationsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.INVITATIONS | _SCOPE.CONTACTS


class IVehiclesAndPositionsController(IArenaVehiclesController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.POSITIONS

    def updatePositions(self, iterator):
        pass


class IBattleFieldController(IArenaVehiclesController):
    __slots__ = ()

    def setVehicleHealth(self, vehicleID, newHealth):
        pass

    def setVehicleData(self, data):
        pass

    def setVehicleVisible(self, vehicleID, health):
        pass

    def stopVehicleVisual(self, vehicleID):
        pass


class IProgressionController(IArenaLoadController):
    __slots__ = ()
    onVehicleUpgradeStarted = None
    onVehicleUpgradeFinished = None

    def getCurrentVehicle(self):
        raise NotImplementedError

    def getCurrentVehicleLevel(self):
        raise NotImplementedError

    def updateXP(self, xp, observedVehicleID):
        raise NotImplementedError

    def mayInstallModule(self, moduleItem):
        raise NotImplementedError

    def mayInstallModuleOnVehicle(self, moduleItem, vehicle):
        raise NotImplementedError

    def updateVehicleXP(self):
        pass

    def vehicleVisualChangingStarted(self, vehicleID):
        pass

    def vehicleVisualChangingFinished(self, vehicleID):
        pass

    def addRuntimeView(self, view):
        pass

    def removeRuntimeView(self, view):
        pass

    def vehicleUpgradeRequest(self, intCD, moduleItem):
        pass

    def vehicleUpgradeResponse(self, intCD, successfullyProcessed):
        pass

    def isModuleSelected(self, intCD):
        pass

    def getModule(self, intCD):
        raise NotImplementedError

    def getInstalledOnVehicleAnalogByIntCD(self, intCD):
        raise NotImplementedError

    def getWindowCtrl(self):
        raise NotImplementedError

    def updateVehicleReadinessTime(self, cooldownTime, reason):
        raise NotImplementedError

    def isVehicleReady(self):
        raise NotImplementedError

    def setAverageBattleLevel(self, level):
        raise NotImplementedError

    @property
    def maxLevel(self):
        raise NotImplementedError


class IContactsAndPersonalInvitationsController(IContactsController, IPersonalInvitationsController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.CONTACTS | _SCOPE.INVITATIONS


class IViewPointsController(IArenaLoadController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.LOAD | _SCOPE.VIEW_POINTS

    def updateViewPoints(self, viewPoints):
        pass

    def updateAttachedVehicle(self, vehicleID):
        pass


class IAnonymizerFakesController(IArenaVehiclesController):
    __slots__ = ()

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def addBattleFriend(self, avatarSessionID):
        raise NotImplementedError

    def removeBattleFriend(self, avatarSessionID):
        raise NotImplementedError

    def addBattleIgnored(self, avatarSessionID):
        raise NotImplementedError

    def removeBattleIgnored(self, avatarSessionID):
        raise NotImplementedError

    def mute(self, avatarSessionID, name):
        raise NotImplementedError

    def unmute(self, avatarSessionID):
        raise NotImplementedError

    def addTmpIgnored(self, avatarSessionID, name):
        raise NotImplementedError

    def removeTmpIgnored(self, avatarSessionID):
        raise NotImplementedError


class IRadarController(object):

    def activateRadar(self):
        raise NotImplementedError

    def updateRadarReadinessTime(self, radarReadinessTime):
        raise NotImplementedError

    def updateRadarReadiness(self, isReady):
        raise NotImplementedError

    def addRuntimeView(self, view):
        raise NotImplementedError

    def removeRuntimeView(self, view):
        raise NotImplementedError


class ISpawnController(object):

    def showSpawnPoints(self, points):
        raise NotImplementedError


class IVehicleCountController(IArenaVehiclesController, ViewComponentsController):

    def updateAttachedVehicle(self, vehicleID):
        raise NotImplementedError


class IPrebattleSetupsController(IArenaPeriodController, IArenaLoadController, ViewComponentsController):

    def getPrebattleSetupsVehicle(self):
        raise NotImplementedError

    def getPrebattleVehicleID(self):
        raise NotImplementedError

    def getCtrlScope(self):
        return _SCOPE.PERIOD | _SCOPE.LOAD

    def isArenaLoaded(self):
        raise NotImplementedError

    def isSelectionStarted(self):
        raise NotImplementedError

    def stopSelection(self):
        raise NotImplementedError

    def setPlayerVehicle(self, vehicleID, vehDescr):
        raise NotImplementedError

    def setCrew(self, vehicleID, crew):
        raise NotImplementedError

    def setDynSlotType(self, vehicleID, dynSlotTypeID):
        raise NotImplementedError

    def setEnhancements(self, vehicleID, enhancements):
        raise NotImplementedError

    def setPerks(self, vehicleID, perks):
        raise NotImplementedError

    def setPostProgression(self, vehicleID, postProgression):
        raise NotImplementedError

    def setDisabledSwitches(self, vehicleID, groupIDs):
        raise NotImplementedError

    def setRespawnReloadFactor(self, vehicleID, reloadFactor):
        raise NotImplementedError

    def setSetups(self, vehicleID, setups):
        raise NotImplementedError

    def setSetupsIndexes(self, vehicleID, setupsIndexes):
        raise NotImplementedError

    def setSiegeState(self, vehicleID, siegeState):
        raise NotImplementedError

    def setVehicleAttrs(self, vehicleID, attrs):
        raise NotImplementedError

    def switchLayout(self, groupID, layoutIdx):
        raise NotImplementedError


class IAppearanceCacheController(IArenaVehiclesController):

    def getAppearance(self, vId, vInfo, callback=None, strCD=None):
        raise NotImplementedError

    def reloadAppearance(self, vId, vInfo, callback=None, strCD=None, oldStrCD=None):
        raise NotImplementedError


class IPointsOfInterestController(IBattleController):
    onPoiEquipmentUsed = None
    onPoiCaptured = None

    @staticmethod
    def getPoiState(poiID):
        raise NotImplementedError

    @staticmethod
    def getPoiEntity(poiID):
        raise NotImplementedError

    def getVehicleCapturingPoiGO(self, poiName, entityGameObject, spaceID):
        raise NotImplementedError


class IComp7PrebattleSetupController(IArenaLoadController, IArenaPeriodController, ViewComponentsController):
    onVehiclesListUpdated = None
    onVehicleChanged = None
    onBattleStarted = None
    onSelectionConfirmed = None
    onTeammateSelectionStatuses = None

    def getCtrlScope(self):
        return _SCOPE.PERIOD | _SCOPE.LOAD

    def confirmVehicleSelection(self):
        raise NotImplementedError

    def isSelectionConfirmed(self):
        raise NotImplementedError

    def chooseVehicle(self, newCD):
        raise NotImplementedError

    def setAvailableVehicles(self, vehiclesList):
        raise NotImplementedError

    @staticmethod
    def getVehiclesList():
        raise NotImplementedError

    def updateVehicleInfo(self, vehiclesList):
        raise NotImplementedError

    @staticmethod
    def getCurrentVehicleInfo():
        raise NotImplementedError

    def updateSpawnPoints(self, spawnPointsList):
        raise NotImplementedError

    def updateConfirmationStatuses(self, newStatuses):
        raise NotImplementedError

    def getCurrentGUIVehicle(self):
        raise NotImplementedError

    def switchPrebattleSetup(self, groupID, layoutIdx):
        raise NotImplementedError

    def isVehicleStateIndicatorAllowed(self):
        raise NotImplementedError


class IComp7VOIPController(IArenaLoadController):
    __slots__ = ()

    @property
    def isVoipSupported(self):
        raise NotImplementedError

    @property
    def isVoipEnabled(self):
        raise NotImplementedError

    @property
    def isTeamChannelAvailable(self):
        raise NotImplementedError

    @property
    def isJoined(self):
        raise NotImplementedError

    @property
    def isTeamVoipEnabled(self):
        raise NotImplementedError

    def toggleChannelConnection(self):
        raise NotImplementedError
