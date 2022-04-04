# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/proxies/vehicles_mgr.py
import time
import typing
import logging
from abc import ABCMeta
from collections import defaultdict
import BigWorld
import Keys
from BattleReplayHelpers import replayPlayer, replayMethod
from Event import Event, EventManager
from RTSShared import COMMAND_NAME, RTSSupply
from constants import VEHICLE_MISC_STATUS
from skeletons.helpers.statistics import IStatisticsCollector
from vehicle_systems import model_assembler
from vehicle_systems.stricted_loading import makeCallbackWeak
from vehicle_systems.tankStructure import ModelsSetParams, VehiclePartsTuple
from wotdecorators import noexcept
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.commander.commands import MoveCommandProducer, CommandsGroupContainer
from gui.battle_control.controllers.commander.common import FocusPriority, addModel, delModel
from gui.battle_control.controllers.commander.interfaces import IProxyVehiclesManager, IProxiesContainer
from gui.battle_control.controllers.commander.proxies.vehicle import makeProxyVehicle, RTSGunSettings
from gui.battle_control.controllers.consumables.ammo_ctrl import AmmoController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VehicleConditions
from helpers.CallbackDelayer import CallbacksSetByID
from arena_components.advanced_chat_component import _DEFAULT_ACTIVE_COMMAND_TIME
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Dict, Optional, List
    import Math
    from gui.battle_control.controllers.commander.interfaces import IProxyVehicle, ICommandsGroup

class _ProxiesContainer(IProxiesContainer):
    __metaclass__ = ABCMeta

    def __init__(self):
        super(_ProxiesContainer, self).__init__()
        self._proxies = {}

    def __getitem__(self, eID):
        return self._proxies.__getitem__(eID)

    def get(self, eID, default=None):
        return self._proxies.get(eID, default)

    def keys(self, criteria=None):
        return list(self.iterkeys(criteria))

    def values(self, criteria=None):
        return list(self.itervalues(criteria))

    def items(self, criteria=None):
        return list(self.iteritems(criteria))

    def iterkeys(self, criteria=None):
        return (k for k, v in self._proxies.iteritems() if criteria is None or criteria(v))

    def itervalues(self, criteria=None):
        return (v for v in self._proxies.itervalues() if criteria is None or criteria(v))

    def iteritems(self, criteria=None):
        return ((k, v) for k, v in self._proxies.iteritems() if criteria is None or criteria(k, v))


