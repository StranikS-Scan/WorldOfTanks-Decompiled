# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/proxies/vehicle.py
import logging
import typing
import math
import BigWorld
import Math
import TriggersManager
from constants import ARENA_PERIOD
from RTSShared import DEFAULT_GROUP_ID, OrderData, RTSManner, RTSOrder, RTSEvent, COMMAND_NAME, RTSCommandQueuePosition
from gui.battle_control.arena_info import arena_vos
from gui.battle_control.controllers.commander.commands import CommandsQueue
from gui.battle_control.controllers.commander.common import FocusPriority
from gui.battle_control.controllers.commander.interfaces import IProxyVehicle
from gui.battle_control.controllers.commander import markers
from gui.battle_control.controllers.commander.commands.bw_path import BWPath
from gui.shared.gui_items.Vehicle import getVehicleClassTag
from helpers import dependency, weakProxy
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.helpers.statistics import IStatisticsCollector
from gui.battle_control import avatar_getter
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional, Dict, Any
    from gui.battle_control.controllers.commander.proxies.vehicles_mgr import ProxyVehiclesManager
    from Vehicle import Vehicle
    from gui.battle_control.controllers.commander.interfaces import IMarker

class AimAtVehicleTriggerListener(TriggersManager.ITriggerListener):

    def __init__(self, vehicle):
        self.__vehicle = vehicle
        self.__isActivated = False

    def onTriggerActivated(self, args):
        if self.__vehicle.isPlayerVehicle and args['type'] == TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE:
            self.__vehicle.onAimAtVehicle(args['vehicleId'])
            self.__isActivated = True

    def onTriggerDeactivated(self, args):
        if self.__isActivated and args['type'] == TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE:
            self.__vehicle.onAimAtVehicle(None)
            self.__isActivated = False
        return


class RTSGunSettings(object):

    def __init__(self, gun):
        self.__clipSize = gun.clip[0]
        self.__interval = gun.clip[1]
        self.__isAutoReload = 'autoreload' in gun.tags
        self.__isDualGun = 'dualGun' in gun.tags
        self.__ammo = {}
        self.__currentShellCD = None
        self.__turretYawLimits = gun.turretYawLimits
        return

    @property
    def clipSize(self):
        return self.__clipSize

    @property
    def interval(self):
        return self.__interval

    @property
    def isAutoReload(self):
        return self.__isAutoReload

    @property
    def isDualGun(self):
        return self.__isDualGun

    @property
    def turretYawLimits(self):
        return self.__turretYawLimits

    @property
    def shellsInClip(self):
        return 0 if self.__currentShellCD not in self.__ammo else self.__ammo[self.__currentShellCD][1]

    def setCurrentShellCD(self, cd):
        self.__currentShellCD = cd

    def setAmmo(self, cd, quantity, quantityInClip):
        self.__ammo[cd] = (quantity, quantityInClip)

    def totalQuantity(self):
        total = 0
        for quantity, _ in self.__ammo.itervalues():
            total += quantity

        return total


def isControllableBot(vID):
    arena = BigWorld.player().arena
    arenaVehicle = arena.vehicles.get(vID, {})
    commanderData = arena.commanderData.get(vID)
    hasOrderData = commanderData is not None and commanderData.orderData
    hasNoRelatedAccount = arenaVehicle.get('accountDBID') == 0
    isAlly = arenaVehicle.get('team') == BigWorld.player().team
    return hasNoRelatedAccount and hasOrderData and isAlly


