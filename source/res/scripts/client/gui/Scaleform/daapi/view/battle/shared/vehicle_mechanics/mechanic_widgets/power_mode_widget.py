# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/power_mode_widget.py
import typing
from constants import POWER_MODE_STATE
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.PowerWidgetMeta import PowerWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from PowerModeController import PowerModeState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class PowerModeMechanicWidget(PowerWidgetMeta, ComponentListener, IMechanicStatesListenerLogic):
    _POWER_MODE_UI_STATES = {POWER_MODE_STATE.NOT_ACTIVE: MECHANICS_WIDGET_CONST.PREPARING,
     POWER_MODE_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     POWER_MODE_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     POWER_MODE_STATE.MAX_MODE: MECHANICS_WIDGET_CONST.ACTIVE}

    def __init__(self):
        super(PowerModeMechanicWidget, self).__init__()
        self.__progress = -1.0

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateAll(newState)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(state)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.POWER_MODE, self), VehicleMechanicStatesUpdater(VehicleMechanic.POWER_MODE, self)]

    def __invalidateAll(self, state, isInstantly=False):
        self.as_setStateS(self._POWER_MODE_UI_STATES[state.state], isInstantly)
        self.__invalidateProgress(state=state, forced=True)

    def __invalidateProgress(self, state, forced=False):
        if forced or state.progress != self.__progress:
            self.__progress = state.progress
            self.as_setProgressS(self.__progress)
