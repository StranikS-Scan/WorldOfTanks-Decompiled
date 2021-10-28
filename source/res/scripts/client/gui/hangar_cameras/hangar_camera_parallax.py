# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_parallax.py
import Math
import GUI
import BigWorld
import Windowing
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
import math_utils
from account_helpers.settings_core.settings_constants import GAME
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents

def cubicEasing(delta, position):
    return delta ** 3 * position


def linearEasing(delta, position):
    return delta * position


class HangarCameraParallax(CallbackDelayer, TimeDeltaMeter):
    CURSOR_POSITION_CLAMP_VALUE = 2.0
    MAX_DT = 0.05
    settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, camera):
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__camera = camera
        self.__isInIdle = False
        self.__smoothedCursorPosition = Math.Vector2(0.0, 0.0)
        self.__wasPreviousUpdateSkipped = True
        self.__zeroPivot = Math.Vector3(0.0, 0.0, 0.0)
        self.__zeroYaw = 0.0
        self.__zeroPitch = 0.0
        self.__distanceDelta = Math.Vector2(0.0, 0.0)
        self.__anglesDelta = Math.Vector2(0.0, 0.0)
        self.__smoothingMultiplier = 0.0
        self.__isWindowAccessible = True
        self.__isForcedDisabled = False
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__distanceDelta = cfg['cam_parallax_distance']
        self.__anglesDelta = cfg['cam_parallax_angles']
        self.__smoothingMultiplier = cfg['cam_parallax_smoothing']
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def __onSpaceCreated(self):
        self.setEnabled(self.settingsCore.getSetting(GAME.HANGAR_CAM_PARALLAX_ENABLED))
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onForceDisable, EVENT_BUS_SCOPE.LOBBY)
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)

    def __onSpaceDestroy(self, inited):
        self.__isForcedDisabled = False
        if inited:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
            g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__handleIdleCameraActivation)
            g_eventBus.removeListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onForceDisable, EVENT_BUS_SCOPE.LOBBY)
            Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)

    def __onSettingsChanged(self, diff):
        if GAME.HANGAR_CAM_PARALLAX_ENABLED in diff:
            self.setEnabled(self.settingsCore.getSetting(GAME.HANGAR_CAM_PARALLAX_ENABLED))

    def __onWindowAccessibilityChanged(self, isAccessible):
        self.__isWindowAccessible = isAccessible

    def setEnabled(self, isEnabled):
        if isEnabled:
            self.__wasPreviousUpdateSkipped = True
            self.delayCallback(0.0, self.__update)
        else:
            self.stopCallback(self.__update)

    def destroy(self):
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        self.hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.__camera = None
        self.__isInIdle = None
        self.stopCallback(self.__update)
        CallbackDelayer.destroy(self)
        return

    def __updateValues(self):
        matrix = Math.Matrix(self.__camera.source)
        yaw = matrix.yaw
        pitch = matrix.pitch
        pivot = self.__camera.pivotPosition
        self.__smoothedCursorPosition = self.__getClampedCursor()
        self.__zeroPivot.x = pivot.x - linearEasing(self.__distanceDelta.x, self.__smoothedCursorPosition.x)
        self.__zeroPivot.y = pivot.y - linearEasing(self.__distanceDelta.y, self.__smoothedCursorPosition.y)
        self.__zeroPivot.z = pivot.z
        self.__zeroYaw = yaw - cubicEasing(self.__anglesDelta.x, self.__smoothedCursorPosition.x)
        self.__zeroPitch = pitch - cubicEasing(self.__anglesDelta.y, self.__smoothedCursorPosition.y)
        self.measureDeltaTime()

    def __checkToSkipUpdate(self):
        if self.__isForcedDisabled:
            return True
        if not self.__camera or self.__camera != BigWorld.camera():
            return True
        if self.__isInIdle:
            return True
        if Waiting.isVisible():
            return True
        if not self.__isWindowAccessible:
            return True
        currentYaw = Math.Matrix(self.__camera.invViewMatrix).yaw
        currentPitch = Math.Matrix(self.__camera.invViewMatrix).pitch
        goalYaw = Math.Matrix(self.__camera.source).yaw
        goalPitch = -Math.Matrix(self.__camera.source).pitch
        return True if abs(goalYaw - currentYaw) > 0.001 or abs(goalPitch - currentPitch) > 0.001 else False

    def __getClampedCursor(self):
        cursorPosition = GUI.mcursor().position
        cursorPosition.x = math_utils.clamp(-self.CURSOR_POSITION_CLAMP_VALUE, self.CURSOR_POSITION_CLAMP_VALUE, cursorPosition.x)
        cursorPosition.y = math_utils.clamp(-self.CURSOR_POSITION_CLAMP_VALUE, self.CURSOR_POSITION_CLAMP_VALUE, cursorPosition.y)
        return cursorPosition

    def __update(self):
        skipUpdate = self.__checkToSkipUpdate()
        if not skipUpdate:
            if not self.__wasPreviousUpdateSkipped:
                cursorPosition = self.__getClampedCursor()
                k = self.__smoothingMultiplier * min(self.measureDeltaTime(), self.MAX_DT)
                self.__smoothedCursorPosition = cursorPosition * k + self.__smoothedCursorPosition * (1.0 - k)
                pivot = Math.Vector3(self.__zeroPivot)
                pivot.x += linearEasing(self.__distanceDelta.x, self.__smoothedCursorPosition.x)
                pivot.y += linearEasing(self.__distanceDelta.y, self.__smoothedCursorPosition.y)
                self.__camera.pivotPosition = pivot
                yaw = self.__zeroYaw + cubicEasing(self.__anglesDelta.x, self.__smoothedCursorPosition.x)
                pitch = self.__zeroPitch + cubicEasing(self.__anglesDelta.y, self.__smoothedCursorPosition.y)
                mat = Math.Matrix()
                mat.setRotateYPR((yaw, pitch, 0.0))
                self.__camera.source = mat
            else:
                self.__updateValues()
        self.__wasPreviousUpdateSkipped = skipUpdate

    def __handleIdleCameraActivation(self, event):
        self.__isInIdle = event.ctx['started']

    def __onForceDisable(self, event):
        if not event.ctx.get('setParallax'):
            return
        self.__isForcedDisabled = event.ctx['isDisable']
