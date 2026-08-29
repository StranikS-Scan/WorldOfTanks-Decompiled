# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/shell_params_switcher_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from constants import SHELL_PARAMS_SWITCHER_STATE
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.ShellParamsSwitcherWidgetMeta import ShellParamsSwitcherWidgetMeta
from gui.Scaleform.genConsts.SHELL_PARAMS_SWITCHER_WIDGET_CONSTS import SHELL_PARAMS_SWITCHER_WIDGET_CONSTS
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.gun_mechanics.shell_params_switcher import IShellParamsSwitcherMechanicState
_MECHANIC_STATE_UI_MAP = {(SHELL_PARAMS_SWITCHER_STATE.NOT_CHARGED, False): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.READY,
 (SHELL_PARAMS_SWITCHER_STATE.CHARGED, False): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.ACTIVE,
 (SHELL_PARAMS_SWITCHER_STATE.SWITCHING_ON, False): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.SWITCHING_ON,
 (SHELL_PARAMS_SWITCHER_STATE.SWITCHING_OFF, False): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.SWITCHING_OFF,
 (SHELL_PARAMS_SWITCHER_STATE.NOT_CHARGED, True): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.DISABLED,
 (SHELL_PARAMS_SWITCHER_STATE.CHARGED, True): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.DISABLED,
 (SHELL_PARAMS_SWITCHER_STATE.SWITCHING_ON, True): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.SWITCHING_CRIT,
 (SHELL_PARAMS_SWITCHER_STATE.SWITCHING_OFF, True): SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.SWITCHING_CRIT}

def _getWidgetState(state):
    return SHELL_PARAMS_SWITCHER_WIDGET_CONSTS.EMPTY if state.isNoAmmo() else _MECHANIC_STATE_UI_MAP[state.baseState, state.isCritState()]


class ShellParamsSwitcherWidget(ShellParamsSwitcherWidgetMeta, ContainersListener, IMechanicStatesListenerLogic):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateTick(self, state):
        if state.state in SHELL_PARAMS_SWITCHER_STATE.SWITCHING_STATES:
            self.as_setTimeS(state.timeLeft())

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.SHELL_PARAMS_SWITCHER, self), VehicleMechanicStatesUpdater(VehicleMechanic.SHELL_PARAMS_SWITCHER, self), HotKeysViewUpdater(list(self._HOT_KEY_MAP), self)]

    def __invalidateState(self, state, isInstantly=False):
        self.as_setStateS(_getWidgetState(state), isInstantly)
        self.as_setTimeS(state.timeLeft())
        self.as_setParamsTypeS(state.mechanicSubtype)
