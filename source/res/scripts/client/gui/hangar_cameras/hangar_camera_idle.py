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

class HangarCameraIdleController(HangarCameraSettingsListener):

    def __init__(self):
        super(HangarCameraIdleController, self).__init__()
        self.registerSettingHandler(GAME.HANGAR_CAM_PERIOD, self._onHangarCamPeriodChanged)
        self.__camPeriod = 0
        self.__isForcedDisabled = False

    def destroy(self):
        self.__camPeriod = None
        self.__isForcedDisabled = None
        self.unregisterSettingsHandler(GAME.HANGAR_CAM_PERIOD)
        super(HangarCameraIdleController, self).destroy()
        return

    def _onSpaceCreated(self):
        super(HangarCameraIdleController, self)._onSpaceCreated()
        g_eventBus.addListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onCameraForceDisable, EVENT_BUS_SCOPE.LOBBY)
        self.__camPeriod = self.__getHangarCamPeriodSetting()
        self._setStartDelay(self.__camPeriod)

    def _onSpaceDestroy(self, inited):
        super(HangarCameraIdleController, self)._onSpaceDestroy(inited)
        self.__isForcedDisabled = False
        if inited:
            g_eventBus.removeListener(CameraRelatedEvents.FORCE_DISABLE_IDLE_PARALAX_MOVEMENT, self.__onCameraForceDisable, EVENT_BUS_SCOPE.LOBBY)

    def _setStartDelay(self, delay):
        pass

    def __getHangarCamPeriodSetting(self):
        return settings.convertSettingToFeatures(self.settingsCore.getSetting(GAME.HANGAR_CAM_PERIOD))

    def _onHangarCamPeriodChanged(self):
        self.__camPeriod = self.__getHangarCamPeriodSetting()
        if self.__isForcedDisabled:
            return
        self._setStartDelay(self.__camPeriod)

    def __onCameraForceDisable(self, event):
        self.__isForcedDisabled = event.ctx['isDisable']
        if self.__isForcedDisabled:
            self._setStartDelay(0.0)
        else:
            self._setStartDelay(self.__camPeriod)


class HangarCameraIdle(HangarCameraIdleController, CallbackDelayer, TimeDeltaMeter):
    TIME_OUT = 0.8
    MAX_DT = 0.05
    MIN_DT = 0.001

    class IdleParams(object):

        def __init__(self):
            self.minValue = 0.0
            self.maxValue = 0.0
            self.period = 1.0
            self.startTime = 0.0
            self.startValue = 0.0
            self.speed = 0.0

    def __init__(self, camera):
        HangarCameraIdleController.__init__(self)
        CallbackDelayer.__init__(self)
        TimeDeltaMeter.__init__(self)
        self.__camera = camera
        self.__pitchParams = self.IdleParams()
        self.__distParams = self.IdleParams()
        self.__yawPeriod = 1.0
        self.__yawSpeed = 0.0
        from gui.ClientHangarSpace import hangarCFG
        cfg = hangarCFG()
        self.__easingInTime = cfg['cam_idle_easing_in_time']
        self.__pitchParams.minValue = cfg['cam_idle_pitch_constr'][0]
        self.__pitchParams.maxValue = cfg['cam_idle_pitch_constr'][1]
        self.__pitchParams.period = cfg['cam_idle_pitch_period']
        self.__distParams.minValue = cfg['cam_idle_dist_constr'][0]
        self.__distParams.maxValue = cfg['cam_idle_dist_constr'][1]
        self.__distParams.period = cfg['cam_idle_dist_period']
        self.__yawPeriod = cfg['cam_idle_yaw_period']

    def destroy(self):
        self.stopCallback(self.__updateIdleMovement)
        self.stopCallback(self.__updateEasingOut)
        BigWorld.removeAllIdleCallbacks()
        self.__pitchParams = None
        self.__distParams = None
        self.__camera = None
        CallbackDelayer.destroy(self)
        HangarCameraIdleController.destroy(self)
        return

    def _setStartDelay(self, delay):
        self.setStartDelay(delay)

    def setStartDelay(self, delay):
        BigWorld.removeAllIdleCallbacks()
        if delay > 0:
            BigWorld.addIdleCallbackForDelay(delay, self.__startCameraIdle, self.__stopCameraIdle)

    def __startCameraIdle(self):
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.IDLE_CAMERA, ctx={'started': True}), scope=EVENT_BUS_SCOPE.DEFAULT)
        self.measureDeltaTime()
        self.__pitchParams.startValue = Math.Matrix(self.__camera.source).pitch
        self.__distParams.startValue = self.__camera.pivotMaxDist
        self.__setStartParams(self.__pitchParams)
        self.__setStartParams(self.__distParams)
        self.__currentIdleTime = 0.0
        self.__yawSpeed = 0.0
        self.delayCallback(self.MIN_DT, self.__updateIdleMovement)

    def __updateIdleMovement(self):
        dt = min(self.measureDeltaTime(), self.MAX_DT)
        self.__currentIdleTime += dt
        if dt < self.MIN_DT:
            return
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
            return
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.IDLE_CAMERA, ctx={'started': False}), scope=EVENT_BUS_SCOPE.DEFAULT)
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
        self.delayCallback(self.MIN_DT, self.__updateEasingOut)
