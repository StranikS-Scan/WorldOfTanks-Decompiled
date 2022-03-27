# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/vehicle_selection.py
import BigWorld
import GUI
import Keys
import aih_constants
import BattleReplay
import Math
from AvatarInputHandler import cameras, aih_global_binding, AvatarInputHandler
from Event import Event
from gui.Scaleform.daapi.view.meta.VehicleSelectionMeta import VehicleSelectionMeta
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.commander.common import hasAppendModifiers, MappedKeys
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider

class _MouseClickHelper(CallbackDelayer):
    onRightMouseButtonDown = Event()
    onRightMouseButtonUp = Event()
    onRightMouseButtonDoubleClick = Event()
    __DISTANCE_TO_TRIGGER = 0.005
    __DOUBLE_CLICK_TIME = 0.5
    __TIME_OF_TOLERANCE = 0.5
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(_MouseClickHelper, self).__init__()
        self.__wasRightMouseButtonDoubleClick = False
        self.__lastMousePosition = None
        self.__lastDoubleClickPosition = None
        self.__isAreaOfToleranceActive = False
        return

    def onHaltPressed(self):
        self.__cancelRightMouseCallback()

    def handleMouse(self):
        info = self.__sessionProvider.dynamic.rtsBWCtrl.getMouseInfo()
        if BigWorld.isKeyDown(Keys.KEY_RIGHTMOUSE) and not BigWorld.isKeyDown(Keys.KEY_LEFTMOUSE):
            self.__checkForMouseMove()
            if not self.__isAreaOfToleranceActive:
                if not self.hasDelayedCallback(self.__rightMouseButtonUp) and info.mouseRightEnabled:
                    self.__rightMouseButtonDown()
                else:
                    currentMousePosition = Math.Vector2(GUI.mcursor().position)
                    if self.__lastMousePosition and self.__lastMousePosition.distSqrTo(currentMousePosition) < self.__DISTANCE_TO_TRIGGER:
                        if info.mouseDoubleRightEnabled:
                            self.__setAreaOfTolerance(True)
                            self.__rightMouseButtonDoubleClick()
                            self.__lastDoubleClickPosition = currentMousePosition
                    elif info.mouseRightEnabled:
                        self.__rightMouseButtonUp()
                        self.__rightMouseButtonDown()
        elif self.__wasRightMouseButtonDoubleClick:
            self.__wasRightMouseButtonDoubleClick = False
        elif not self.hasDelayedCallback(self.__rightMouseButtonUp) and not self.__isAreaOfToleranceActive:
            self.delayCallback(0.0, self.__checkForMouseMove)
            if not self.hasDelayedCallback(self.__setAreaOfTolerance):
                self.delayCallback(self.__TIME_OF_TOLERANCE, self.__setAreaOfTolerance, False)
            self.delayCallback(self.__DOUBLE_CLICK_TIME, self.__rightMouseButtonUp)
            self.__lastMousePosition = Math.Vector2(GUI.mcursor().position)
            self.__rightMouseButtonUp(isDoubleClickPossible=True)

    def __rightMouseButtonDoubleClick(self):
        self.__wasRightMouseButtonDoubleClick = True
        self.__cancelRightMouseCallback()
        self.onRightMouseButtonDoubleClick()

    def __rightMouseButtonDown(self):
        self.onRightMouseButtonDown()

    def __checkForMouseMove(self):
        currentMousePosition = Math.Vector2(GUI.mcursor().position)
        if self.__lastDoubleClickPosition and self.__lastDoubleClickPosition.distSqrTo(currentMousePosition) > self.__DISTANCE_TO_TRIGGER:
            self.__setAreaOfTolerance(False)
        if self.__lastMousePosition and self.__lastMousePosition.distSqrTo(currentMousePosition) > self.__DISTANCE_TO_TRIGGER:
            self.__rightMouseButtonUp()
            return -1.0

    def __rightMouseButtonUp(self, isDoubleClickPossible=False):
        if not isDoubleClickPossible:
            self.__cancelRightMouseCallback()
        if not self.__isAreaOfToleranceActive:
            self.onRightMouseButtonUp(isDoubleClickPossible)

    def __cancelRightMouseCallback(self):
        self.stopCallback(self.__checkForMouseMove)
        self.stopCallback(self.__rightMouseButtonUp)
        self.__lastMousePosition = None
        return

    def __setAreaOfTolerance(self, value):
        self.__isAreaOfToleranceActive = value