class _ProxyVehicle(IProxyVehicle):
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self, eID, container):
        self.__id = eID
        self.__focusPriority = FocusPriority.NONE
        self.__reloadingState = (0.0, 0.0, 0.0)
        self._container = weakProxy(container)
        self._gunSettings = None
        self._bwVehicle = BigWorld.entity(eID)
        self._lastKnownMatrix = Math.Matrix(self._bwVehicle.matrix) if self._bwVehicle else None
        self._lastKnownPositionMarker = None
        self._targetedMarks = {}
        self._activeTargetMask = None
        return

    @property
    def id(self):
        return self.__id

    @property
    def isAlive(self):
        return bool(self.__getArenaVehicle().get('isAlive', 0))

    @property
    def isVisible(self):
        return self._bwVehicle is not None and self._bwVehicle.isStarted

    @property
    def isAlly(self):
        return self.__getArenaVehicle().get('team') == BigWorld.player().team

    @property
    def isAllyBot(self):
        return self.isBot and self.isAlly

    @property
    def isBot(self):
        return self.__getArenaVehicle().get('accountDBID') == 0 and self.__getOrderData() is not None

    @property
    def isCommander(self):
        return arena_vos.isCommander(self.typeDescriptor.type.tags)

    @property
    def isControllable(self):
        return False

    @property
    def isEnabled(self):
        return True

    @property
    def isEnemy(self):
        return not self.isAlly

    @property
    def isEnemyBot(self):
        return self.isBot and not self.isAlly

    @property
    def isObserver(self):
        return arena_vos.isObserver(self.typeDescriptor.type.tags)

    @property
    def isPlayer(self):
        return not any((self.isCommander,
         self.isObserver,
         self.isSupply,
         self.isBot))

    @property
    def isSupply(self):
        return arena_vos.isSupply(self.typeDescriptor.type.tags)

    @property
    def insideDragBox(self):
        return False

    @property
    def isSelected(self):
        return False

    @isSelected.setter
    def isSelected(self, _):
        pass

    @property
    def focusPriority(self):
        return self.__focusPriority

    @property
    def initialized(self):
        return self._bwVehicle is not None

    @property
    def rawGroupID(self):
        commanderData = self.__getCommanderData()
        return commanderData.groupID if commanderData is not None else DEFAULT_GROUP_ID

    @property
    def groupID(self):
        groupID = self.rawGroupID
        if groupID == DEFAULT_GROUP_ID:
            groupID = _getRosterIndex(self.id) + 1
        return groupID

    @property
    def typeDescriptor(self):
        return self.__getArenaVehicle().get('vehicleType')

    @property
    def vehicleClassTag(self):
        return getVehicleClassTag(self.typeDescriptor.type.tags)

    @property
    def appearance(self):
        return self._bwVehicle.appearance if self._bwVehicle is not None else None

    @property
    def maxHealth(self):
        return self.__getArenaVehicle().get('maxHealth')

    @property
    def matrix(self):
        return self._bwVehicle.matrix if self._bwVehicle is not None and self._bwVehicle.isStarted else self._lastKnownMatrix

    @property
    def yaw(self):
        return self._bwVehicle.yaw if self._bwVehicle is not None and self._bwVehicle.isStarted else 0

    @property
    def pitch(self):
        return self._bwVehicle.pitch if self._bwVehicle is not None and self._bwVehicle.isStarted else 0

    @property
    def position(self):
        return self._bwVehicle.position if self._bwVehicle is not None and self._bwVehicle.isStarted else self.lastKnownPosition

    @property
    def isPlayerVehicle(self):
        return self._bwVehicle.isPlayerVehicle if self._bwVehicle is not None and self._bwVehicle.isStarted else False

    @property
    def lastKnownPosition(self):
        return self._lastKnownMatrix.translation

    @property
    def targetPosition(self):
        return None

    @property
    def lastPosition(self):
        return None

    @property
    def aimParams(self):
        return self._bwVehicle.getAimParams() if self._bwVehicle is not None and self._bwVehicle.isStarted else (0.0, 0.0)

    @property
    def activeGunIndex(self):
        return self._bwVehicle.activeGunIndex if self._bwVehicle is not None and self._bwVehicle.isStarted else 0

    @property
    def serverGunAngles(self):
        return self._bwVehicle.getServerGunAngles() if self._bwVehicle is not None and self._bwVehicle.isStarted else (0.0, 0.0)

    def init(self):
        pass

    def fini(self):
        pass

    def enableVisual(self):
        pass

    def disableVisual(self):
        pass

    def enableVehicle(self):
        pass

    def disableVehicle(self):
        pass

    def updateCommanderData(self):
        pass

    def updateCommanderGroup(self, groupID):
        pass

    def abortCommands(self):
        pass

    def halt(self, manner=None, isForce=False):
        pass

    def updateTick(self):
        pass

    def canQueueCommand(self, commandTypeName, executeNow=False):
        return False

    def enqueue(self, commandID, executeNow=False, **kwargs):
        return False

    def getCommandsGroup(self, groupID):
        return None

    def onRTSEvent(self, event, position):
        pass

    def onCommandUpdated(self):
        pass

    def onCommandComplete(self, command):
        pass

    def onEnterWorld(self, bwVehicle):
        self._bwVehicle = bwVehicle
        self._updateLastKnownPositionMarker()

    def onLeaveWorld(self, bwVehicle):
        self._lastKnownMatrix = Math.Matrix(bwVehicle.matrix)
        self._bwVehicle = None
        self._updateLastKnownPositionMarker()
        return

    def markAsTarget(self, instigator, order):
        self._targetedMarks[instigator] = order
        self._activeTargetMask = (instigator, order)
        self._container.handleVehicleTargeted(self.id, self.getActiveTargetMark())
        self._updateLastKnownPositionMarker()

    def unmarkAsTarget(self, instigator):
        if instigator in self._targetedMarks:
            del self._targetedMarks[instigator]
            activeTargetInstigator = self._activeTargetMask[0]
            if activeTargetInstigator in (instigator, None):
                self._activeTargetMask = (None, self.getHighestTargetMark())
            self._container.handleVehicleTargeted(self.id, self.getActiveTargetMark())
            self._updateLastKnownPositionMarker()
        return

    def handleOnCommandEnqueued(self, command):
        pass

    def handleOnCommandDequeued(self, command):
        pass

    @property
    def reloadingState(self):
        return self.__reloadingState

    @reloadingState.setter
    def reloadingState(self, value):
        self.__reloadingState = value

    @property
    def gunSettings(self):
        return self._gunSettings

    @property
    def lastCommandInQueue(self):
        return None

    @property
    def activeCommand(self):
        return None

    @property
    def manner(self):
        return None

    @property
    def order(self):
        return None

    @property
    def orderData(self):
        return self.__getOrderData()

    def setAmmo(self, cd, quantity, quantityInClip):
        self._gunSettings.setAmmo(cd, quantity, quantityInClip)

    def setCurrentShellCD(self, cd):
        self._gunSettings.setCurrentShellCD(cd)

    def changeManner(self, manner):
        self.statsCollector.apm.recordAction()
        self.updateRTSOrder(manner=manner)

    def updateRTSOrder(self, order=None, manner=None, position=None, target=None, heading=None, baseID=None, baseTeam=None, **extra):
        pass

    def queryRTSData(self, queryType, context, callback):
        return None

    def setFocusPriority(self, value):
        self.__focusPriority = value

    def getFocusPriority(self):
        return self.__focusPriority

    def _updateLastKnownPositionMarker(self):
        targetOrderMark = self.getActiveTargetMark()
        if not self.isVisible and targetOrderMark:
            if self._lastKnownPositionMarker is None:
                yaw = self._lastKnownMatrix.yaw
                heading = Math.Vector3(math.sin(yaw), 0, math.cos(yaw))
                self._lastKnownPositionMarker = markers.TerrainOrderMarker(vID=self.id, orderType=targetOrderMark, position=self._lastKnownMatrix.translation, heading=heading, vehicleModel=None, queuePos=RTSCommandQueuePosition.SINGLE)
                self._container.handleVehicleLostWhileAttacked(self.id, self._targetedMarks)
            else:
                self._lastKnownPositionMarker.orderType = targetOrderMark
        elif self._lastKnownPositionMarker is not None:
            self._lastKnownPositionMarker.fini()
            self._lastKnownPositionMarker = None
        return

    def getHighestTargetMark(self):
        return max(self._targetedMarks.values(), key=lambda order: order.value) if self._targetedMarks else None

    def getActiveTargetMark(self):
        return self._activeTargetMask[1] if self._activeTargetMask is not None else self._activeTargetMask

    def __getArenaVehicle(self):
        return BigWorld.player().arena.vehicles.get(self.__id, {})

    def __getOrderData(self):
        commanderData = self.__getCommanderData()
        return None if commanderData is None else commanderData.orderData

    def __getCommanderData(self):
        return BigWorld.player().arena.commanderData.get(self.__id)


