# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_idle.py
import math
import BigWorld
import Math
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
import math_utils
from account_helpers.settings_core.settings_constants import GAME
import gui.hangar_cam_settings as settings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from .hangar_camera_settings_listener import HangarCameraSettingsListener

class HangarCameraIdle(HangarCameraSettingsListener, CallbackDelayer, TimeDeltaMeter):
    TIME_OUT = 0.8
    MAX_DT = 0.05

    class IdleParams(object):

        def __init__(self):
            self.minValue = 0.0
            self.maxValue = 0.0
            self.period = 1.0
            self.startTime = 0.0
            self.startValue = 0.0
            self.speed = 0.0

    def __init__(self, camera):
        HangarCameraSettingsListener.__init__(self)
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__camera = camera
        self.__easingInTime = None
        self.__pitchParams = None
        self.__distParams = None
        self.__yawPeriod = None
        self.__yawSpeed = 0.0
        self.__currentIdleTime = 0.0
        self.__camPeriod = 0
        self.__isForcedDisabled = False
        self.__disabledCount = 0
        self.__camPeriod = 0
        self.__isActive = False
        self.__isInitialized = False
        self.registerSettingHandler(GAME.HANGAR_CAM_PERIOD, self._onHangarCamPeriodChanged)
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onCameraForceDisable, EVENT_BUS_SCOPE.LOBBY)
        return

    def destroy(self):
        if self.__isActive:
            return
        else:
            self.__isForcedDisabled = False
            self.__pitchParams = None
            self.__distParams = None
            self.__camera = None
            self.__camPeriod = None
            self.__isForcedDisabled = None
            self.__disabledCount = 0
            g_eventBus.removeListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onCameraForceDisable, EVENT_BUS_SCOPE.LOBBY)
            self.unregisterSettingsHandler(GAME.HANGAR_CAM_PERIOD)
            CallbackDelayer.destroy(self)
            HangarCameraSettingsListener.destroy(self)
            return

    def initialize(self, easingInTime, pitchParams, distParams, yawPeriod):
        self.__easingInTime = easingInTime
        self.__pitchParams = pitchParams
        self.__distParams = distParams
        self.__yawPeriod = yawPeriod
        self.__isInitialized = True

    def activate(self):
        if self.__isActive or not self.__isInitialized:
            return
        self._activate()
        self.__camPeriod = self.__getHangarCamPeriodSetting()
        self.setStartDelay(self.__camPeriod)
        self.__isActive = True

    def deactivate(self):
        if not self.__isActive:
            return
        self._deactivate(True)
        self.stopCallback(self.__updateIdleMovement)
        self.stopCallback(self.__updateEasingOut)
        BigWorld.removeAllIdleCallbacks()
        self.__isActive = False
        self.__isInitialized = False

    def isActive(self):
        return self.__isActive

    def setStartDelay(self, delay):
        BigWorld.removeAllIdleCallbacks()
        if delay > 0:
            BigWorld.addIdleCallbackForDelay(delay, self.__startCameraIdle, self.__stopCameraIdle)
        else:
            self.stopCallback(self.__updateIdleMovement)

    def _onHangarCamPeriodChanged(self):
        self.__camPeriod = self.__getHangarCamPeriodSetting()
        if self.__isForcedDisabled:
            return
        self.setStartDelay(self.__camPeriod)

    def __onCameraForceDisable(self, event):
        if not event.ctx['setIdle']:
            return
        isDisabled = event.ctx['isDisable']
        if isDisabled:
            self.__disabledCount += 1
        elif self.__disabledCount > 0:
            self.__disabledCount -= 1
        self.__isForcedDisabled = self.__disabledCount != 0
        if self.__isForcedDisabled:
            self.setStartDelay(0.0)
        else:
            self.setStartDelay(self.__camPeriod)

    def __getHangarCamPeriodSetting(self):
        return settings.convertSettingToFeatures(self.settingsCore.getSetting(GAME.HANGAR_CAM_PERIOD))

    def __startCameraIdle(self):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.IDLE_CAMERA, ctx={'started': True}), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.measureDeltaTime()
        self.__pitchParams.startValue = Math.Matrix(self.__camera.source).pitch
        self.__distParams.startValue = self.__camera.pivotMaxDist
        self.__setStartParams(self.__pitchParams)
        self.__setStartParams(self.__distParams)
        self.__currentIdleTime = 0.0
        self.__yawSpeed = 0.0
        self.delayCallback(0.0, self.__updateIdleMovement)

    def __updateIdleMovement(self):
        dt = min(self.measureDeltaTime(), self.MAX_DT)
        self.__currentIdleTime += dt
        cameraMatrix = Math.Matrix(self.__camera.source)
        if self.__yawPeriod > 0:
            yawDelta = 2.0 * math.pi * dt / self.__yawPeriod
            yawDelta *= 1.0 if self.__currentIdleTime > self.__easingInTime else self.__currentIdleTime / self.__easingInTime
        else:
            yawDelta = 0
        self.__yawSpeed = yawDelta / dt
        yaw = cameraMatrix.yaw + yawDelta
        pitch = self.__updateValue(self.__pitchParams)
        dist = self.__updateValue(self.__distParams)
        self.__pitchParams.speed = (pitch - cameraMatrix.pitch) / dt
        self.__distParams.speed = (dist - self.__camera.pivotMaxDist) / dt
        self.__setCameraParams(yaw, pitch, dist)

    def __updateValue(self, params):
        if params.period <= 0:
            return params.startValue
        return params.startValue + math_utils.easeOutQuad(self.__currentIdleTime, self.__sinValue(params) - params.startValue, self.__easingInTime) if self.__currentIdleTime < self.__easingInTime else self.__sinValue(params)

    def __sinValue(self, params):
        a = params.minValue
        b = params.maxValue - params.minValue
        c = 2.0 * math.pi * self.__currentIdleTime / params.period
        d = params.startTime
        result = a + b * (math.sin(c + d) * 0.5 + 0.5)
        return result

    def __setCameraParams(self, yaw, pitch, dist):
        mat = Math.Matrix()
        mat.setRotateYPR((yaw, pitch, 0.0))
        self.__camera.source = mat
        self.__camera.pivotMaxDist = dist

    def __updateEasingOut(self):
        dt = min(self.measureDeltaTime(), self.MAX_DT)
        self.__currentIdleTime += dt
        cameraMatrix = Math.Matrix(self.__camera.source)
        yaw = self.__easeOutValue(self.__yawSpeed, cameraMatrix.yaw, dt)
        pitch = self.__easeOutValue(self.__pitchParams.speed, cameraMatrix.pitch, dt)
        dist = self.__easeOutValue(self.__distParams.speed, self.__camera.pivotMaxDist, dt)
        self.__setCameraParams(yaw, pitch, dist)
        if self.__currentIdleTime < self.TIME_OUT:
            return 0.0
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.IDLE_CAMERA, ctx={'started': False}), scope=EVENT_BUS_SCOPE.DEFAULT)

    def __easeOutValue(self, startSpeed, prevValue, dt):
        a = -startSpeed / self.TIME_OUT
        v = startSpeed + self.__currentIdleTime * a
        result = prevValue + v * dt + a * dt * dt / 2.0
        return result

    def __setStartParams(self, params):
        a = params.minValue
        b = params.maxValue - params.minValue
        clampedValue = math_utils.clamp(params.minValue, params.maxValue, params.startValue)
        dArg = -1.0 + (clampedValue - a) * 2.0 / b if b != 0.0 else 0.0
        params.startTime = math.asin(dArg)

    def __stopCameraIdle(self):
        self.stopCallback(self.__updateIdleMovement)
        self.__currentIdleTime = 0.0
        self.delayCallback(0.0, self.__updateEasingOut)
