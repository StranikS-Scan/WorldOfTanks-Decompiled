# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/hangar/presenters/comp7_light_optional_devices_assistant_presenter.py
import typing
from frameworks.state_machine import visitor
from gui.impl.lobby.hangar.presenters.optional_devices_assistant_presenter import _OptionalDevicesObserver, OptionalDevicesAssistantPresenter
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frameworks.state_machine import State

class _Comp7LightOptionalDevicesObserver(_OptionalDevicesObserver):

    def isObservingState(self, state):
        from comp7_light.gui.impl.lobby.hangar.states import Comp7LightEquipmentLoadoutState
        lsm = state.getMachine()
        return visitor.isDescendantOf(state, lsm.getStateByCls(Comp7LightEquipmentLoadoutState)) or state.getStateID() == Comp7LightEquipmentLoadoutState.STATE_ID


class Comp7LightOptionalDevicesAssistantPresenter(OptionalDevicesAssistantPresenter):
    _STATES_OBSERVER = _Comp7LightOptionalDevicesObserver
