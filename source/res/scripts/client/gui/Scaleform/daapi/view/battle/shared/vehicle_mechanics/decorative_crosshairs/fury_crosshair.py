# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/fury_crosshair.py
import typing
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.FuryDecorativeCrosshairMeta import FuryDecorativeCrosshairMeta
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events.events_listener import ComponentListener
if typing.TYPE_CHECKING:
    from typing import List
    from BattleFuryController import BattleFuryState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class FuryDecorativeCrosshair(FuryDecorativeCrosshairMeta, ComponentListener, IMechanicStatesListenerLogic):

    def __init__(self):
        super(FuryDecorativeCrosshair, self).__init__()
        self.__level = -1
        self.__progress = -1.0

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateState(state)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.BATTLE_FURY, self), VehicleMechanicStatesUpdater(VehicleMechanic.BATTLE_FURY, self)]

    def __invalidateState(self, state):
        if state.level != self.__level or state.progress != self.__progress:
            self.__level = state.level
            self.__progress = state.progress
            self.as_setGunStackProgressS(self.__level, self.__progress)
