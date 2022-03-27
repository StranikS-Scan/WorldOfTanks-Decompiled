# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/interfaces.py
import typing
from abc import ABCMeta
from gui.battle_control.controllers.interfaces import IBattleController
if typing.TYPE_CHECKING:
    import Vehicle
    from Event import Event
    from gui.battle_control.controllers.commander.proxies.vehicle import RTSGunSettings, _ProxyVehicle
    from gui.battle_control.controllers.commander.common import FocusPriority
    from gui.battle_control.controllers.commander.rts_bw_ctrl import BaseInfo
    from Math import Vector2, Vector3
    from typing import Iterable, Iterator, List, Optional, Set, Callable, Any, Tuple
    from RTSShared import RTSQuery, RTSEvent, RTSCommandQueuePosition, COMMAND_NAME, RTSOrder, RTSManner

class IRTSBWController(IBattleController):
    __metaclass__ = ABCMeta
    onControlPointsReady = None
    onTeamBaseStateChanged = None

    @property
    def controlPoint(self):
        raise NotImplementedError

    @property
    def controlPoints(self):
        raise NotImplementedError

    @property
    def capturingControlPoints(self):
        raise NotImplementedError

    def setMouseOverUI(self, isOverUI):
        raise NotImplementedError

    def toggleAppendDisplay(self, isAppendMode):
        raise NotImplementedError


class IRTSSoundController(IBattleController):
    __metaclass__ = ABCMeta

    def playEnemyDetectedSound(self, enemyID):
        raise NotImplementedError

    def controllableVehicleStateUpdated(self, state, vehicleID):
        raise NotImplementedError

    def selectionChanged(self, selectedVehiclesIDs, selectionViaPanel):
        raise NotImplementedError

    def triggerDeviceDamagedSoundNotification(self, vehicleID, deviceName):
        raise NotImplementedError

    def focusedVehicleChanged(self, focusVehicleID, isInFocus):
        raise NotImplementedError


