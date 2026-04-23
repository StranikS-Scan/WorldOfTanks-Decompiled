# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/low_charge_shot/public/mechanic_events.py
from __future__ import absolute_import
import typing
import BattleReplay
import BigWorld
from constants import LowChargeShotVisualState
from events_handler import eventHandler
from vehicles.components.component_events import VehicleComponentEventsCoreIntegration
from vehicles.mechanics.mechanic_states import MechanicStatesEvents, IMechanicStatesListenerLogic
from cgf_events import gun_events
if typing.TYPE_CHECKING:
    from vehicles.mechanics.gun_mechanics.low_charge_shot.public import LowChargeShotPublicMechanicState
_INSTANT_ANIMATION_TIMESTAMP = -10.0

def _makeEvent(quickShot=None, fullShot=None, fullShotChangeTime=None):
    event = {}
    if quickShot is not None:
        event['vehicle/gun/lowChargeShot/quickShot'] = quickShot
    if fullShot is not None:
        event['vehicle/gun/lowChargeShot/fullShot'] = fullShot
    if fullShotChangeTime is not None:
        event['vehicle/gun/lowChargeShot/fullShotChangeTime'] = fullShotChangeTime
    return event


class LowChargeShotPublicStatesEvents(MechanicStatesEvents):

    def _createCoreIntegration(self):
        return LowChargeShotPublicStatesCoreIntegration(self, self._getComponent())


class LowChargeShotPublicStatesCoreIntegration(VehicleComponentEventsCoreIntegration, IMechanicStatesListenerLogic):

    def __init__(self, events, component):
        super(LowChargeShotPublicStatesCoreIntegration, self).__init__(events, component)
        self.__visualState = LowChargeShotVisualState.NONE
        self.__fullShotAnimationTimerID = None
        self.__fullShotAnimationEventHappened = None
        return

    @eventHandler
    def onStatePrepared(self, state):
        if not BattleReplay.g_replayCtrl.isPlaying:
            postLowChargeShotInitialEvent(state.visualState, self._spaceID, self._vehicleID, self._slotName)
        self.__visualState = state.visualState

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__postLowChargeShotChangedEvent(newState)
        self.__visualState = newState.visualState

    @eventHandler
    def onEventsContainerDestroy(self, events):
        if self.__fullShotAnimationTimerID is not None:
            BigWorld.cancelCallback(self.__fullShotAnimationTimerID)
            self.__fullShotAnimationTimerID = None
        super(LowChargeShotPublicStatesCoreIntegration, self).onEventsContainerDestroy(events)
        return

    def __postLowChargeShotChangedEvent(self, state):
        if state.visualState == self.__visualState:
            return
        else:
            event = None
            if self.__visualState == LowChargeShotVisualState.NONE:
                if state.visualState == LowChargeShotVisualState.QUICK_SHOT:
                    event = _makeEvent(quickShot=True)
                elif state.visualState == LowChargeShotVisualState.FULL_SHOT:
                    event = _makeEvent(fullShot=True, fullShotChangeTime=state.fullShotChangeTime)
            elif self.__visualState == LowChargeShotVisualState.QUICK_SHOT:
                if state.visualState == LowChargeShotVisualState.FULL_SHOT:
                    event = _makeEvent(quickShot=False, fullShot=True, fullShotChangeTime=state.fullShotChangeTime)
                    self.__fullShotAnimationTimerID = BigWorld.callback(state.almostFinishedTime, self.__fullShotAnimationEnd)
                elif state.visualState == LowChargeShotVisualState.NONE:
                    event = _makeEvent(quickShot=False)
            elif self.__visualState == LowChargeShotVisualState.FULL_SHOT:
                if state.visualState == LowChargeShotVisualState.NONE:
                    if self.__fullShotAnimationTimerID is None:
                        event = _makeEvent(fullShot=False, fullShotChangeTime=state.fullShotChangeTime)
                    else:
                        self.__fullShotAnimationEventHappened = state.fullShotChangeTime
            if event is not None:
                gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, event)
            return

    def __fullShotAnimationEnd(self):
        self.__fullShotAnimationTimerID = None
        if self.__fullShotAnimationEventHappened is not None:
            event = _makeEvent(fullShot=False, fullShotChangeTime=self.__fullShotAnimationEventHappened)
            gun_events.postVehicularVariablesChangedEvent(self._spaceID, self._vehicleID, self._slotName, event)
        self.__fullShotAnimationEventHappened = None
        return


def postLowChargeShotInitialEvent(visualState, spaceID, vehicleID, slotName):
    if visualState == LowChargeShotVisualState.QUICK_SHOT:
        event = _makeEvent(quickShot=True, fullShot=False, fullShotChangeTime=_INSTANT_ANIMATION_TIMESTAMP)
    elif visualState == LowChargeShotVisualState.FULL_SHOT:
        event = _makeEvent(quickShot=False, fullShot=True, fullShotChangeTime=_INSTANT_ANIMATION_TIMESTAMP)
    else:
        event = _makeEvent(quickShot=False, fullShot=False, fullShotChangeTime=_INSTANT_ANIMATION_TIMESTAMP)
    gun_events.postVehicularVariablesChangedEvent(spaceID, vehicleID, slotName, event)
