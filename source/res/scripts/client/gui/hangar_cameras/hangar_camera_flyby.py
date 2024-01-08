# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_cameras/hangar_camera_flyby.py
import logging
import math
import CGF
import Math
from shared_utils import first
import math_utils
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer, TimeDeltaMeter
from skeletons.gui.shared.utils import IHangarSpace
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
_logger = logging.getLogger(__name__)
_MAX_DT = 0.05

@registerComponent
class FlyByComponent(object):
    editorTitle = 'Camera Flyby'
    category = 'Camera'
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    pitch = ComponentProperty(type=CGFMetaTypes.FLOAT, value=-30, editorName='Goal Pitch')
    distance = ComponentProperty(type=CGFMetaTypes.FLOAT, value=6.5, editorName='Goal Distance')
    duration = ComponentProperty(type=CGFMetaTypes.FLOAT, value=12, editorName='Duration')


class HangarCameraFlyby(object):
    __slots__ = ('__camera', '__callback', '__callbackDelayer', '__timeDeltaMeter', '__isActive', '__timeFromStart', '__yawEasing', '__pitchEasing', '__distEasing')
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, camera):
        super(HangarCameraFlyby, self).__init__()
        self.__callbackDelayer = CallbackDelayer()
        self.__timeDeltaMeter = TimeDeltaMeter()
        self.__camera = camera
        self.__callback = None
        self.__isActive = False
        self.__timeFromStart = 0.0
        self.__yawEasing = None
        self.__pitchEasing = None
        self.__distEasing = None
        return

    @property
    def isActive(self):
        return self.__isActive

    def fini(self):
        self.deactivate()
        self.__callbackDelayer.clearCallbacks()
        self.__callbackDelayer = None
        self.__timeDeltaMeter = None
        return

    def activate(self, callback=None):
        if self.__isActive:
            _logger.warning('Could not activate fly-by, it is already active')
            return
        else:
            flybyComponent = self.__findFlybyComponent()
            if flybyComponent is None:
                _logger.warning('Please define FlybyComponent to start fly-by')
                return
            self.__isActive = True
            self.__callback = callback
            self.__camera.enableCollisions(False)
            camMatrix = Math.Matrix(self.__camera.source)
            duration = flybyComponent.duration
            self.__yawEasing = _YawEasing(camMatrix.yaw, camMatrix.yaw, duration)
            self.__pitchEasing = _PitchDistEasing(camMatrix.pitch, math.radians(flybyComponent.pitch), duration)
            self.__distEasing = _PitchDistEasing(self.__camera.pivotMaxDist, flybyComponent.distance, duration)
            self.__timeFromStart = 0.0
            self.__timeDeltaMeter.measureDeltaTime()
            self.__callbackDelayer.delayCallback(0.0, self.__update)
            return

    def deactivate(self):
        self.__callbackDelayer.stopCallback(self.__update)
        self.__isActive = False
        self.__camera.enableCollisions(True)
        self.__yawEasing = None
        self.__pitchEasing = None
        self.__distEasing = None
        if self.__callback is not None:
            self.__callback()
            self.__callback = None
        return

    def __update(self):
        flybyComponent = self.__findFlybyComponent()
        if flybyComponent is None:
            _logger.warning('Could not update fly-by, FlybyComponent is absent')
            self.deactivate()
            return
        else:
            dt = min(self.__timeDeltaMeter.measureDeltaTime(), _MAX_DT)
            self.__timeFromStart += dt
            if self.__timeFromStart <= flybyComponent.duration:
                time = min(self.__timeFromStart + dt, flybyComponent.duration)
                yaw = self.__yawEasing.update(time)
                pitch = self.__pitchEasing.update(time)
                dist = self.__distEasing.update(time)
                self.__camera.source = math_utils.createRotationMatrix((yaw, pitch, 0.0))
                self.__camera.pivotMaxDist = dist
            else:
                self.deactivate()
            if self.__isActive:
                self.__callbackDelayer.delayCallback(0.0, self.__update)
            return

    def __findFlybyComponent(self):
        from cgf_components.hangar_camera_manager import CurrentCameraObject
        currentCameraQuery = CGF.Query(self.__hangarSpace.spaceID, (CGF.GameObject, CurrentCameraObject))
        if not currentCameraQuery.empty():
            gameObject, _ = first(currentCameraQuery)
            return gameObject.findComponentByType(FlyByComponent)
        else:
            return None


class _FlybyEasing(object):

    def __init__(self, start, goal, duration):
        self._start = start
        self._end = goal
        self._duration = duration

    def update(self, time):
        raise NotImplementedError


class _PitchDistEasing(_FlybyEasing):

    def update(self, time):
        halfDuration = self._duration * 0.5
        return math_utils.easeInCubic(time, self._end - self._start, halfDuration) + self._start if time <= halfDuration else math_utils.easeOutCubic(time - halfDuration, self._start - self._end, halfDuration) + self._end


class _YawEasing(_FlybyEasing):

    def update(self, time):
        return math_utils.easeInOutCubic(time, math.radians(360.0), self._duration) + self._start