@replayPlayer
class ProxyVehiclesManager(_ProxiesContainer, IProxyVehiclesManager, CallbacksSetByID):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    _ORDER_VECTOR_UPDATE_INTERVAL = 0.0
    _GHOST_TANK_SHADER_HULL_TURRET_PATH = 'shaders/custom/ghostTankAlphaHullTurret'
    _GHOST_TANK_SHADER_CHASSIS_GUN_PATH = 'shaders/custom/ghostTankAlphaChassisGun'
    _GHOST_TANK_ALPHA = 0.5

    def __init__(self):
        super(ProxyVehiclesManager, self).__init__()
        self.__eventManager = EventManager()
        self.onCommandEnqueued = Event(self.__eventManager)
        self.onCommandComplete = Event(self.__eventManager)
        self.onCommandDequeued = Event(self.__eventManager)
        self.onVehicleCreated = Event(self.__eventManager)
        self.onVehicleUpdated = Event(self.__eventManager)
        self.onVehicleGroupChanged = Event(self.__eventManager)
        self.onVehicleSpeedLinkChanged = Event(self.__eventManager)
        self.onOrderChanged = Event(self.__eventManager)
        self.onMannerChanged = Event(self.__eventManager)
        self.onSelectionChanged = Event(self.__eventManager)
        self.onSelectionFinished = Event(self.__eventManager)
        self.onVehicleSpeaking = Event(self.__eventManager)
        self.onVehicleReloading = Event(self.__eventManager)
        self.onVehicleAboutToReload = Event(self.__eventManager)
        self.onVehicleShellsUpdated = Event(self.__eventManager)
        self.onVehicleDeviceDamaged = Event(self.__eventManager)
        self.onVehicleDeviceRepaired = Event(self.__eventManager)
        self.onVehicleConditionUpdated = Event(self.__eventManager)
        self.onVehicleTargeted = Event(self.__eventManager)
        self.onVehicleFireLineBlocked = Event(self.__eventManager)
        self.onFocusVehicleChanged = Event(self.__eventManager)
        self.onVehiclesInDragBoxChanged = Event(self.__eventManager)
        self.onVehicleDisabledStateChanged = Event(self.__eventManager)
        self.onVehicleLostWhileAttacked = Event(self.__eventManager)
        self.onVehicleFoundWhileAttacked = Event(self.__eventManager)
        self.onVehicleSelectionChangeAttempt = Event(self.__eventManager)
        self.onMannerBlockStateChanged = Event(self.__eventManager)
        self.__commandProducer = MoveCommandProducer()
        self.__commandsGroupContainer = CommandsGroupContainer()
        self.__models = {}
        self.__isDragBoxActive = False
        self.__mannerBlockList = set()
        self.__isRetreatEnabled = True
        self.__vehicleConditions = defaultdict(lambda : {VehicleConditions.NO_CONDITION})
        self.__extDestroyTimersStatusInfo = defaultdict(dict)
        self.__isCommander = False

    def init(self):
        sharedCtrls = self.__sessionProvider.shared
        sharedCtrls.feedback.onVehicleReloading += self.__onVehicleReloading
        sharedCtrls.feedback.onVehicleFeedbackReceived += self.__onVehicleFeedbackReceived
        if sharedCtrls.vehicleState is not None:
            sharedCtrls.vehicleState.onVehicleControlling += self.__onVehicleControlledChanged
        arena = BigWorld.player().arena
        arena.onCommanderDataVehicle += self.__onCommanderDataVehicle
        arena.onNewVehicleListReceived += self.__initVehicles
        arena.onVehicleAdded += self.__onVehicleUpdated
        arena.onVehicleUpdated += self.__onVehicleUpdated
        arena.onVehicleKilled += self.__onVehicleUpdated
        arena.onVehicleRecovered += self.__onVehicleUpdated
        BigWorld.player().onVehicleEnterWorld += self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld += self.__onVehicleLeaveWorld
        self.__initVehicles()
        self.__isCommander = avatar_getter.isPlayerCommander()
        return

    def fini(self):
        self.__finiVehicles()
        self.__isDragBoxActive = False
        self.__commandProducer.reset()
        self.__commandsGroupContainer.reset()
        arena = avatar_getter.getArena()
        if arena:
            arena.onVehicleRecovered -= self.__onVehicleUpdated
            arena.onVehicleKilled -= self.__onVehicleUpdated
            arena.onVehicleUpdated -= self.__onVehicleUpdated
            arena.onVehicleAdded -= self.__onVehicleUpdated
            arena.onNewVehicleListReceived -= self.__initVehicles
            arena.onCommanderDataVehicle -= self.__onCommanderDataVehicle
        if self.__sessionProvider.shared.vehicleState is not None:
            self.__sessionProvider.shared.vehicleState.onVehicleControlling -= self.__onVehicleControlledChanged
        self.__sessionProvider.shared.feedback.onVehicleReloading -= self.__onVehicleReloading
        self.__sessionProvider.shared.feedback.onVehicleFeedbackReceived -= self.__onVehicleFeedbackReceived
        BigWorld.player().onVehicleEnterWorld -= self.__onVehicleEnterWorld
        BigWorld.player().onVehicleLeaveWorld -= self.__onVehicleLeaveWorld
        self.__eventManager.clear()
        CallbacksSetByID.clear(self)
        return

    @property
    def hasSelection(self):
        return any(self.itervalues(lambda v: v.isSelected))

    @property
    def focusedID(self):
        focused = self.__getFocusedVehicle()
        return 0 if focused is None else focused.id

    @property
    def isRetreatEnabled(self):
        return self.__isRetreatEnabled

    @isRetreatEnabled.setter
    def isRetreatEnabled(self, enabled):
        self.__isRetreatEnabled = enabled

    def hasEdge(self, vID):
        inFocus = self.focusedID == vID
        vProxy = self.get(vID)
        isInsideDragBox = vProxy.insideDragBox if vProxy else False
        isSelected = vProxy.isSelected if vProxy else False
        return inFocus or isInsideDragBox or isSelected

    def hasForceSimpleEdge(self, vID):
        inFocus = self.focusedID == vID
        vProxy = self.get(vID)
        isInsideDragBox = vProxy.insideDragBox if vProxy else False
        isSelected = vProxy.isSelected if vProxy else False
        return not isSelected and (inFocus or isInsideDragBox)

    def enableVisual(self):
        for vehicle in self.itervalues(lambda v: v.isAlive):
            vehicle.enableVisual()

    def disableVisual(self):
        for vehicle in self.itervalues(lambda v: v.isAlive):
            vehicle.disableVisual()

    def blockManner(self, manner):
        self.__mannerBlockList.add(manner)
        self.onMannerBlockStateChanged(manner, blocked=True)

    def unblockManner(self, manner):
        self.__mannerBlockList.remove(manner)
        self.onMannerBlockStateChanged(manner, blocked=False)

    def resetBlockedManners(self):
        self.__mannerBlockList.clear()

    def isMannerBlocked(self, command):
        return command in self.__mannerBlockList

    def enableVehicle(self, vID=None):
        for proxyVeh in self.itervalues(lambda v: v.isAlive and (vID is None or v.id == vID)):
            proxyVeh.enableVehicle()
            self.onVehicleUpdated(proxyVeh)
            self.onVehicleDisabledStateChanged(proxyVeh.id, False)

    def disableVehicle(self, vID=None):
        for proxyVeh in self.itervalues(lambda v: v.isAlive and (vID is None or v.id == vID)):
            proxyVeh.disableVehicle()
            self.onVehicleUpdated(proxyVeh)
            self.onVehicleDisabledStateChanged(proxyVeh.id, True)

        selectedVehiclesIDs = self.keys(lambda v: v.isSelected)
        self.__updateSelection(selectedVehiclesIDs)
        self.__sessionProvider.dynamic.rtsSound.selectionChanged(selectedVehiclesIDs, False)

    def handleOnCommandEnqueued(self, command):
        self.__commandsGroupContainer.handleOnCommandEnqueued(command)
        self.onCommandEnqueued(command)

    def handleOnCommandComplete(self, command, numCommandsInQueue):
        self.onCommandComplete(command, numCommandsInQueue)

    def handleOnCommandDequeued(self, command):
        self.onCommandDequeued(command)
        self.__commandsGroupContainer.handleOnCommandDequeued(command)

    def handleVehicleSpeedLinkChanged(self, vID, isSpeedLinked):
        self.onVehicleSpeedLinkChanged(vID, isSpeedLinked)

    def handleVehicleOrderChanged(self, *args, **kwargs):
        self.onOrderChanged(*args, **kwargs)

    def handleVehicleTargeted(self, vID, highestOrder):
        self.onVehicleTargeted(vID, highestOrder)

    def handleVehicleMannerChanged(self, *args, **kwargs):
        self.onMannerChanged(*args, **kwargs)

    def handleVehicleGroupChanged(self, *args, **kwargs):
        self.onVehicleGroupChanged(*args, **kwargs)

    def handleVehicleFoundWhileAttacked(self, enemyVehicleID, targetedMarks):
        self.onVehicleFoundWhileAttacked(enemyVehicleID, targetedMarks)

    def handleVehicleLostWhileAttacked(self, enemyVehicleID, targetedMarks):
        self.onVehicleLostWhileAttacked(enemyVehicleID, targetedMarks)

    def handleSelectionFinished(self):
        self.onSelectionFinished(self.keys(lambda v: v.isSelected))

    def handleVehicleDestroyed(self, vID):
        self.__onVehicleUpdated(vID)

    def handleVehicleAboutToReload(self, vehicleID, isNonEmptyClip):
        self.onVehicleAboutToReload(vehicleID, isNonEmptyClip)

    def handleVehicleFireLineBlocked(self, vehicleID):
        self.onVehicleFireLineBlocked(vehicleID)

    def handleVehicleSelectionChangeAttempt(self, vIDs):
        self.onVehicleSelectionChangeAttempt(vIDs)

    @noexcept
    def updateTick(self):
        for vehicle in self.itervalues():
            vehicle.updateTick()

        self.__commandProducer.update()

    @replayMethod
    def resetMoveCommand(self):
        self.__commandProducer.reset()

    @replayMethod
    def startOrientating(self):
        self.__commandProducer.startOrientating()

    @replayMethod
    def finishMovingOrOrienting(self, isAggressive=False, keepPosition=False):
        if not self.__commandProducer.isActive:
            return False
        else:
            positions, markers, controlPoint, append, vehicleIDs = self.__commandProducer.finishMovingOrOrienting()
            groupID = self.__commandsGroupContainer.getNextCommandsGroupID()
            for vehicleID, position, heading in positions:
                marker = markers.pop(vehicleID, None)
                if marker is not None:
                    marker.setVisible(False)
                wasEnqueued = self[vehicleID].enqueue(COMMAND_NAME.MOVE, marker=marker, position=position, heading=heading, controlPoint=controlPoint, isAggressive=isAggressive, isRetreat=self.__sessionProvider.dynamic.rtsCommander.isRetreatModeActive, executeNow=not append, companions=self.__getCompanions(vehicleID, vehicleIDs) or None, vehicleModel=self.__models.get(vehicleID, None), groupID=groupID)
                if marker and not wasEnqueued:
                    marker.fini()

            if not keepPosition:
                self.__commandProducer.reset()
            return True

    @replayMethod
    def activateMoving(self, vehicleIDs, position, append, controlPoint):
        vehicles = [ self._proxies[vID] for vID in vehicleIDs ]
        if not self.canQueueCommand(COMMAND_NAME.MOVE, isRequireAll=True, vehicles=vehicles):
            return
        self.__commandProducer.activateMoving(vehicles, position, append, controlPoint, self.__models)

    def setAmmo(self, vehicleID, compactDescr, quantity, quantityInClip):
        vehicle = self._proxies.get(vehicleID)
        if vehicle is not None and vehicle.isControllable:
            vehicle.setAmmo(compactDescr, quantity, quantityInClip)
            self.__updateVehicleShells(vehicle)
        return

    def setCurrentShellCD(self, vehicleID, compactDescr):
        vehicle = self._proxies.get(vehicleID)
        if vehicle is not None and vehicle.isControllable:
            vehicle.setCurrentShellCD(compactDescr)
            self.__updateVehicleShells(vehicle)
        return

    def canQueueCommand(self, commandTypeName, isRequireAll=True, vehicles=None):
        selectedVehicles = vehicles if vehicles is not None else self.values(lambda v: v.isSelected)
        isAppend = self.__commandProducer.isAppendModeActive()
        for vehicle in selectedVehicles:
            canQueue = vehicle.canQueueCommand(commandTypeName, executeNow=not isAppend)
            if isRequireAll:
                if not canQueue:
                    return False
            if canQueue:
                return True

        return isRequireAll

    @replayMethod
    def setDirection(self, direction):
        self.__commandProducer.setDirection(direction)

    @replayMethod
    def setFormationIndex(self, index):
        self.__commandProducer.setFormationIndex(index)

    @replayMethod
    def moveSelected(self, worldPos, controlPoint):
        vehicles = self.values(lambda v: v.isSelected)
        selectedMove = self.__commandProducer.moveSelected(worldPos, vehicles)
        if selectedMove:
            positions, append = selectedMove
        else:
            return False
        wasMoveEnqueued = False
        groupID = self._getNextCommandsGroupID()
        for vehicleID, position, heading in positions:
            wasMoveEnqueued = self[vehicleID].enqueue(COMMAND_NAME.MOVE, marker=None, position=position, heading=heading, controlPoint=controlPoint, isAggressive=self.__sessionProvider.dynamic.rtsCommander.isForceOrderModeActive, isRetreat=BigWorld.isKeyDown(Keys.KEY_F) and self.isRetreatEnabled, executeNow=not append, companions=self.__getCompanions(vehicleID, (v.id for v in vehicles)) or None, vehicleModel=self.__models[vehicleID], groupID=groupID) or wasMoveEnqueued

        return wasMoveEnqueued

    @replayMethod
    def startMoving(self):
        controlPoint = self.__sessionProvider.dynamic.rtsBWCtrl.controlPoint
        selectedVehicles = self.values(lambda v: v.isSelected)
        return True if not self.canQueueCommand(COMMAND_NAME.MOVE, isRequireAll=True, vehicles=selectedVehicles) else self.__commandProducer.startMoving(selectedVehicles, self.__models, controlPoint)

    @replayMethod
    def stopOrientating(self):
        self.__commandProducer.stopOrientating()

    def disableOrientating(self):
        self.__commandProducer.disableOrientating()

    def stopRebuildingPositions(self):
        self.__commandProducer.stopRebuildingPositions()

    @replayMethod
    def vehicleTargeting(self, isAggressive, targetID):
        if self.__commandProducer.isActive:
            return True
        else:
            appendAttack = self.__commandProducer.isAppendModeActive()
            groupID = self._getNextCommandsGroupID()
            if targetID is not None:
                vehicleIDs = self.keys(lambda v: v.isSelected)
                for vehicleID in vehicleIDs:
                    self[vehicleID].enqueue(COMMAND_NAME.ATTACK, executeNow=not appendAttack, target=self.get(targetID), force=isAggressive, companions=self.__getCompanions(vehicleID, vehicleIDs) or None, groupID=groupID)

            return False

    @replayMethod
    def onRTSEvent(self, event, vehicleID, position):
        vehicle = self.get(vehicleID)
        if vehicle is None:
            _logger.warning('onRTSEvent: vehicle with ID: %s not found', vehicleID)
            return
        else:
            vehicle.onRTSEvent(event, position)
            return

    @replayMethod
    def enqueue(self, vehicleIDs, commandID, executeNow=False, **kwargs):
        groupID = kwargs.pop('groupID', None) or self._getNextCommandsGroupID()
        for vehicleID in vehicleIDs:
            vehicle = self.get(vehicleID)
            if vehicle is None:
                _logger.warning('enqueue: vehicle with ID: %s not found, ignored', vehicleID)
                continue
            vehicle.enqueue(commandID, executeNow=executeNow, groupID=groupID, **kwargs)

        return

    @replayMethod
    def abortCommands(self, vehIDs=None):
        for vehicleID in vehIDs:
            vehicle = self._proxies.get(vehicleID)
            if vehicle:
                vehicle.abortCommands()
            _logger.warning('abortCommands: vehicle with ID: %s not found, ignored', vehicleID)

    @replayMethod
    def halt(self, vehicleIDs, manner=None):
        for vehicleID in vehicleIDs:
            vehicle = self.get(vehicleID)
            if vehicle is None:
                _logger.warning('halt: vehicle with ID: %s not found, ignored', vehicleID)
            vehicle.halt(manner=manner)

        return

    @replayMethod
    def changeManner(self, vehicleIDs, manner):
        for vehicleID in vehicleIDs:
            vehicle = self.get(vehicleID)
            if vehicle is None:
                _logger.warning('changeManner: vehicle with ID: %s not found, ignored', vehicleID)
            vehicle.changeManner(manner)

        return

    @replayMethod
    def createControlGroup(self, groupID):
        selectedIDs = self.keys(lambda v: v.isSelected)
        for vehicle in self.itervalues(lambda v: v.isControllable):
            if vehicle.id in selectedIDs:
                vehicle.updateCommanderGroup(groupID)
                continue
            if vehicle.groupID == groupID:
                vehicle.updateCommanderGroup(0)

    def selectControlGroup(self, groupID):
        selectedVehiclesIDs = self.keys(lambda v: v.isControllable and v.groupID == groupID)
        self.setSelection(selectedVehiclesIDs)
        self.onVehicleSelectionChangeAttempt(selectedVehiclesIDs)
        self.__sessionProvider.dynamic.rtsSound.selectionChanged(selectedVehiclesIDs, selectionViaPanel=True)

    def getControlGroup(self, groupID):
        return self.values(lambda v: v.isControllable and v.groupID == groupID)

    def getAliveNearCursor(self, criteria):
        focusedVeh = self.__getFocusedVehicle()
        return focusedVeh.id if focusedVeh is not None and focusedVeh.isAlive and focusedVeh.initialized and criteria(focusedVeh) else None

    def setDragBoxActivated(self, isActivated):
        self.__isDragBoxActive = isActivated

    def setInsideDragBox(self, vIDs):
        updated = False
        for vID in vIDs:
            vehicle = self._proxies.get(vID)
            if vehicle is not None and vehicle.isControllable:
                if not vehicle.insideDragBox:
                    vehicle.insideDragBox = True
                    updated = True

        if updated:
            self.onVehiclesInDragBoxChanged(vIDs, True)
            _updateHighlights()
        return

    def clearInsideDragBox(self, vIDs=None):
        if vIDs is None:
            vIDs = self.keys(lambda v: v.insideDragBox)
        updated = False
        for vID in vIDs:
            vehicle = self._proxies.get(vID)
            if vehicle is not None and vehicle.isAllyBot:
                if vehicle.insideDragBox:
                    vehicle.insideDragBox = False
                    updated = True

        if updated:
            self.onVehiclesInDragBoxChanged(vIDs, False)
            _updateHighlights()
        return

    def setSelection(self, vIDs):
        self.clearSelection()
        if vIDs is None:
            vIDs = self.keys(lambda v: v.isControllable)
        self.appendSelection(vIDs)
        return

    @replayMethod
    def appendSelection(self, vIDs):
        appended = False
        for vID in vIDs:
            vehicle = self._proxies.get(vID)
            if vehicle is not None and vehicle.isControllable:
                if not vehicle.isSelected:
                    vehicle.isSelected = True
                    appended = True

        if appended:
            selectedVehiclesIDs = self.keys(lambda v: v.isSelected)
            self.__updateSelection(selectedVehiclesIDs)
        return

    @replayMethod
    def toggleSelection(self, vIDs):
        changed = False
        for vID in vIDs:
            vehicle = self._proxies.get(vID)
            if vehicle is not None and vehicle.isControllable:
                vehicle.isSelected = not vehicle.isSelected
                changed = True

        if changed:
            selectedVehiclesIDs = self.keys(lambda v: v.isSelected)
            self.__updateSelection(selectedVehiclesIDs)
        return

    @replayMethod
    def clearSelection(self, vIDs=None):
        if vIDs is None:
            vIDs = self._proxies
        changed = False
        for vID in vIDs:
            vehicle = self._proxies.get(vID)
            if vehicle is not None:
                if vehicle.isSelected or vehicle.getFocusPriority() != FocusPriority.NONE:
                    vehicle.isSelected = False
                    vehicle.setFocusPriority(FocusPriority.NONE)
                    changed = True

        if changed:
            selectedVehiclesIDs = self.keys(lambda v: v.isSelected)
            self.__updateSelection(selectedVehiclesIDs)
        return

    @replayMethod(priority=FocusPriority)
    def setFocusVehicle(self, vID, isInFocus, priority):
        focused = self.__getFocusedVehicle()
        if focused is not None and focused.id == vID and focused.focusPriority == priority and isInFocus or self.__isDragBoxActive:
            return
        else:
            self.__clearFocus(priority)
            if isInFocus:
                self.__setFocus(vID, priority)
            _updateHighlights()
            self.onFocusVehicleChanged(vID, isInFocus)
            if avatar_getter.isCommanderCtrlMode():
                self.__sessionProvider.dynamic.rtsSound.focusedVehicleChanged(self.focusedID, isInFocus)
            return

    def getCommandsGroup(self, commandsGroupID):
        return self.__commandsGroupContainer.getCommandsGroup(commandsGroupID)

    def _getNextCommandsGroupID(self):
        return self.__commandsGroupContainer.getNextCommandsGroupID()

    def __onVehicleReloading(self, vehicleID, timeLeft, baseTime):
        vehicle = self._proxies.get(vehicleID)
        if vehicle is None or RTSSupply.isWatchTower(vehicle.typeDescriptor.type.tags):
            return
        else:
            if vehicle.isSupply:
                gunSettings = RTSGunSettings(vehicle.typeDescriptor.gun)
            else:
                gunSettings = vehicle.gunSettings
            if gunSettings is None:
                return
            baseTime = AmmoController.correctGunReloadBaseTime(gunSettings.interval, gunSettings.shellsInClip, timeLeft, baseTime, gunSettings.isAutoReload)
            self[vehicleID].reloadingState = (time.time(), timeLeft, baseTime)
            self.onVehicleReloading(vehicleID, self[vehicleID].reloadingState)
            return

    def setFocusVehicleToNone(self):
        self.__clearFocus(FocusPriority.MAX)
        _updateHighlights()
        self.onFocusVehicleChanged(0, False)
        self.__sessionProvider.dynamic.rtsSound.focusedVehicleChanged(0, False)

    def canShowVehicleStatus(self, vehicleID):
        if VehicleConditions.DEAD_CONDITION in self.__vehicleConditions[vehicleID]:
            return False
        else:
            vehProxyMgr = self.__sessionProvider.dynamic.rtsCommander.vehicles
            if vehProxyMgr is not None:
                vehProxy = vehProxyMgr.get(vehicleID)
                if vehProxy:
                    return vehProxy.isEnabled and not vehProxy.isSupply and vehProxy.isAllyBot
                return False
            return False

    def __updateVehicleShellStatus(self, vehicle):
        vID = vehicle.id
        if self.canShowVehicleStatus(vID):
            if vehicle.gunSettings.totalQuantity() <= 0:
                self.__removeVehicleCondition(vID, VehicleConditions.SPOTTED_CONDITION)
                self.__removeVehicleCondition(vID, VehicleConditions.SOS_CONDITION)
                self.__addVehicleCondition(vID, VehicleConditions.NO_SHOT_CONDITION)
            else:
                self.__removeVehicleCondition(vID, VehicleConditions.NO_SHOT_CONDITION)

    def controllableVehicleStateUpdated(self, state, args, vehicleID=0):
        if state not in (VEHICLE_VIEW_STATE.FIRE,
         VEHICLE_VIEW_STATE.DESTROY_TIMER,
         VEHICLE_VIEW_STATE.DEVICES,
         VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY):
            return
        self.__removeVehicleCondition(vehicleID, VehicleConditions.SPOTTED_CONDITION)
        self.__removeVehicleCondition(vehicleID, VehicleConditions.SOS_CONDITION)
        if state == VEHICLE_VIEW_STATE.FIRE:
            if args:
                self.__addVehicleCondition(vehicleID, VehicleConditions.ON_FIRE_CONDITION)
            else:
                self.__removeVehicleCondition(vehicleID, VehicleConditions.ON_FIRE_CONDITION)
        elif state == VEHICLE_VIEW_STATE.DESTROY_TIMER:
            if args.code == VEHICLE_MISC_STATUS.VEHICLE_DROWN_WARNING:
                if args.level > 0:
                    self.__addVehicleCondition(vehicleID, VehicleConditions.DROWNING_CONDITION)
                else:
                    self.__removeVehicleCondition(vehicleID, VehicleConditions.DROWNING_CONDITION)
                self.__extDestroyTimersStatusInfo[vehicleID][VehicleConditions.DROWNING_CONDITION] = args
            elif args.code == VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED:
                if args.level > 0:
                    self.__addVehicleCondition(vehicleID, VehicleConditions.OVERTURNED_CONDITION)
                else:
                    self.__removeVehicleCondition(vehicleID, VehicleConditions.OVERTURNED_CONDITION)
                self.__extDestroyTimersStatusInfo[vehicleID][VehicleConditions.OVERTURNED_CONDITION] = args
        elif state == VEHICLE_VIEW_STATE.DEVICES:
            name, deviceState, _ = args
            if deviceState == 'critical' and name == 'engine':
                self.__sessionProvider.dynamic.rtsSound.triggerDeviceDamagedSoundNotification(vehicleID, name)
            elif deviceState == 'destroyed' or deviceState == 'critical' and name == 'ammoBay':
                self.onVehicleDeviceDamaged(vehicleID, name)
                if name in ('engine', 'leftTrack0', 'rightTrack0', 'leftTrack1', 'rightTrack1'):
                    self.__addVehicleCondition(vehicleID, VehicleConditions.NO_MOVE_CONDITION)
                elif name == 'gun':
                    self.__addVehicleCondition(vehicleID, VehicleConditions.NO_SHOT_CONDITION)
            else:
                self.onVehicleDeviceRepaired(vehicleID, name)
                if name in ('engine', 'leftTrack0', 'rightTrack0', 'leftTrack1', 'rightTrack1'):
                    self.__removeVehicleCondition(vehicleID, VehicleConditions.NO_MOVE_CONDITION)
                elif name == 'gun':
                    self.__removeVehicleCondition(vehicleID, VehicleConditions.NO_SHOT_CONDITION)
        elif state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            if not self.__sameOrHigherPriorityConditionDisplayed(vehicleID, VehicleConditions.SOS_CONDITION):
                if args:
                    self.__addVehicleCondition(vehicleID, VehicleConditions.SPOTTED_CONDITION)
                else:
                    self.__removeVehicleCondition(vehicleID, VehicleConditions.SPOTTED_CONDITION)

    @staticmethod
    def __getCompanions(targetVehicleID, vehicleIDs):
        return list(set(vehicleIDs) ^ {targetVehicleID})

    def __getFocusedVehicle(self):
        focused = None
        for vehicle in (v for v in self._proxies.itervalues() if v.focusPriority != FocusPriority.NONE):
            if focused is None or focused.focusPriority.value < vehicle.focusPriority.value:
                focused = vehicle

        return focused

    def __clearFocus(self, priority):
        for vehicle in (v for v in self._proxies.itervalues() if v.focusPriority == priority):
            vehicle.setFocusPriority(FocusPriority.NONE)

    def __setFocus(self, vID, priority):
        vehicle = self._proxies.get(vID)
        if vehicle is not None and vehicle.isAlive:
            vehicle.setFocusPriority(priority)
        return

    def __updateSelection(self, selectedVehiclesIDs):
        _updateHighlights()
        self.statsCollector.apm.recordAction()
        self.onSelectionChanged(selectedVehiclesIDs)

    def __initVehicles(self, *_):
        self.__finiVehicles()
        for eID in BigWorld.player().arena.vehicles:
            self.__onVehicleUpdated(eID)

        self.__preloadTankModels()

    def __onCommanderDataVehicle(self, eID):
        self.__onVehicleUpdated(eID)

    def __onVehicleUpdated(self, eID, *_):
        vehicle = self._proxies.get(eID)
        isNewVehicle = vehicle is None
        if isNewVehicle:
            vehicle = makeProxyVehicle(eID, self)
            vehicle.init()
            self._proxies[eID] = vehicle
            self.__updateVehicleShells(vehicle)
        if vehicle.isControllable:
            vehicle.updateCommanderData()
        if isNewVehicle:
            self.onVehicleCreated(vehicle)
        self.onVehicleUpdated(vehicle)
        if not vehicle.isAlive:
            self.clearSelection([vehicle.id])
            selectedVehiclesIDs = self.keys(lambda v: v.isSelected)
            self.__sessionProvider.dynamic.rtsSound.selectionChanged(selectedVehiclesIDs, False)
        return

    def __onVehicleFeedbackReceived(self, eventID, vID, value):
        if eventID == FEEDBACK_EVENT_ID.ENTITY_IN_FOCUS:
            self.setFocusVehicle(vID, value.isInFocus, FocusPriority.MAX)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_HEALTH and self.canShowVehicleStatus(vID):
            health, attackerInfo = value[:2]
            if health <= 0:
                self.__addVehicleCondition(vID, VehicleConditions.DEAD_CONDITION)
            elif attackerInfo and not self.__sameOrHigherPriorityConditionDisplayed(vID, VehicleConditions.SOS_CONDITION):
                isSOS = health / float(attackerInfo.vehicleType.maxHealth) < VehicleConditions.SOS_HEALTH_THRESHOLD
                if isSOS:
                    self.__addVehicleCondition(vID, VehicleConditions.SOS_CONDITION)
                    self.delayCallback(vID, _DEFAULT_ACTIVE_COMMAND_TIME, self.__removeVehicleCondition, vID, VehicleConditions.SOS_CONDITION)
                else:
                    self.__removeVehicleCondition(vID, VehicleConditions.SOS_CONDITION)
        elif eventID == FEEDBACK_EVENT_ID.VEHICLE_DEAD and self.canShowVehicleStatus(vID):
            self.__addVehicleCondition(vID, VehicleConditions.DEAD_CONDITION)
            self.stopCallback(vID)

    def __sameOrHigherPriorityConditionDisplayed(self, vehicleID, newCondition):
        for condition in self.__vehicleConditions[vehicleID]:
            if VehicleConditions.CONDITIONS_PRIORITIES[condition] <= VehicleConditions.CONDITIONS_PRIORITIES[newCondition]:
                return True

        return False

    def __updateVehicleShells(self, vehicle):
        if vehicle.isControllable:
            gunSettings = vehicle.gunSettings
            self.onVehicleShellsUpdated(vehicle.id, gunSettings.clipSize, gunSettings.shellsInClip, gunSettings.isAutoReload, gunSettings.isDualGun)
            self.__updateVehicleShellStatus(vehicle)

    def __onVehicleEnterWorld(self, bwVehicle):
        proxyVehicle = self.get(bwVehicle.id)
        if proxyVehicle is not None:
            proxyVehicle.onEnterWorld(bwVehicle)
        return

    def __onVehicleLeaveWorld(self, bwVehicle):
        proxyVehicle = self.get(bwVehicle.id)
        if proxyVehicle is not None:
            proxyVehicle.onLeaveWorld(bwVehicle)
        return

    def __onVehicleControlledChanged(self, vehicle):
        if not vehicle:
            return
        vehicleId = vehicle.id
        isVehicleOverturned = False
        isDrowning = False
        isOnFire = False
        if vehicleId in self.__vehicleConditions:
            if vehicleId in self.__extDestroyTimersStatusInfo:
                vehicleStatus = self.__vehicleConditions[vehicleId]
                for status in vehicleStatus:
                    value = self.__extDestroyTimersStatusInfo[vehicleId].get(status)
                    if value:
                        self.__sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DESTROY_TIMER, value)
                    if status == VehicleConditions.ON_FIRE_CONDITION:
                        self.__sessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.FIRE, True)

                isVehicleOverturned = VehicleConditions.OVERTURNED_CONDITION in vehicleStatus
                isDrowning = VehicleConditions.DROWNING_CONDITION in vehicleStatus
                isOnFire = VehicleConditions.ON_FIRE_CONDITION in vehicleStatus
        self.__commandProducer.reset()
        BigWorld.player().overwriteVehicleMiscStatus(isVehicleOverturned=isVehicleOverturned, isDrowning=isDrowning, isOnFire=isOnFire)

    def __finiVehicles(self):
        for model in self.__models.itervalues():
            BigWorld.wgDelEdgeDetectCompoundModel(model)
            delModel(model)

        self.__models.clear()
        for vehicle in self._proxies.itervalues():
            vehicle.fini()

        self._proxies.clear()

    def __preloadTankModels(self):
        modelSetParam = ModelsSetParams('', 'undamaged', [])
        for vehicle in self._proxies.itervalues():
            if vehicle.isControllable:
                assembler = model_assembler.prepareCompoundAssembler(vehicle.typeDescriptor, modelSetParam, BigWorld.player().spaceID)
                BigWorld.loadResourceListBG((assembler,), makeCallbackWeak(self.__onResourcesLoaded, vehicle.id))

    def __onResourcesLoaded(self, vehicleID, resourceRefs):
        for _, model in resourceRefs.items():
            model.visible = False
            self.__models[vehicleID] = model
            addModel(model)
            self.__setupVehicleFashion(model)

    def __setupVehicleFashion(self, model):
        fashions = VehiclePartsTuple(self.__createCustomFashion(self._GHOST_TANK_SHADER_HULL_TURRET_PATH), self.__createCustomFashion(self._GHOST_TANK_SHADER_CHASSIS_GUN_PATH), self.__createCustomFashion(self._GHOST_TANK_SHADER_CHASSIS_GUN_PATH), self.__createCustomFashion(self._GHOST_TANK_SHADER_HULL_TURRET_PATH))
        model.setupFashions(fashions)
        BigWorld.wgAddEdgeDetectCompoundModel(model, 3, 0, True)

    def __createCustomFashion(self, effectPath=''):
        fashion = BigWorld.WGAlphaFadeCompoundFashion(effectPath)
        fashion.minAlpha = self._GHOST_TANK_ALPHA
        fashion.isFixedAlpha = True
        return fashion

    def __addVehicleCondition(self, vehicleID, condition):
        if condition in VehicleConditions.ALL_CONDITIONS:
            if condition not in self.__vehicleConditions[vehicleID]:
                self.__vehicleConditions[vehicleID].add(condition)
                if len(self.__vehicleConditions[vehicleID]) > 1 and VehicleConditions.NO_CONDITION in self.__vehicleConditions[vehicleID]:
                    self.__vehicleConditions[vehicleID].remove(VehicleConditions.NO_CONDITION)
                self.onVehicleConditionUpdated(vehicleID, self.__vehicleConditions)

    def __removeVehicleCondition(self, vehicleID, condition):
        if condition in self.__vehicleConditions[vehicleID]:
            self.__vehicleConditions[vehicleID].remove(condition)
            if not self.__vehicleConditions[vehicleID]:
                self.__vehicleConditions[vehicleID].add(VehicleConditions.NO_CONDITION)
            self.onVehicleConditionUpdated(vehicleID, self.__vehicleConditions)


def _updateHighlights():
    player = BigWorld.player()
    if player.userSeesWorld() and player.isCommander():
        player.updateAllHighlights()
