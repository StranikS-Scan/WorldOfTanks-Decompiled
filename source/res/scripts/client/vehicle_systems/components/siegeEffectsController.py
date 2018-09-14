# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/siegeEffectsController.py
from AvatarInputHandler.cameras import ImpulseReason
import BigWorld
import Math
import svarog_script.py_component
from constants import VEHICLE_SIEGE_STATE
from vehicle_systems.tankStructure import TankNodeNames

class SiegeEffectsController(svarog_script.py_component.Component):
    SIEGE_TIMEOUT = 2.0
    SIEGE_IMPULSE = 0.1

    def __init__(self, appearance):
        self.__appearance = appearance
        self.__effectManager = appearance.customEffectManager
        self.__siegeTimeOut = 0.0
        self.__siegeInProgress = 0
        self.__state = VEHICLE_SIEGE_STATE.DISABLED

    def destroy(self):
        self.__effectManager = None
        self.__appearance = None
        return

    def __shake(self):
        matrix = Math.Matrix(self.__appearance.compoundModel.matrix)
        impulseDir = -matrix.applyToAxis(2)
        self.__appearance.receiveShotImpulse(impulseDir, self.SIEGE_IMPULSE)

    def onSiegeStateChanged(self, newState):
        if self.__state != newState:
            if newState == VEHICLE_SIEGE_STATE.SWITCHING_ON:
                self.__siegeInProgress = 1
                self.__siegeTimeOut = self.SIEGE_TIMEOUT
                self.__shake()
            elif newState == VEHICLE_SIEGE_STATE.ENABLED:
                self.__siegeInProgress = 0
            elif newState == VEHICLE_SIEGE_STATE.SWITCHING_OFF:
                self.__siegeInProgress = 1
                self.__siegeTimeOut = self.SIEGE_TIMEOUT
                self.__shake()
            elif newState == VEHICLE_SIEGE_STATE.DISABLED:
                self.__siegeInProgress = 0
            self.__state = newState

    def tick(self, dt):
        if self.__siegeTimeOut > 0.0:
            self.__siegeTimeOut -= dt
        self.__effectManager.variables['siegeStart'] = 1 if self.__siegeTimeOut > 0.0 else 0
        self.__effectManager.variables['siegeProgress'] = self.__siegeInProgress
