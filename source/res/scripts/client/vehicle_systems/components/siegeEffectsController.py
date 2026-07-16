# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/siegeEffectsController.py
import CGF
import Math
from constants import VEHICLE_SIEGE_STATE
from cgf_script.registration import registerComponent

@registerComponent
class SiegeEffectsController(object):
    domain = CGF.Domain.ClientEditor
    userVisible = False
    vseVisible = False
    SIEGE_IMPULSE = 0.1
    SIEGE_START_NAME = 'siegeStart'
    SIEGE_PROGRESS_NAME = 'siegeProgress'

    def __init__(self, appearance, hasSwitchImpulse):
        self.__appearance = appearance
        self.__effectManager = appearance.customEffectManager
        self.__hasSwitchImpulse = hasSwitchImpulse
        self.__state = VEHICLE_SIEGE_STATE.DISABLED
        self.__pendingStateChanges = 0

    def destroy(self):
        self.__effectManager = None
        self.__appearance = None
        return

    def __shake(self):
        if self.__hasSwitchImpulse:
            matrix = Math.Matrix(self.__appearance.compoundModel.matrix)
            impulseDir = -matrix.applyToAxis(2)
            self.__appearance.receiveShotImpulse(impulseDir, self.SIEGE_IMPULSE)

    def onSiegeStateChanged(self, newState):
        if self.__state == newState:
            return
        else:
            isTransition = None
            if newState == VEHICLE_SIEGE_STATE.SWITCHING_ON:
                isTransition = 1
                self.__shake()
            elif VEHICLE_SIEGE_STATE.isEnabled(newState):
                isTransition = 0
            elif newState == VEHICLE_SIEGE_STATE.SWITCHING_OFF:
                isTransition = 1
                self.__shake()
            elif newState == VEHICLE_SIEGE_STATE.DISABLED:
                isTransition = 0
            self.__state = newState
            if isTransition is not None:
                if self.__pendingStateChanges > 0:
                    self.__effectManager.scheduleResetForEffect(self.SIEGE_START_NAME)
                    self.__effectManager.scheduleResetForEffect(self.SIEGE_PROGRESS_NAME)
                self.__pendingStateChanges += 1
                self.__effectManager.variables[self.SIEGE_START_NAME] = isTransition
                self.__effectManager.variables[self.SIEGE_PROGRESS_NAME] = isTransition
            return

    def tick(self):
        self.__pendingStateChanges = 0
