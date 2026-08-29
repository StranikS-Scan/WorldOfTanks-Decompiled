# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/gun_mechanics/shell_params_switcher/__init__.py
from __future__ import absolute_import
import typing
from constants import SERVER_TICK_LENGTH, SHELL_PARAMS_SWITCHER_STATE
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.mechanics.gun_mechanics.shell_params_switcher.mechanic_interfaces import IShellParamsSwitcherMechanicState, IShellParamsSwitcherComponentParams
from vehicles.mechanics.gun_mechanics.shell_params_switcher.mechanic_models import ShellParamsSwitcherMechanicState, ShellParamsSwitcherComponentParams, ShellParamsSwitcherAmmoState, ShellParamsSwitcherAmmoMode
from vehicles.mechanics.gun_mechanics.shell_params_switcher.mechanic_events import ShellParamsSwitcherStatesEvents
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
__all__ = ('IShellParamsSwitcherComponentParams', 'IShellParamsSwitcherMechanicState', 'ShellParamsSwitcherComponentParams', 'ShellParamsSwitcherMechanicState', 'ShellParamsSwitcherStatesEvents', 'DEFAULT_SHELL_PARAMS_SWITCHER_PARAMS', 'DEFAULT_SHELL_PARAMS_SWITCHER_STATE', 'createShellParamsSwitcherStatesEvents', 'ShellParamsSwitcherAmmoMode', 'ShellParamsSwitcherAmmoState')
DEFAULT_SHELL_PARAMS_SWITCHER_PARAMS = ShellParamsSwitcherComponentParams({})
DEFAULT_SHELL_PARAMS_SWITCHER_STATE = ShellParamsSwitcherMechanicState(state=SHELL_PARAMS_SWITCHER_STATE.NOT_CHARGED, endTime=0.0, isActive=False, lastActiveShotTimestamp=0.0, params=DEFAULT_SHELL_PARAMS_SWITCHER_PARAMS, shellCD=0)

@activateEventsContainer()
def createShellParamsSwitcherStatesEvents(component, tickInterval=SERVER_TICK_LENGTH, **_):
    return ShellParamsSwitcherStatesEvents(component, tickInterval)
