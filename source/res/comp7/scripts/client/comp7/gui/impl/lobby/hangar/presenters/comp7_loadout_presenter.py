# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/hangar/presenters/comp7_loadout_presenter.py
import typing
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import LoadoutPresenter, _LoadoutStatesObserver
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_component import ViewComponent

class _Comp7LoadoutStatesObserver(_LoadoutStatesObserver):

    @property
    def _stateID(self):
        from comp7.gui.impl.lobby.hangar.states import Comp7LoadoutState
        return Comp7LoadoutState.STATE_ID


class Comp7LoadoutPresenter(LoadoutPresenter):
    _STATES_OBSERVER = _Comp7LoadoutStatesObserver

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : Comp7ShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : ConsumablesPresenter(self._vehInteractingItem)}


class Comp7ShellsPresenter(ShellsPresenter):

    @property
    def isShellState(self):
        from comp7.gui.impl.lobby.hangar.states import Comp7ShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(Comp7ShellsLoadoutState).isEntered()