class _InsideDragBox(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self._vehInside = set()

    def update(self, vehInside):
        toAdd = vehInside - self._vehInside
        toRemove = self._vehInside - vehInside
        vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
        vehicles.setInsideDragBox(toAdd)
        vehicles.clearInsideDragBox(toRemove)
        vehicles.setDragBoxActivated(True)
        self._vehInside = vehInside

    def finish(self):
        vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
        vehicles.clearInsideDragBox()
        vehicles.setDragBoxActivated(False)
        if hasAppendModifiers():
            vehicles.toggleSelection(self._vehInside)
        else:
            vehicles.setSelection(self._vehInside)
            vehicles.handleVehicleSelectionChangeAttempt(self._vehInside)
        selectedVehiclesIDs = self.__sessionProvider.dynamic.rtsCommander.vehicles.keys(lambda v: v.isSelected)
        self.__sessionProvider.dynamic.rtsSound.selectionChanged(selectedVehiclesIDs, False)
        self._vehInside.clear()


class VehicleSelection(VehicleSelectionMeta, CallbackDelayer):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __aihCtrlModeName = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)

    def __init__(self):
        super(VehicleSelection, self).__init__()
        self.__selectionParams = None
        self.__scale = 1.0
        self.__mouseClickHelper = _MouseClickHelper()
        self._insideDragBox = _InsideDragBox()
        return

    def _populate(self):
        super(VehicleSelection, self)._populate()
        self.__scale = round(self.__settingsCore.interfaceScale.get(), 1)
        handler = avatar_getter.getInputHandler()
        if handler is not None and isinstance(handler, AvatarInputHandler):
            handler.onCameraChanged += self.__onCameraChanged
        self.__settingsCore.interfaceScale.onScaleChanged += self.__onScaleFactorChanged
        self.__mouseClickHelper.onRightMouseButtonDown += self.__onRightMouseButtonDown
        self.__mouseClickHelper.onRightMouseButtonUp += self.__onRightMouseButtonUp
        self.__mouseClickHelper.onRightMouseButtonDoubleClick += self.__onRightMouseButtonDoubleClick
        self.__sessionProvider.dynamic.rtsCommander.onRTSKeyEvent += self.__onRTSKeyEvent
        self.__onCameraChanged()
        return

    def _dispose(self):
        self.__mouseClickHelper.onRightMouseButtonDoubleClick -= self.__onRightMouseButtonDoubleClick
        self.__mouseClickHelper.onRightMouseButtonUp -= self.__onRightMouseButtonUp
        self.__mouseClickHelper.onRightMouseButtonDown -= self.__onRightMouseButtonDown
        self.__settingsCore.interfaceScale.onScaleChanged -= self.__onScaleFactorChanged
        if self.__sessionProvider.dynamic.rtsCommander:
            self.__sessionProvider.dynamic.rtsCommander.onRTSKeyEvent -= self.__onRTSKeyEvent
        handler = avatar_getter.getInputHandler()
        if handler is not None and isinstance(handler, AvatarInputHandler):
            handler.onCameraChanged -= self.__onCameraChanged
        self.setEnabled(False)
        super(VehicleSelection, self)._dispose()
        return

    def setSelectionParams(self, topX, topY, bottomX, bottomY, finish):
        w, h = GUI.screenResolution()
        halfMaxX = w / 2.0 / self.__scale
        halfMaxY = h / 2.0 / self.__scale
        left = (topX - halfMaxX) / halfMaxX
        top = (halfMaxY - topY) / halfMaxY
        right = (bottomX - halfMaxX) / halfMaxX
        bottom = (halfMaxY - bottomY) / halfMaxY
        self.__selectionParams = (left,
         top,
         right,
         bottom,
         finish)

    def handleMouseWheel(self, delta):
        if BattleReplay.isPlaying():
            handler = avatar_getter.getInputHandler()
            if handler is not None and isinstance(handler, AvatarInputHandler):
                return handler.ctrl.camera.handleMouseWheel(int(delta))
        self.__sessionProvider.dynamic.rtsCommander.handleMouseWheel(int(delta))
        return

    def handleRightMouseBtn(self):
        info = self.__sessionProvider.dynamic.rtsBWCtrl.getMouseInfo()
        if info.mouseRightEnabled:
            self.__mouseClickHelper.handleMouse()

    def handleMouseOverUI(self, isOverUI):
        self.__sessionProvider.dynamic.rtsBWCtrl.setMouseOverUI(isOverUI)

    def isEnabledForMode(self, mode=None):
        if BattleReplay.isPlaying():
            return False
        if not mode:
            mode = self.__aihCtrlModeName
        return mode == aih_constants.CTRL_MODE_NAME.COMMANDER

    def setEnabled(self, enabled):
        if enabled:
            self.delayCallback(0.0, self.__update)
        else:
            self.stopCallback(self.__update)
            self.__selectionParams = None
        self.as_setEnabledS(enabled)
        return

    def __onRightMouseButtonDown(self):
        self.__sessionProvider.dynamic.rtsCommander.handleRightMouseButtonDown()

    def __onRightMouseButtonUp(self, isDoubleClickPossible):
        self.__sessionProvider.dynamic.rtsCommander.handleRightMouseButtonUp(isDoubleClickPossible)

    def __onRightMouseButtonDoubleClick(self):
        self.__sessionProvider.dynamic.rtsCommander.handleRightMouseButtonDoubleClick()

    def __onRTSKeyEvent(self, isDown, key):
        if isDown and MappedKeys.isMappedTo(key, MappedKeys.KEY_HALT):
            self.__mouseClickHelper.onHaltPressed()

    def __update(self):
        if self.__selectionParams:
            left, top, right, bottom, finish = self.__selectionParams
            vehicles = self.__sessionProvider.dynamic.rtsCommander.vehicles
            focusedID = vehicles.focusedID
            currentlyInside = set()
            currentlyInside.update([focusedID] if focusedID else [])

            def inSelectionRect(vehicle):
                p = cameras.projectPoint(vehicle.position)
                return left < p.x < right and bottom < p.y < top

            currentlyInside.update([ v.id for v in BigWorld.player().vehicles if inSelectionRect(v) ])
            target = BigWorld.player().target
            currentlyInside.update([target.id] if target else [])
            self._insideDragBox.update(currentlyInside)
            if finish:
                self.__onSelectionFinished()

    def __onCameraChanged(self, mode=None, *_):
        self.setEnabled(self.isEnabledForMode(mode))

    def __onScaleFactorChanged(self, scale):
        scale = round(scale, 1)
        if self.__scale != scale:
            self.__scale = scale

    def __onSelectionFinished(self):
        self._insideDragBox.finish()
        self.__selectionParams = None
        self.__sessionProvider.dynamic.rtsCommander.vehicles.handleSelectionFinished()
        return
