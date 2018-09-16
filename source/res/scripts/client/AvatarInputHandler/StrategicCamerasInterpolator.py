# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/StrategicCamerasInterpolator.py
import BigWorld
import Math
from AvatarInputHandler import mathUtils
from helpers.CallbackDelayer import CallbackDelayer
_EASING_METHOD = mathUtils.easeInOutQuad
_INTERPOLATION_TIME = 0.2

class StrategicCamerasInterpolator(CallbackDelayer):

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__totalInterpolationTime = max(0.01, _INTERPOLATION_TIME)
        self.__elapsedTime = 0.0
        self.__easingMethod = _EASING_METHOD
        self.__prevTime = 0.0
        self.__initialState = None
        self.__finalState = None
        self.__initialFov = 0.0
        self.__finalFov = 0.0
        self.__cam = None
        return

    def enable(self, initialState, finalState, initialFov, finalFov):
        self.__prevTime = BigWorld.timeExact()
        if self.__elapsedTime > 0.0:
            self.__elapsedTime = self.__totalInterpolationTime - self.__elapsedTime
        self.__initialState = initialState
        self.__finalState = finalState
        self.__initialFov = initialFov
        self.__finalFov = finalFov
        self.__setupCamera()
        self.__cameraUpdate()
        self.delayCallback(0.0, self.__cameraUpdate)

    def __setupCamera(self):
        if self.__cam is None:
            self.__cam = BigWorld.CursorCamera()
        self.__cam.target = mathUtils.MatrixProviders.product(self.__finalState.target.a, Math.Matrix())
        self.__cam.source = Math.Matrix()
        self.__cam.pivotMaxDist = 0.0
        self.__cam.maxDistHalfLife = 0.01
        self.__cam.movementHalfLife = 0.0
        self.__cam.turningHalfLife = -1
        self.__cam.pivotPosition = self.__initialState.pivotPosition
        self.__cam.wg_applyParams()
        BigWorld.camera(self.__cam)
        BigWorld.projection().fov = self.__initialFov
        return

    def disable(self):
        self.__elapsedTime = 0.0
        self.stopCallback(self.__cameraUpdate)
        self.stopCallback(self.disable)
        BigWorld.camera(self.__finalState)
        self.__initialState = None
        self.__finalState = None
        self.__cam = None
        return

    def __cameraUpdate(self):
        currentTime = BigWorld.timeExact()
        self.__elapsedTime += currentTime - self.__prevTime
        self.__prevTime = currentTime
        interpolationCoefficient = self.__easingMethod(self.__elapsedTime, 1.0, self.__totalInterpolationTime)
        interpolationCoefficient = mathUtils.clamp(0.0, 1.0, interpolationCoefficient)
        iSource = self.__initialState.source
        iTarget = self.__initialState.target.b.translation
        iPivotPosition = self.__initialState.pivotPosition
        fSource = self.__finalState.source
        fTarget = self.__finalState.target.b.translation
        fPivotPosition = self.__finalState.pivotPosition
        self.__cam.source = Math.slerp(iSource, fSource, interpolationCoefficient)
        self.__cam.target.b.translation = mathUtils.lerp(iTarget, fTarget, interpolationCoefficient)
        self.__cam.pivotPosition = mathUtils.lerp(iPivotPosition, fPivotPosition, interpolationCoefficient)
        BigWorld.projection().fov = mathUtils.lerp(self.__initialFov, self.__finalFov, interpolationCoefficient)
        if self.__elapsedTime > self.__totalInterpolationTime:
            self.delayCallback(0.0, self.disable)
            return 10.0