class _ControllableProxyVehicle(_ProxyVehicle):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vID, container):
        super(_ControllableProxyVehicle, self).__init__(vID, container)
        self.__commandsQueue = CommandsQueue(self)
        self._insideDragBox = False
        self.__isSelected = False
        self.__isSpeedLinked = False
        self.__isEnabled = True
        self.__isVisualEnabled = True
        self._gunSettings = RTSGunSettings(self.typeDescriptor.gun)
        self.__directionMarker = None
        self.__overwatchMarker = None
        self.__isOverwatchSectorEnabled = True
        self.__path = BWPath(self.id)
        self.__operationCircle = None
        self.__isFirstGroupIdUpdate = True
        self.__aimAtVehicleTriggerListener = None
        return

    @property
    def isControllable(self):
        return self.isAlive and not self.isSupply and self.isEnabled

    @property
    def isEnabled(self):
        return self.__isEnabled

    @property
    def isSelected(self):
        return self.__isSelected

    @isSelected.setter
    def isSelected(self, value):
        self.__isSelected = value

    @property
    def insideDragBox(self):
        return self._insideDragBox

    @insideDragBox.setter
    def insideDragBox(self, value):
        self._insideDragBox = value

    @property
    def targetPosition(self):
        position = self.__commandsQueue.targetPosition
        if position is None:
            orderData = self._getOrderData()
            if orderData is not None:
                return orderData.position
        return

    @property
    def lastPosition(self):
        return self.__commandsQueue.lastPosition

    @property
    def currentPath(self):
        return BigWorld.player().arena.commanderData.get(self.id).currentPath

    @property
    def isSpeedLinked(self):
        return self.__isSpeedLinked

    @property
    def path(self):
        return self.__path

    @property
    def isDeployed(self):
        return self.position.y > -499.0

    @property
    def manner(self):
        orderData = self._getOrderData()
        return orderData.manner if orderData is not None else None

    @property
    def order(self):
        orderData = self._getOrderData()
        return orderData.order if orderData is not None else None

    def init(self):
        self.updateCommanderGroup(_getRosterIndex(self.id) + 1)
        self.__directionMarker = markers.ProxyDirectionMarker(self)
        self.__operationCircle = markers.OperationCircle(self)
        if markers.OverwatchSectorMarker.isSuitedForVehicle(self):
            self.__overwatchMarker = markers.OverwatchSectorMarker(self.position, self.yaw)
        self.__aimAtVehicleTriggerListener = AimAtVehicleTriggerListener(self)
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.addListener(self.__aimAtVehicleTriggerListener)
        return

    def fini(self):
        self._destroyMarkers()
        self.__commandsQueue.clear()
        if TriggersManager.g_manager is not None:
            TriggersManager.g_manager.delListener(self.__aimAtVehicleTriggerListener)
        self.__aimAtVehicleTriggerListener = None
        return

    def enableVisual(self):
        self.__isVisualEnabled = True
        self._updateVehicleMarkers()

    def disableVisual(self):
        self.__isVisualEnabled = False
        self._updateVehicleMarkers()
        self.__path.removePath()

    def enableVehicle(self):
        self.__isEnabled = True
        self._updateVehicleMarkers()

    def disableVehicle(self):
        self.__isEnabled = False
        self._updateVehicleMarkers()
        if BigWorld.player().arena.period == ARENA_PERIOD.BATTLE and self.isDeployed:
            self.halt(manner=RTSManner.HOLD, isForce=True)
        self.isSelected = False
        vehicleChange = self.__sessionProvider.dynamic.vehicleChange
        if vehicleChange.currentVehicleID == self.id:
            vehicleChange.stopVehicleControl()

    def abortCommands(self):
        self.__commandsQueue.clear()

    def halt(self, manner=None, isForce=False):
        if (not self.isEnabled or self._container.isMannerBlocked(RTSManner.DEFENSIVE)) and not isForce:
            return
        hadCommandsInQueue = True if self.__commandsQueue.getNumCommandsInQueue > 0 else False
        self.__commandsQueue.clear()
        heading = Math.Vector3()
        heading.setPitchYaw(0.0, self.yaw)
        if not isForce:
            self.statsCollector.apm.recordAction()
        self.updateRTSOrder(order=RTSOrder.STOP, manner=manner or self.manner, position=self.position, heading=heading, halt=True, isForce=isForce, hadCommandsInQueue=hadCommandsInQueue)

    def updateCommanderData(self):
        commanderData = BigWorld.player().arena.commanderData.get(self.id)
        if self.__isSpeedLinked != commanderData.isSpeedLinked:
            self.__isSpeedLinked = commanderData.isSpeedLinked
            self._container.handleVehicleSpeedLinkChanged(self.id, self.__isSpeedLinked)

    def updateCommanderGroup(self, groupID):
        if self.__isFirstGroupIdUpdate:
            arena = avatar_getter.getArena()
            if arena:
                self.__isFirstGroupIdUpdate = False
                arena.onGameModeSpecifcStats(True, {self.id: {arena_vos.RtsKeys.VEHICLE_GROUP: groupID}})
        if self.groupID != groupID:
            self.__sessionProvider.dynamic.rtsCommander.requester.updateRTSGroup(self.id, groupID)
            self._container.handleVehicleGroupChanged(self.id, groupID)

    def updateTick(self):
        self.__commandsQueue.update()
        if self.isAlive:
            if self.isVisible:
                self.__path.tick(self.position, self.currentPath)
                self.__directionMarker.setVisible(avatar_getter.isCommanderCtrlMode())
                self.__directionMarker.update()
                self.__operationCircle.update()
                self.__updateOverwatchMarker()
            else:
                self.__directionMarker.setVisible(False)
                self.__path.removePath()
        else:
            self._destroyMarkers()
            self.__path.removePath()

    def canQueueCommand(self, commandTypeName, executeNow=False):
        return self.__commandsQueue.canQueueCommand(commandTypeName, executeNow)

    def enqueue(self, commandTypeName, executeNow=False, **kwargs):
        return self.__commandsQueue.enqueue(commandTypeName, executeNow=executeNow, **kwargs)

    def getCommandsGroup(self, groupID):
        return self._container.getCommandsGroup(groupID)

    def handleOnCommandEnqueued(self, command):
        self._container.handleOnCommandEnqueued(command)

    def handleOnCommandDequeued(self, command):
        self._container.handleOnCommandDequeued(command)

    def onRTSEvent(self, event, position):
        self.__commandsQueue.handleRTSEvent(event, position)
        orderData = self._getOrderData()
        if event == RTSEvent.ON_MANNER_MODIFIED_BY_SERVER:
            if orderData is not None:
                self._container.handleVehicleMannerChanged(self.id, orderData.manner)
        elif event == RTSEvent.ON_OVERWATCH_MODE_DISABLED:
            self.__isOverwatchSectorEnabled = False
        elif event == RTSEvent.ON_OVERWATCH_MODE_ENABLED:
            self.__isOverwatchSectorEnabled = True
        elif event == RTSEvent.ON_PURSUIT_TARGET:
            if position is not None and BigWorld.entity(orderData.target) is None:
                if self.__commandsQueue.activeCommand is None:
                    self.enqueue(COMMAND_NAME.PURSUIT, executeNow=True, order=orderData.order, position=position)
        elif event in (RTSEvent.ON_RELOAD, RTSEvent.ON_RELOAD_NON_EMPTY_CLIP):
            self._container.handleVehicleAboutToReload(self.id, isNonEmptyClip=event == RTSEvent.ON_RELOAD_NON_EMPTY_CLIP)
        elif event == RTSEvent.ON_FIRE_LINE_BLOCKED:
            self._container.handleVehicleFireLineBlocked(self.id)
        return

    def onCommandUpdated(self):
        self.__commandsQueue.onCommandUpdated()

    def onCommandComplete(self, command):
        self._container.handleOnCommandComplete(command, self.__commandsQueue.getNumCommandsInQueue)

    @property
    def activeCommand(self):
        return self.__commandsQueue.activeCommand

    def onAimAtVehicle(self, vehicleId):
        self._bwVehicle.cell.onAimAtVehicle(vehicleId if vehicleId is not None else 0)
        return

    @property
    def lastCommandInQueue(self):
        return self.__commandsQueue.lastCommandInQueue

    def updateRTSOrder(self, order=None, manner=None, position=None, target=None, heading=None, baseID=None, baseTeam=None, isForce=False, **extra):
        if not self.isEnabled and not isForce:
            return
        else:
            if manner is not None and not isForce:
                if self._container.isMannerBlocked(manner):
                    manner = None
            if not self.isAllyBot:
                _logger.error('Vehicle with vID: %s is not ally', self.id)
                return
            orderData = self._getOrderData()
            if orderData is None:
                return

            def getValidVector(value, valueFromBase):
                return None if value is None and valueFromBase is None else Math.Vector3(value or valueFromBase)

            newOrderData = OrderData(order=order or orderData.order, manner=manner or orderData.manner, position=getValidVector(position, orderData.position), isPositionModified=orderData.isPositionModified, target=target or orderData.target, heading=getValidVector(heading, orderData.heading), baseID=baseID or orderData.baseID, baseTeam=baseTeam or orderData.baseTeam, companions=extra.get('companions', None))
            isOrderChanged = newOrderData.order != orderData.order
            isMannerChanged = newOrderData.manner != orderData.manner
            packedOrderData = newOrderData.pack()
            self.__sessionProvider.dynamic.rtsCommander.requester.updateRTSOrder(self.id, packedOrderData.order, packedOrderData.manner, packedOrderData.position, packedOrderData.isPositionModified, packedOrderData.target, packedOrderData.heading, packedOrderData.baseID, packedOrderData.baseTeam, packedOrderData.companions)
            if isMannerChanged:
                self._container.handleVehicleMannerChanged(self.id, manner)
            orderKwargs = {'order': newOrderData.order,
             'manner': newOrderData.manner,
             'position': newOrderData.position,
             'isPositionModified': newOrderData.isPositionModified,
             'target': newOrderData.target,
             'heading': newOrderData.heading,
             'baseID': newOrderData.baseID,
             'baseTeam': newOrderData.baseTeam,
             'extra': extra,
             'isOrderChanged': isOrderChanged,
             'isMannerChanged': isMannerChanged,
             'commandQueue': self.__commandsQueue}
            self._container.handleVehicleOrderChanged(self.id, **orderKwargs)
            return newOrderData

    def queryRTSData(self, queryType, context, callback):
        return self.__sessionProvider.dynamic.rtsCommander.requester.queryRTSData(self.id, queryType, context, callback)

    def cancelRTSQuery(self, queryID):
        return self.__sessionProvider.dynamic.rtsCommander.requester.cancelRTSQuery(queryID)

    def _updateVehicleMarkers(self):
        if self.__directionMarker is not None:
            isCommanderCtrlMode = avatar_getter.isCommanderCtrlMode()
            self.__directionMarker.setVisible(self.__isVisualEnabled and self.__isEnabled and isCommanderCtrlMode)
        self.__updateOverwatchMarker()
        return

    def _getOrderData(self):
        commanderData = BigWorld.player().arena.commanderData.get(self.id)
        if not commanderData:
            _logger.error('Vehicle have no commanderData so cant execute orders.If this happens, consider to add more checks or fix synchronization protocols')
            return
        else:
            orderData = commanderData.orderData
            if orderData is None:
                _logger.error('Vehicle commanderData without orderData so cant execute orders vID: %s, commanderData: %s', self.id, commanderData)
                return
            return orderData

    def _destroyMarkers(self):
        if self.__directionMarker is not None:
            self.__directionMarker.fini()
            self.__directionMarker = None
        if self.__overwatchMarker is not None:
            self.__overwatchMarker.fini()
            self.__overwatchMarker = None
        if self.__operationCircle is not None:
            self.__operationCircle.fini()
            self.__operationCircle = None
        return

    def __updateOverwatchMarker(self):
        if self.__overwatchMarker is None:
            return
        else:
            if self.__isOverwatchSectorEnabled:
                if self.lastCommandInQueue and self.lastCommandInQueue.heading:
                    self.__overwatchMarker.setVisible(False)
                else:
                    self.__overwatchMarker.updateVisibilityFromVehicle(self)
                    self.__overwatchMarker.update(self.position, self.yaw)
            else:
                self.__overwatchMarker.setVisible(False)
            return


def makeProxyVehicle(vID, container):
    return _ControllableProxyVehicle(vID, container) if isControllableBot(vID) else _ProxyVehicle(vID, container)


@dependency.replace_none_kwargs(sessionProvider=IBattleSessionProvider)
def _getRosterIndex(vID, sessionProvider=None):
    vInfo = sessionProvider.getArenaDP().getVehicleInfo(vID)
    vehicleCD = vInfo.vehicleType.compactDescr
    rosterVehicles = BigWorld.player().aiRosterVehicles
    return rosterVehicles.index(vehicleCD) if vehicleCD in rosterVehicles else -1