class IProxyVehicle(object):

    @property
    def id(self):
        raise NotImplementedError

    @property
    def isAlive(self):
        raise NotImplementedError

    @property
    def isVisible(self):
        raise NotImplementedError

    @property
    def isAlly(self):
        raise NotImplementedError

    @property
    def isAllyBot(self):
        raise NotImplementedError

    @property
    def isBot(self):
        raise NotImplementedError

    @property
    def isCommander(self):
        raise NotImplementedError

    @property
    def isControllable(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isEnemy(self):
        raise NotImplementedError

    @property
    def isEnemyBot(self):
        raise NotImplementedError

    @property
    def isObserver(self):
        raise NotImplementedError

    @property
    def isPlayer(self):
        raise NotImplementedError

    @property
    def isSupply(self):
        raise NotImplementedError

    @property
    def insideDragBox(self):
        raise NotImplementedError

    @property
    def isSelected(self):
        raise NotImplementedError

    @isSelected.setter
    def isSelected(self, value):
        raise NotImplementedError

    @property
    def initialized(self):
        raise NotImplementedError

    @property
    def rawGroupID(self):
        raise NotImplementedError

    @property
    def groupID(self):
        raise NotImplementedError

    @property
    def typeDescriptor(self):
        raise NotImplementedError

    @property
    def vehicleClassTag(self):
        raise NotImplementedError

    @property
    def appearance(self):
        raise NotImplementedError

    @property
    def maxHealth(self):
        raise NotImplementedError

    @property
    def matrix(self):
        raise NotImplementedError

    @property
    def yaw(self):
        raise NotImplementedError

    @property
    def pitch(self):
        raise NotImplementedError

    @property
    def position(self):
        raise NotImplementedError

    @property
    def lastKnownPosition(self):
        raise NotImplementedError

    @property
    def targetPosition(self):
        raise NotImplementedError

    @property
    def lastPosition(self):
        raise NotImplementedError

    @property
    def aimParams(self):
        raise NotImplementedError

    @property
    def activeGunIndex(self):
        raise NotImplementedError

    @property
    def serverGunAngles(self):
        raise NotImplementedError

    @property
    def reloadingState(self):
        raise NotImplementedError

    @reloadingState.setter
    def reloadingState(self, value):
        raise NotImplementedError

    @property
    def gunSettings(self):
        raise NotImplementedError

    @property
    def activeCommand(self):
        raise NotImplementedError

    @property
    def lastCommandInQueue(self):
        raise NotImplementedError

    @property
    def manner(self):
        raise NotImplementedError

    @property
    def order(self):
        raise NotImplementedError

    def setAmmo(self, cd, quantity, quantityInClip):
        raise NotImplementedError

    def setCurrentShellCD(self, cd):
        raise NotImplementedError

    def enableVisual(self):
        raise NotImplementedError

    def disableVisual(self):
        raise NotImplementedError

    def enableVehicle(self):
        raise NotImplementedError

    def disableVehicle(self):
        raise NotImplementedError

    def updateRTSOrder(self, order=None, manner=None, position=None, target=None, heading=None, baseID=None, baseTeam=None, **extra):
        raise NotImplementedError

    def queryRTSData(self, queryType, context, callback):
        raise NotImplementedError

    def updateCommanderGroup(self, groupID):
        raise NotImplementedError

    def changeManner(self, manner):
        raise NotImplementedError

    def updateTick(self):
        raise NotImplementedError

    def canQueueCommand(self, commandTypeName, executeNow=False):
        raise NotImplementedError

    def enqueue(self, commandTypeName, executeNow=False, **kwargs):
        raise NotImplementedError

    def getCommandsGroup(self, groupID):
        raise NotImplementedError

    def abortCommands(self):
        raise NotImplementedError

    def halt(self, manner=None, isForce=False):
        raise NotImplementedError

    def onRTSEvent(self, event, position):
        raise NotImplementedError

    def onCommandUpdated(self):
        raise NotImplementedError

    def onCommandComplete(self, command):
        raise NotImplementedError

    def onEnterWorld(self, bwVehicle):
        raise NotImplementedError

    def onLeaveWorld(self, bwVehicle):
        raise NotImplementedError

    def markAsTarget(self, instigator, order):
        raise NotImplementedError

    def unmarkAsTarget(self, instigator):
        raise NotImplementedError

    def handleOnCommandEnqueued(self, command):
        raise NotImplementedError

    def handleOnCommandDequeued(self, command):
        raise NotImplementedError


class IProxiesContainer(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def __getitem__(self, eID):
        raise NotImplementedError

    def get(self, eID, default=None):
        raise NotImplementedError

    def keys(self, criteria=None):
        raise NotImplementedError

    def values(self, criteria=None):
        raise NotImplementedError

    def items(self, criteria=None):
        raise NotImplementedError

    def iterkeys(self, criteria=None):
        raise NotImplementedError

    def itervalues(self, criteria=None):
        raise NotImplementedError

    def iteritems(self, criteria=None):
        raise NotImplementedError


class IProxyVehiclesManager(IProxiesContainer):
    __metaclass__ = ABCMeta
    onVehicleCreated = None
    onVehicleUpdated = None
    onVehicleGroupChanged = None
    onVehicleSpeedLinkChanged = None
    onCommandEnqueued = None
    onCommandComplete = None
    onCommandDequeued = None
    onOrderChanged = None
    onMannerChanged = None
    onVehicleTargeted = None
    onSelectionChanged = None
    onSelectionFinished = None
    onVehicleSelectionChangeAttempt = None
    onVehicleReloading = None
    onVehicleAboutToReload = None
    onVehicleFireLineBlocked = None
    onVehicleShellsUpdated = None
    onVehicleDeviceDamaged = None
    onVehicleDeviceRepaired = None
    onVehicleConditionUpdated = None
    onFocusVehicleChanged = None
    onVehiclesInDragBoxChanged = None
    onVehicleDisabledStateChanged = None
    onVehicleLostWhileAttacked = None
    onVehicleFoundWhileAttacked = None
    onVehicleSpeaking = None
    onMannerBlockStateChanged = None

    @property
    def hasSelection(self):
        raise NotImplementedError

    @property
    def focusedID(self):
        raise NotImplementedError

    @property
    def isRetreatEnabled(self):
        raise NotImplementedError

    def hasEdge(self, vID):
        raise NotImplementedError

    def hasForceSimpleEdge(self, vID):
        raise NotImplementedError

    def enableVisual(self):
        raise NotImplementedError

    def disableVisual(self):
        raise NotImplementedError

    def blockManner(self, manner):
        raise NotImplementedError

    def unblockManner(self, manner):
        raise NotImplementedError

    def resetBlockedManners(self):
        raise NotImplementedError

    def enableVehicle(self, vID=None):
        raise NotImplementedError

    def disableVehicle(self, vID=None):
        raise NotImplementedError

    def handleOnCommandEnqueued(self, command):
        raise NotImplementedError

    def handleOnCommandDequeued(self, command):
        raise NotImplementedError

    def handleSelectionFinished(self):
        raise NotImplementedError

    def handleVehicleDestroyed(self, vID):
        raise NotImplementedError

    def handleVehicleAboutToReload(self, vehicleID, isNonEmptyClip):
        raise NotImplementedError

    def handleVehicleFireLineBlocked(self, vehicleID):
        raise NotImplementedError

    def handleVehicleSelectionChangeAttempt(self, vIDs):
        raise NotImplementedError

    def updateTick(self):
        raise NotImplementedError

    def resetMoveCommand(self):
        raise NotImplementedError

    def startOrientating(self):
        raise NotImplementedError

    def finishMovingOrOrienting(self, isAggressive=False, keepPosition=False):
        raise NotImplementedError

    def activateMoving(self, vehicleIDs, position, append, controlPoint):
        raise NotImplementedError

    def setAmmo(self, vehicleID, compactDescr, quantity, quantityInClip):
        raise NotImplementedError

    def setCurrentShellCD(self, vehicleID, compactDescr):
        raise NotImplementedError

    def canQueueCommand(self, commandTypeName, isRequireAll=True, vehicles=None):
        raise NotImplementedError

    def setDirection(self, direction):
        raise NotImplementedError

    def setFormationIndex(self, index):
        raise NotImplementedError

    def moveSelected(self, worldPos, controlPoint):
        raise NotImplementedError

    def startMoving(self):
        raise NotImplementedError

    def stopOrientating(self):
        raise NotImplementedError

    def vehicleTargeting(self, isAggressive, targetID):
        raise NotImplementedError

    def onRTSEvent(self, rtsEvent, vID, position):
        raise NotImplementedError

    def enqueue(self, vehicleIDs, commandID, executeNow=False, **kwargs):
        raise NotImplementedError

    def abortCommands(self, vehIDs=None):
        raise NotImplementedError

    def halt(self, vehicleIDs):
        raise NotImplementedError

    def changeManner(self, vehicleIDs, manner):
        raise NotImplementedError

    def createControlGroup(self, groupID):
        raise NotImplementedError

    def selectControlGroup(self, groupID):
        raise NotImplementedError

    def getControlGroup(self, groupID):
        raise NotImplementedError

    def getAliveNearCursor(self, criteria):
        raise NotImplementedError

    def setSelection(self, vIDs, selectionViaPanel=True):
        raise NotImplementedError

    def appendSelection(self, vIDs):
        raise NotImplementedError

    def toggleSelection(self, vIDs):
        raise NotImplementedError

    def clearSelection(self, vIDs=None):
        raise NotImplementedError

    def setFocusVehicle(self, vID, isInFocus, priority):
        raise NotImplementedError

    def setInsideDragBox(self, vIDs):
        raise NotImplementedError

    def clearInsideDragBox(self, vIDs=None):
        raise NotImplementedError

    def setDragBoxActivated(self, isActive):
        raise NotImplementedError

    def getCommandsGroup(self, commandsGroupID):
        raise NotImplementedError


class IMoveCommandProducer(object):

    @property
    def isActive(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def moveSelected(self, worldPos, vehicles):
        raise NotImplementedError

    def finishMovingOrOrienting(self):
        raise NotImplementedError

    def disableOrientating(self):
        raise NotImplementedError

    def activateMoving(self, vehicles, position, append, controlPoint, vehicleModels):
        raise NotImplementedError

    def startMoving(self, vehicles, controlPoint):
        raise NotImplementedError

    def startOrientating(self):
        raise NotImplementedError

    def stopOrientating(self):
        raise NotImplementedError

    def setDirection(self, direction):
        raise NotImplementedError

    def setFormationIndex(self, rowCount):
        raise NotImplementedError


class ICommand(object):

    @property
    def isCompleted(self):
        raise NotImplementedError

    @property
    def isExecuted(self):
        raise NotImplementedError

    @property
    def result(self):
        raise NotImplementedError

    @property
    def position(self):
        raise NotImplementedError

    @property
    def order(self):
        raise NotImplementedError

    @property
    def group(self):
        raise NotImplementedError

    @property
    def groupID(self):
        raise NotImplementedError

    @property
    def heading(self):
        raise NotImplementedError

    @property
    def entity(self):
        raise NotImplementedError

    def handleRTSEvent(self, event, position):
        raise NotImplementedError

    def enqueued(self, queuePos):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError

    def updateQueuePosition(self, queuePos):
        raise NotImplementedError

    def canQueueCommand(self, commandTypeName):
        raise NotImplementedError

    def canReplaceQueuedCommand(self, commandTypeName):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def onPreviewAppeared(self):
        pass


class ICommandsGroup(object):
    __slots__ = ()

    @property
    def isGroupComplete(self):
        raise NotImplementedError

    @property
    def id(self):
        raise NotImplementedError

    @property
    def commands(self):
        raise NotImplementedError


class IRequester(object):

    def updateTick(self):
        raise NotImplementedError

    def updateRTSOrder(self, vehicleID, order, manner, position, isPositionModified, target, heading, baseID, baseTeam, companions):
        raise NotImplementedError

    def queryRTSData(self, vehicleID, queryType, context, callback):
        raise NotImplementedError

    def cancelRTSQuery(self, queryID):
        raise NotImplementedError

    def onRTSQueryResult(self, queryResultsList):
        raise NotImplementedError

    def updateRTSGroup(self, vehicleID, groupID):
        raise NotImplementedError


class IRTSCommanderController(IBattleController):
    __metaclass__ = ABCMeta
    onTick = None
    onCameraPositionChanged = None
    onSetMarkerEnabled = None
    onRTSStaticMarkerShow = None
    onRTSStaticMarkerRemove = None
    onRTSKeyEvent = None

    @property
    def isForceOrderModeActive(self):
        raise NotImplementedError

    @property
    def isRetreatModeActive(self):
        raise NotImplementedError

    @property
    def enabled(self):
        raise NotImplementedError

    @property
    def vehicles(self):
        raise NotImplementedError

    @property
    def requester(self):
        raise NotImplementedError

    @property
    def isAppendModeEnabled(self):
        raise NotImplementedError

    def enable(self, *args, **kwargs):
        raise NotImplementedError

    def disable(self):
        raise NotImplementedError

    def getCameraPosition(self):
        raise NotImplementedError

    def setCameraPosition(self, worldPos):
        raise NotImplementedError

    def setCameraPositionAndRotation(self, worldPos, yaw):
        raise NotImplementedError

    def handleKeyEvent(self, isDown, key, mods, event=None):
        raise NotImplementedError

    def handleMouseEvent(self, dx, dy, dz):
        raise NotImplementedError

    def handleRightMouseButtonDoubleClick(self):
        raise NotImplementedError

    def handleRightMouseButtonDown(self):
        raise NotImplementedError

    def handleMouseWheel(self, delta):
        raise NotImplementedError

    def handleRightMouseButtonUp(self, isDoubleClickPossible):
        raise NotImplementedError

    def destroyProxyVehicle(self, vID):
        raise NotImplementedError

    def setCamera(self, camera):
        raise NotImplementedError

    def onRTSEvent(self, rtsEvent, vID, position):
        raise NotImplementedError

    def onStartVehicleControl(self, vID):
        raise NotImplementedError

    def onStopVehicleControl(self, stopControlVID):
        raise NotImplementedError

    def moveToVehicle(self, vehicle):
        raise NotImplementedError

    def moveSelected(self, worldPos, controlPoint):
        raise NotImplementedError

    def enqueue(self, vehicleIDs, command, executeNow=False, **kwargs):
        raise NotImplementedError

    def halt(self, vehicleIDs):
        raise NotImplementedError

    def changeManner(self, vehicleIDs, manner):
        raise NotImplementedError

    def invalidateControlledVehicleState(self, vehicleID, state, value):
        raise NotImplementedError


class IMarker(object):
    __metaclass__ = ABCMeta

    @property
    def position(self):
        raise NotImplementedError

    @property
    def overTerrainOffset(self):
        raise NotImplementedError

    @property
    def yaw(self):
        raise NotImplementedError

    @property
    def size(self):
        raise NotImplementedError

    @property
    def scale(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def move(self, position, overTerrainOffset=None):
        raise NotImplementedError

    def rotate(self, yaw):
        raise NotImplementedError

    def resize(self, size):
        raise NotImplementedError

    def scaling(self, scale):
        raise NotImplementedError

    def setCommandQueuePosition(self, queuePos):
        raise NotImplementedError

    def cleanVehicleMarkerRef(self):
        pass

    def update(self, *args, **kwargs):
        raise NotImplementedError

    def _setupMarker(self):
        raise NotImplementedError


class IMarkerColor(object):
    __metaclass__ = ABCMeta

    @property
    def color(self):
        raise NotImplementedError

    @color.setter
    def color(self, color):
        raise NotImplementedError

    @property
    def alpha(self):
        raise NotImplementedError

    @alpha.setter
    def alpha(self, alpha):
        raise NotImplementedError

    @property
    def colorWithAlpha(self):
        raise NotImplementedError

    def setColorWithAlpha(self, color, alpha):
        raise NotImplementedError


class IMarkerVisible(object):
    __metaclass__ = ABCMeta

    def isVisible(self):
        raise NotImplementedError

    def setVisible(self, isVisible):
        raise NotImplementedError


class IMarkerEnabled(object):
    __metaclass__ = ABCMeta

    def isEnabled(self):
        raise NotImplementedError

    def setEnabled(self, isEnabled):
        raise NotImplementedError
