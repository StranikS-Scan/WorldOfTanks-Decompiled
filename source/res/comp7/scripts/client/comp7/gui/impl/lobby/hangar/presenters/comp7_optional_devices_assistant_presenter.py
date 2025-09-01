# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/presenters/comp7_optional_devices_assistant_presenter.py
import typing
from frameworks.state_machine import visitor
from gui.impl.lobby.hangar.presenters.optional_devices_assistant_presenter import _OptionalDevicesObserver, OptionalDevicesAssistantPresenter
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frameworks.state_machine import State

class _Comp7OptionalDevicesObserver(_OptionalDevicesObserver):

    def isObservingState(self, state):
        from comp7.gui.impl.lobby.hangar.states import Comp7EquipmentLoadoutState
        lsm = state.getMachine()
        return visitor.isDescendantOf(state, lsm.getStateByCls(Comp7EquipmentLoadoutState)) or state.getStateID() == Comp7EquipmentLoadoutState.STATE_ID


class Comp7OptionalDevicesAssistantPresenter(OptionalDevicesAssistantPresenter):
    _STATES_OBSERVER = _Comp7OptionalDevicesObserver
