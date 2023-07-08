# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/auto_shoot_guns/auto_burst_predictor.py
import logging
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState, AutoShootPredictionState, CLIP_MAX_INTERVAL
from constants import SERVER_TICK_LENGTH
from Event import Event, EventManager
from gui.battle_control.arena_info.interfaces import IAutoShootGunController
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getBurstActivationTimeout, getBurstDeactivationTimeout
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import autoCooldown, checkPredictionStates
from helpers.CallbackDelayer import CallbackDelayer
_logger = logging.getLogger(__name__)
_NOT_PREDICTED_TIME = -1

class BurstPredictor(IAutoShootGunController.IBurstPredictor, CallbackDelayer):
    __slots__ = ('__isShootingPossible', '__needDeactivation', '__predActivationTime', '__state', '__em', 'onStateChanged', 'onStateUpdated')

    def __init__(self):
        super(BurstPredictor, self).__init__()
        self.__needDeactivation = False
        self.__isShootingPossible = True
        self.__predActivationTime = _NOT_PREDICTED_TIME
        self.__state = AutoShootPredictionState.NOT_ACTIVE
        self.__em = EventManager()
        self.onStateChanged = Event(self.__em)
        self.onStateUpdated = Event(self.__em)

    def destroy(self):
        self.__clear()
        self.__em.clear()
        self.__state = AutoShootPredictionState.NOT_ACTIVE
        super(BurstPredictor, self).destroy()

    def isShootingPossible(self):
        return self.__isShootingPossible and not self.__needDeactivation

    def isShootingProcess(self):
        return self.__state in AutoShootPredictionState.COOLDOWNABLE

    def canConfirmShooting(self):
        return self.__state in AutoShootPredictionState.CONFIRMABLE

    def getPredictionState(self):
        return self.__state

    def setShootingPossible(self, isShootingPossible):
        self.__isShootingPossible = isShootingPossible

    @checkPredictionStates(states=AutoShootPredictionState.COOLDOWNABLE)
    def activateCooldown(self):
        self.__clear()
        self.clearCallbacks()
        self.__invalidateState(AutoShootPredictionState.COOLDOWN)
        self.delayCallback(CLIP_MAX_INTERVAL, self.__cooldownShooting)

    @checkPredictionStates(states=(AutoShootPredictionState.NOT_ACTIVE,))
    def activateShooting(self):
        activationTimeout = getBurstActivationTimeout()
        self.__invalidateState(AutoShootPredictionState.ACTIVATION)
        self.delayCallback(activationTimeout, self.__activateShooting)
        self.__predActivationTime = BigWorld.time() + activationTimeout

    @checkPredictionStates(states=AutoShootPredictionState.DISABLEABLE)
    def deactivateShooting(self):
        newState = AutoShootPredictionState.DEACTIVATION
        deactivationTimeout = getBurstDeactivationTimeout()
        if self.__state == AutoShootPredictionState.ACTIVATION:
            newState = AutoShootPredictionState.ACTIVATION
            activationTimeout = self.__predActivationTime - BigWorld.time()
            deactivationTimeout = max(deactivationTimeout, activationTimeout + 0.01)
        self.__invalidateState(newState)
        self.delayCallback(deactivationTimeout, self.__deactivateShooting)

    def killShooting(self):
        self.__clear()
        self.clearCallbacks()
        self.__invalidateState(AutoShootPredictionState.NOT_ACTIVE)

    def synchronizeShooting(self, state):
        isActive = state in AutoShootGunState.SHOOTING_STATES
        if isActive and self.__state == AutoShootPredictionState.ACTIVATION:
            self.stopCallback(self.__activateShooting)
            self.__isShootingPossible = True
            self.__activateShooting()
        elif not isActive and self.__state == AutoShootPredictionState.DEACTIVATION:
            self.stopCallback(self.__deactivateShooting)
            self.activateCooldown()

    def __clear(self):
        self.__needDeactivation = False
        self.__isShootingPossible = True
        self.__predActivationTime = _NOT_PREDICTED_TIME

    @autoCooldown
    @checkPredictionStates(states=(AutoShootPredictionState.ACTIVATION,))
    def __activateShooting(self):
        newState = AutoShootPredictionState.ACTIVE
        self.__predActivationTime = _NOT_PREDICTED_TIME
        if self.hasDelayedCallback(self.__deactivateShooting):
            newState = AutoShootPredictionState.DEACTIVATION
        self.__invalidateState(newState)
        self.delayCallback(SERVER_TICK_LENGTH, self.__invalidateShooting)

    @checkPredictionStates(states=(AutoShootPredictionState.COOLDOWN,))
    def __cooldownShooting(self):
        self.__invalidateState(AutoShootPredictionState.NOT_ACTIVE)
        self.clearCallbacks()

    @checkPredictionStates(states=(AutoShootPredictionState.DEACTIVATION,))
    def __deactivateShooting(self):
        self.__needDeactivation = True

    @autoCooldown
    @checkPredictionStates(states=AutoShootPredictionState.ACTIVATED)
    def __invalidateShooting(self):
        self.delayCallback(SERVER_TICK_LENGTH, self.__invalidateShooting)
        self.__invalidateState(self.__state)

    def __invalidateState(self, newState):
        isStateChanged = self.__state != newState
        self.__state = newState
        self.onStateUpdated(newState)
        if isStateChanged:
            _logger.debug('BurstPredictor new state %s %s', AutoShootPredictionState.NAMES[newState], BigWorld.time())
            self.onStateChanged(newState)


class BurstReplayPredictor(BurstPredictor):

    def activateCooldown(self):
        pass

    def activateShooting(self):
        pass

    def killShooting(self):
        pass

    def synchronizeShooting(self, state):
        pass


def createBurstPredictor(setup):
    return BurstReplayPredictor() if setup.isReplayPlaying else BurstPredictor()
