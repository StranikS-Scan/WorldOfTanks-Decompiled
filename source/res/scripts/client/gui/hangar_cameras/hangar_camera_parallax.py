# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_parallax.py
import Math
import GUI
import BigWorld
import Windowing
import Keys
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
import math_utils
from account_helpers.settings_core.settings_constants import GAME
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui import g_keyEventHandlers

def cubicEasing(delta, position):
    return delta ** 3 * position


def linearEasing(delta, position):
    return delta * position


class HangarCameraParallax(CallbackDelayer, TimeDeltaMeter):
    CURSOR_POSITION_CLAMP_VALUE = 2.0
    MAX_DT = 0.05
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, camera):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__camera = camera
        self.__isInIdle = False
        self.__smoothedCursorPosition = Math.Vector2(0.0, 0.0)
        self.__wasPreviousUpdateSkipped = True
        self.__distanceDelta = Math.Vector2(0.0, 0.0)
        self.__anglesDelta = Math.Vector2(0.0, 0.0)
        self.__smoothingMultiplier = 0.0
        self.__isEnabled = True
        self.__isWindowAccessible = True
        self.__isMouseDown = False
        self.__isActive = False
        self.__isInitialized = False
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        g_keyEventHandlers.add(self.__handleKeyEvent)
        Windowing.addWindowAccessibilitynHandler(self.onWindowAccessibilityChanged)
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onForceDisable, EVENT_BUS_SCOPE.LOBBY)

    def destroy(self):
        if self.__isActive:
            return
        else:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
            g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
            g_keyEventHandlers.remove(self.__handleKeyEvent)
            Windowing.removeWindowAccessibilityHandler(self.onWindowAccessibilityChanged)
            g_eventBus.removeListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onForceDisable, EVENT_BUS_SCOPE.LOBBY)
            self.__camera = None
            self.__isInIdle = None
            self.stopCallback(self.__update)
            CallbackDelayer.destroy(self)
            return

    def initialize(self, distanceDelta, angelsDelta, smoothing):
        self.__distanceDelta = distanceDelta
        self.__anglesDelta = angelsDelta
        self.__smoothingMultiplier = smoothing
        self.__isInitialized = True

    def activate(self):
        if self.__isActive or not self.__isInitialized:
            return
        self.setEnabled()
        self.delayCallback(0.0, self.__update)
        self.__smoothedCursorPosition = self.__getClampedCursor()
        self.__isActive = True
        self.__wasPreviousUpdateSkipped = True

    def deactivate(self):
        self.__isInitialized = False
        if self.__isActive:
            self.stopCallback(self.__update)
            self.__isActive = False

    def isActive(self):
        return self.__isActive

    def __onSettingsChanged(self, diff):
        if GAME.HANGAR_CAM_PARALLAX_ENABLED in diff:
            self.setEnabled()

    def onWindowAccessibilityChanged(self, isAccessible):
        self.__isWindowAccessible = isAccessible

    def setEnabled(self, isEnabled=True):
        self.__isEnabled = self.settingsCore.getSetting(GAME.HANGAR_CAM_PARALLAX_ENABLED) and isEnabled

    def __handleKeyEvent(self, event):
        if event.key == Keys.KEY_LEFTMOUSE:
            self.__isMouseDown = event.isKeyDown()

    def __checkToSkipUpdate(self):
        if not self.__isEnabled:
            return True
        if self.__isMouseDown:
            return True
        if not self.__camera or self.__camera != BigWorld.camera() or self.__camera.isInTransition():
            return True
        if self.__isInIdle:
            return True
        if Waiting.isVisible():
            return True
        return True if not self.__isWindowAccessible else False

    def __getClampedCursor(self):
        cursorPosition = GUI.mcursor().position
        cursorPosition.x = math_utils.clamp(-self.CURSOR_POSITION_CLAMP_VALUE, self.CURSOR_POSITION_CLAMP_VALUE, cursorPosition.x)
        cursorPosition.y = math_utils.clamp(-self.CURSOR_POSITION_CLAMP_VALUE, self.CURSOR_POSITION_CLAMP_VALUE, cursorPosition.y)
        return cursorPosition

    def __update(self):
        skipUpdate = self.__checkToSkipUpdate()
        if not skipUpdate:
            cursorPosition = self.__getClampedCursor()
            prevSmoothedCursorPosition = self.__smoothedCursorPosition
            if self.__wasPreviousUpdateSkipped:
                self.__smoothedCursorPosition = cursorPosition
                self.measureDeltaTime()
            else:
                k = self.__smoothingMultiplier * min(self.measureDeltaTime(), self.MAX_DT)
                self.__smoothedCursorPosition = cursorPosition * k + self.__smoothedCursorPosition * (1.0 - k)
            pivotPositionDelta = Math.Vector3(linearEasing(self.__distanceDelta.x, self.__smoothedCursorPosition.x) - linearEasing(self.__distanceDelta.x, prevSmoothedCursorPosition.x), linearEasing(self.__distanceDelta.y, self.__smoothedCursorPosition.y) - linearEasing(self.__distanceDelta.y, prevSmoothedCursorPosition.y), 0)
            self.__camera.pivotPosition += pivotPositionDelta
            matrix = Math.Matrix(self.__camera.source)
            yawDelta = cubicEasing(self.__anglesDelta.x, self.__smoothedCursorPosition.x) - cubicEasing(self.__anglesDelta.x, prevSmoothedCursorPosition.x)
            pitchDelta = cubicEasing(self.__anglesDelta.y, self.__smoothedCursorPosition.y) - cubicEasing(self.__anglesDelta.y, prevSmoothedCursorPosition.y)
            matrix.setRotateYPR((matrix.yaw + yawDelta, matrix.pitch + pitchDelta, 0.0))
            self.__camera.source = matrix
        self.__wasPreviousUpdateSkipped = skipUpdate

    def __handleIdleCameraActivation(self, event):
        self.__isInIdle = event.ctx['started']

    def __onForceDisable(self, event):
        if event.ctx['setParallax']:
            self.setEnabled(not event.ctx['isDisable'])
