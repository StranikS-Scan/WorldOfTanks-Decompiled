# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_idle.py
import math
import BigWorld
import Math
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from AvatarInputHandler import mathUtils
from account_helpers.settings_core.settings_constants import GAME
from skeletons.account_helpers.settings_core import ISettingsCore
from helpers import dependency
import gui.hangar_cam_settings as settings
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.shared import g_eventBus, EVENT_BUS_SCOPE

class HangarCameraIdle(CallbackDelayer, TimeDeltaMeter):
    TIME_OUT = 0.8
    MAX_DT = 0.05
    settingsCore = dependency.descriptor(ISettingsCore)

    class IdleParams(object):

        def __init__(self):
            self.minValue = 0.0
            self.maxValue = 0.0
            self.period = 1.0
            self.startTime = 0.0
            self.startValue = 0.0
            self.speed = 0.0

    def __init__(self, camera):
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
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.onSpaceCreate += self.__onSpaceCreated
        g_hangarSpace.onSpaceDestroy += self.__onSpaceDestroy

    def destroy(self):
        from gui.shared.utils.HangarSpace import g_hangarSpace
        g_hangarSpace.onSpaceCreate -= self.__onSpaceCreated
        g_hangarSpace.onSpaceDestroy -= self.__onSpaceDestroy
        self.stopCallback(self.__updateIdleMovement)
        self.stopCallback(self.__updateEasingOut)
        BigWorld.removeAllIdleCallbacks()
        self.__pitchParams = None
        self.__distParams = None
        self.__camera = None
        CallbackDelayer.destroy(self)
        return

    def __onSpaceCreated(self):
        self.setStartDelay(settings.convertSettingToFeatures(self.settingsCore.getSetting(GAME.HANGAR_CAM_PERIOD)))
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged

    def __onSpaceDestroy(self, inited):
        if inited:
            self.settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def __onSettingsChanged(self, diff):
        if GAME.HANGAR_CAM_PERIOD in diff:
            self.setStartDelay(settings.convertSettingToFeatures(self.settingsCore.getSetting(GAME.HANGAR_CAM_PERIOD)))

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
        return params.startValue + mathUtils.easeOutQuad(self.__currentIdleTime, self.__sinValue(params) - params.startValue, self.__easingInTime) if self.__currentIdleTime < self.__easingInTime else self.__sinValue(params)

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
        g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.IDLE_CAMERA, ctx={'started': False}), scope=EVENT_BUS_SCOPE.DEFAULT)

    def __easeOutValue(self, startSpeed, prevValue, dt):
        a = -startSpeed / self.TIME_OUT
        v = startSpeed + self.__currentIdleTime * a
        result = prevValue + v * dt + a * dt * dt / 2.0
        return result

    def __setStartParams(self, params):
        a = params.minValue
        b = params.maxValue - params.minValue
        clampedValue = mathUtils.clamp(params.minValue, params.maxValue, params.startValue)
        dArg = -1.0 + (clampedValue - a) * 2.0 / b if b != 0.0 else 0.0
        params.startTime = math.asin(dArg)

    def __stopCameraIdle(self):
        self.stopCallback(self.__updateIdleMovement)
        self.__currentIdleTime = 0.0
        self.delayCallback(0.0, self.__updateEasingOut)
