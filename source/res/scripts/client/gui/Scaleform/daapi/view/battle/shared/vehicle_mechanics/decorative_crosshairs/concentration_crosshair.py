# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/concentration_crosshair.py
import typing
from constants import CONCENTRATION_MODE_STATE
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.ConcentrationDecorativeCrosshairMeta import ConcentrationDecorativeCrosshairMeta
from gui.Scaleform.genConsts.DECORATIVE_CROSSHAIR_CONSTS import DECORATIVE_CROSSHAIR_CONSTS as _DECORATIVE_CONSTS
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from ConcentrationModeComponent import ConcentrationModeState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class ConcentrationDecorativeCrosshair(ConcentrationDecorativeCrosshairMeta, ComponentListener, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateAll(newState)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.CONCENTRATION_MODE, self), VehicleMechanicStatesUpdater(VehicleMechanic.CONCENTRATION_MODE, self)]

    def __invalidateAll(self, state, isInstantly=False):
        isActive = state.state == CONCENTRATION_MODE_STATE.ACTIVE
        self.as_setStateS(_DECORATIVE_CONSTS.SHOW_STATE if isActive else _DECORATIVE_CONSTS.HIDE_STATE, isInstantly)
