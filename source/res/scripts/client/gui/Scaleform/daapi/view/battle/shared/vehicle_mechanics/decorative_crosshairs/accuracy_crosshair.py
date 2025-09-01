# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/accuracy_crosshair.py
import typing
from events_handler import eventHandler
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.meta.AccuracyStackDecorativeCrosshairMeta import AccuracyStackDecorativeCrosshairMeta
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.vehicle_state_updater import VehicleStateUpdater
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from AccuracyStacksController import AccuracyStacksState

class AccuracyDecorativeCrosshair(AccuracyStackDecorativeCrosshairMeta, ComponentListener, IMechanicStatesListenerLogic):

    def __init__(self):
        super(AccuracyDecorativeCrosshair, self).__init__()
        self.__level = -1
        self.__progress = -1.0
        self.__speedThreshold = -1
        self.__isGainingActive = False
        self.__isSpeedLimitActive = False

    @eventHandler
    def onStatePrepared(self, state):
        self.__speedThreshold = state.speedThreshold
        self.as_setInitDataS(state.maxLevel, self.__speedThreshold)
        self.updateSpeedLimit(self.__isSpeedLimitActive, True)

    @eventHandler
    def onStateObservation(self, state):
        self.__update(state)

    @eventHandler
    def onStateTick(self, state):
        self.__update(state)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.ACCURACY_STACKS, self), VehicleMechanicStatesUpdater(VehicleMechanic.ACCURACY_STACKS, self), VehicleStateUpdater(self)]

    def updateSpeedLimit(self, value, forced=False):
        if self.__isSpeedLimitActive != value or forced:
            self.__isSpeedLimitActive = value
            self.as_setSpeedLimitActiveS(self.__isSpeedLimitActive)

    def onVehicleStateUpdated(self, stateID, value):
        if stateID != VEHICLE_VIEW_STATE.SPEED:
            return
        isSpeedLimitActive = abs(value) >= self.__speedThreshold
        self.updateSpeedLimit(isSpeedLimitActive)

    def __update(self, state):
        if self.__level != state.level or self.__progress != state.progress:
            self.__level = state.level
            self.__progress = state.progress
            self.as_setStacksProgresS(self.__level, self.__progress)
        if self.__isGainingActive != state.isGainingActive:
            self.__isGainingActive = state.isGainingActive
            self.as_setGainingActiveS(self.__isGainingActive)
