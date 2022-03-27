# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/rts_commander_ctrl.py
import typing
import logging
import aih_constants
import BattleReplay
import BigWorld
import GUI
import Keys
import CGF
from PlayerEvents import g_playerEvents
from Event import Event, EventManager
from AvatarInputHandler import aih_global_binding
from BattleReplay import CallbackDataNames
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VehicleConditions
from gui.battle_control.controllers.commander.common import center, MappedKeys
from gui.battle_control.controllers.commander.interfaces import IRTSCommanderController
from gui.battle_control.controllers.commander.key_helper import KeyHelper
from gui.battle_control.controllers.commander.proxies.camera import CameraProxy
from gui.battle_control.controllers.commander.proxies.vehicles_mgr import ProxyVehiclesManager
from gui.battle_control.controllers.commander.requests import Requester
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from rts.base_highlight import BaseHighlightComponent
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Tuple, Optional
    import Math
_logger = logging.getLogger(__name__)

class RTSCommanderController(CallbackDelayer, KeyHelper, IRTSCommanderController):
    __aihCtrlModeName = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)
    __appLoader = dependency.descriptor(IAppLoader)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __MIN_CONTROL_GROUP_NUM = 1
    __MAX_CONTROL_GROUP_NUM = 7

    def __init__(self):
        CallbackDelayer.__init__(self)
        KeyHelper.__init__(self)
        self.__eventManager = EventManager()
        self.onTick = Event(self.__eventManager)
        self.onCameraPositionChanged = Event(self.__eventManager)
        self.onSetMarkerEnabled = Event(self.__eventManager)
        self.onRTSStaticMarkerShow = Event(self.__eventManager)
        self.onRTSStaticMarkerRemove = Event(self.__eventManager)
        self.onRTSKeyEvent = Event(self.__eventManager)
        self.__enabled = False
        self.__inAppendMode = None
        self.__isAppendModeEnabled = True
        self.__focusedVehicleIndex = -1
        self.__cameraProxy = None
        self.__requester = Requester()
        self.__proxies = ProxyVehiclesManager()
        self.isForceOrderModeEnabled = True
        self.__isMinimapInteractionEnabled = True
        self.__isForceOrderModeActive = False
        self.__isRetreatModeActive = False
        self.__enemyInAreaOfTolerance = False
        return

    @property
    def isMinimapInteractionEnabled(self):
        return self.__isMinimapInteractionEnabled

    @property
    def isForceOrderModeActive(self):
        return self.__isForceOrderModeActive

    @property
    def isRetreatModeActive(self):
        return self.__isRetreatModeActive

    @property
    def enabled(self):
        return self.__enabled

    @property
    def vehicles(self):
        return self.__proxies

    @property
    def requester(self):
        return self.__requester

    @property
    def isAppendModeEnabled(self):
        return self.__isAppendModeEnabled

    @isMinimapInteractionEnabled.setter
    def isMinimapInteractionEnabled(self, enabled):
        self.__isMinimapInteractionEnabled = enabled

    @isAppendModeEnabled.setter
    def isAppendModeEnabled(self, enabled):
        self.__isAppendModeEnabled = enabled

    def getControllerID(self):
        return BATTLE_CTRL_ID.RTS_COMMANDER_CTRL

    def startControl(self, *args):
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
        self.delayCallback(0.0, self.__update)

    def stopControl(self):
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        self.__eventManager.clear()
        self.stopCallback(self.__update)

    def setCamera(self, camera):
        if self.__cameraProxy is None:
            self.__cameraProxy = CameraProxy(camera)
        else:
            self.__cameraProxy.reset(camera)
        return

    def setCurrentShellCD(self, vehicleID, value):
        if self.enabled:
            self.__proxies.setCurrentShellCD(vehicleID, value)

    def enable(self, *args, **kwargs):
        if self.__enabled:
            return
        self.__enabled = True
        self.__cameraProxy.enable(*args, **kwargs)

    def disable(self):
        if not self.__enabled:
            return
        else:
            self.__cameraProxy.disable()
            self.__enabled = False
            cursorMgr = self.__appLoader.getApp().cursorMgr
            if cursorMgr is not None:
                cursorMgr.detachCursor()
            return

    def moveSelected(self, worldPos, controlPoint=None):
        return self.__proxies.moveSelected(worldPos, controlPoint or self.__sessionProvider.dynamic.rtsBWCtrl.controlPoint)

    def onRTSEvent(self, rtsEvent, vID, position):
        if not BigWorld.player().arena.commanderData.get(vID):
            _logger.error('Vehicle have no commanderData so cant execute orders.')
            return
        self.__proxies.onRTSEvent(rtsEvent, vID, position)

    def handleKeyEvent(self, isDown, key, mods, event=None):
        if not self.__isForceOrderModeActive:
            if MappedKeys.isMappedTo(key, MappedKeys.KEY_RETREAT) and self.__proxies.isRetreatEnabled:
                self.__isRetreatModeActive = isDown
                if isDown:
                    self.__isForceOrderModeActive = False
                elif BigWorld.isKeyDown(MappedKeys.getKey(MappedKeys.KEY_FORCE_ORDER_MODE)) and self.isForceOrderModeEnabled:
                    self.__isForceOrderModeActive = True
        else:
            self.__isRetreatModeActive = False
        if not self.__isRetreatModeActive:
            if MappedKeys.isMappedTo(key, MappedKeys.KEY_FORCE_ORDER_MODE) and self.isForceOrderModeEnabled:
                self.__isForceOrderModeActive = isDown
                if isDown:
                    self.__isRetreatModeActive = False
                elif BigWorld.isKeyDown(MappedKeys.getKey(MappedKeys.KEY_RETREAT)) and self.__proxies.isRetreatEnabled:
                    self.__isRetreatModeActive = True
        else:
            self.__isForceOrderModeActive = False
        if self.__aihCtrlModeName == aih_constants.CTRL_MODE_NAME.COMMANDER:
            self.onRTSKeyEvent(isDown, key)
        if self.__aihCtrlModeName == aih_constants.CTRL_MODE_NAME.COMMANDER and isDown:
            manner = MappedKeys.getMannerByKeyCode(key)
            if manner is not None:
                self.__setMannerForSelection(manner)
                return True
        if BigWorld.isKeyDown(Keys.KEY_LCONTROL) and isDown and key == Keys.KEY_A:
            vIDs = self.__proxies.keys(lambda v: v.isControllable)
            self.__proxies.setSelection(vIDs)
            self.__sessionProvider.dynamic.rtsSound.selectionChanged(vIDs, selectionViaPanel=True)
            return True
        elif not BigWorld.isKeyDown(Keys.KEY_CAPSLOCK) and isDown and key == Keys.KEY_K:
            BigWorld.player().cell.toggleRTSSpeedSync(not BigWorld.isKeyDown(Keys.KEY_LCONTROL))
            return True
        elif MappedKeys.isKey(event, MappedKeys.KEY_HALT) and isDown:
            self.__proxies.halt(self.__proxies.keys(lambda v: v.isSelected))
            return True
        elif MappedKeys.isKey(event, MappedKeys.KEY_SHOW_NEXT):
            self.__showNextVehicle()
            return True
        else:
            self.__toggleAppendDisplay(MappedKeys.isModifierDown(MappedKeys.MOD_APPEND_ORDER) and self.__isAppendModeEnabled)
            isDoublePress = self.isDoublePress(isDown, key)
            if not BigWorld.isKeyDown(Keys.KEY_CAPSLOCK):
                self.__handleControlGroups(event, isDoublePress)
            return self.__cameraProxy.handleKeyEvent(isDown, key, mods, event)

    def handleMouseEvent(self, dx, dy, dz):
        if not self.__enabled:
            return False
        if not any((dx, dy, dz)):
            return False
        if BattleReplay.g_replayCtrl.isRecording:
            cursor = GUI.mcursor()
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.REPLAY_MOUSE, (cursor.position.x, cursor.position.y))
        return self.__cameraProxy.handleMouseEvent(dx, dy, dz)

    def handleRightMouseButtonDoubleClick(self):
        if not self.__enabled or BattleReplay.isPlaying():
            return
        else:
            _triggerHoveredBase()
            if self.__enemyInAreaOfTolerance and self.__handleAttackOrder(True, self.__enemyInAreaOfTolerance):
                self.__enemyInAreaOfTolerance = None
                return
            return None if self.__handleMoveOrder(True) else None

    def handleRightMouseButtonDown(self):
        if not self.__enabled or BattleReplay.isPlaying():
            return
        _triggerHoveredBase()
        self.__proxies.resetMoveCommand()
        self.__enemyInAreaOfTolerance = self.__proxies.getAliveNearCursor(lambda e: e.isEnemy)
        if self.__enemyInAreaOfTolerance and self.__proxies.hasSelection and self.__handleAttackOrder(self.__isForceOrderModeActive, self.__enemyInAreaOfTolerance):
            return
        return None if not self.__enemyInAreaOfTolerance and self.__proxies.startMoving() else None

    def handleMouseWheel(self, delta):
        self.__cameraProxy.handleMouseWheel(delta)

    def handleRightMouseButtonUp(self, isDoubleClickPossible):
        if not self.__enabled or BattleReplay.isPlaying():
            return
        else:
            if self.__isForceOrderModeActive:
                _triggerHoveredBase()
                self.__handleMoveOrder(True)
            else:
                if isDoubleClickPossible:
                    self.__proxies.stopOrientating()
                    self.__proxies.disableOrientating()
                    self.__proxies.stopRebuildingPositions()
                    self.__handleMoveOrder(False, keepPosition=True)
                    return
                self.__enemyInAreaOfTolerance = None
            return

    def destroyProxyVehicle(self, vID):
        self.__proxies.handleVehicleDestroyed(vID)

    def getCameraPosition(self):
        return self.__cameraProxy.position if self.__enabled else None

    def setCameraPosition(self, worldPos):
        if self.__enabled:
            self.__cameraProxy.teleportWithFocusOnPoint(worldPos)

    def enablePlayerCameraAdjustment(self, enable):
        self.__cameraProxy.enablePlayerCameraAdjustment(enable)

    def setCameraPositionAndRotation(self, worldPos, yaw):
        if self.__enabled:
            self.__cameraProxy.moveToPos(worldPos, yaw)

    def enableHorizontalCameraMovement(self, enable):
        self.__cameraProxy.enableHorizontalCameraMovement(enable)

    def moveToVehicle(self, vehicleID):
        self.__cameraProxy.moveToVehicle(self.__proxies.get(vehicleID))

    def onStartVehicleControl(self, vID):
        self.__proxies.disableVisual()
        self.__proxies.clearInsideDragBox()
        self.__proxies.clearSelection()
        self.__proxies.abortCommands([vID])
        self.__toggleAppendDisplay(False)
        self.__isRetreatModeActive = False
        self.__isForceOrderModeActive = False

    def onStopVehicleControl(self, stopControlVehID):
        self.__proxies.enableVisual()
        self.__proxies.setSelection([stopControlVehID])

    def enqueue(self, vehicleIDs, command, executeNow=False, **kwargs):
        self.__proxies.enqueue(vehicleIDs, command, executeNow=executeNow, **kwargs)

    def halt(self, vehicleIDs, manner=None):
        self.__proxies.halt(vehicleIDs, manner)

    def changeManner(self, vehicleIDs, manner):
        self.__proxies.changeManner(vehicleIDs, manner)

    def invalidateControlledVehicleState(self, vehicleID, state, value):
        if not self.__proxies.canShowVehicleStatus(vehicleID):
            return
        self.__proxies.controllableVehicleStateUpdated(state, value, vehicleID)
        self.__sessionProvider.dynamic.rtsSound.controllableVehicleStateUpdated(state, vehicleID)

    def __setMannerForSelection(self, manner):
        selected = self.__sessionProvider.dynamic.rtsCommander.vehicles.values(lambda v: v.isSelected)
        for v in selected:
            if manner != v.orderData.manner:
                self.__proxies.changeManner([ veh.id for veh in selected ], manner)
                return

    def __onBattleSessionStart(self):
        g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __onBattleSessionStop(self):
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__proxies.fini()

    def __onAvatarReady(self):
        self.__proxies.init()

    def __update(self):
        self.__proxies.updateTick()
        if self.__enabled:
            self.onTick()
        self.__requester.updateTick()

    def __handleAttackOrder(self, isAggressive, enemy):
        return self.__proxies.vehicleTargeting(isAggressive, enemy)

    def __handleMoveOrder(self, isAggresive, keepPosition=False):
        return self.__proxies.finishMovingOrOrienting(isAggresive, keepPosition=keepPosition)

    def __handleControlGroups(self, event, isDoublePress):
        for groupID in xrange(self.__MIN_CONTROL_GROUP_NUM, self.__MAX_CONTROL_GROUP_NUM + 1):
            mappedKey = MappedKeys.KEY_GROUP_0 + groupID
            if MappedKeys.isKey(event, mappedKey):
                if MappedKeys.isModifierDown(MappedKeys.MOD_CREATE_GROUP):
                    self.__proxies.createControlGroup(groupID)
                else:
                    self.__proxies.selectControlGroup(groupID)
                    if isDoublePress:
                        controlGroup = self.__proxies.getControlGroup(groupID)
                        sizeOfGroup = len(controlGroup)
                        if sizeOfGroup > 1:
                            pos = center(tuple((vehicle.position for vehicle in controlGroup)))
                            self.__cameraProxy.moveToPosKeepRotation(pos)
                        elif sizeOfGroup == 1:
                            self.__cameraProxy.moveToVehicle(controlGroup[0])

    def __showNextVehicle(self):
        friendlyIDs = self.__proxies.keys(lambda e: e.isSelected) or self.__proxies.keys(lambda e: e.isAllyBot)
        if not friendlyIDs:
            return
        self.__focusedVehicleIndex = (self.__focusedVehicleIndex + 1) % len(friendlyIDs)
        vID = friendlyIDs[self.__focusedVehicleIndex]
        self.moveToVehicle(vID)

    def __toggleAppendDisplay(self, isAppendMode):
        if self.__inAppendMode != isAppendMode:
            self.__inAppendMode = isAppendMode
            self.__sessionProvider.dynamic.rtsBWCtrl.toggleAppendDisplay(isAppendMode)


def _triggerHoveredBase():
    avatar = BigWorld.player()
    query = CGF.Query(avatar.spaceID, BaseHighlightComponent)
    for baseComponent in query:
        if baseComponent.hovered:
            baseComponent.trigger()


def getPrioritizedCondition(vehicleID, conditions):
    condition = VehicleConditions.NO_CONDITION
    if isinstance(conditions, dict) and vehicleID in conditions:
        condition = ''
        for cond in conditions[vehicleID]:
            if condition == '' or VehicleConditions.CONDITIONS_PRIORITIES[cond] < VehicleConditions.CONDITIONS_PRIORITIES[condition]:
                condition = cond

    return condition
