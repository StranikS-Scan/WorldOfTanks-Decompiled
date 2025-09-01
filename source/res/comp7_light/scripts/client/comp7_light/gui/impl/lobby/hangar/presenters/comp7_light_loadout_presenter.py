# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/hangar/presenters/comp7_light_loadout_presenter.py
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

class _Comp7LightLoadoutStatesObserver(_LoadoutStatesObserver):

    @property
    def _stateID(self):
        from comp7_light.gui.impl.lobby.hangar.states import Comp7LightLoadoutState
        return Comp7LightLoadoutState.STATE_ID


class Comp7LightLoadoutPresenter(LoadoutPresenter):
    _STATES_OBSERVER = _Comp7LightLoadoutStatesObserver

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : Comp7LightShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : ConsumablesPresenter(self._vehInteractingItem)}


class Comp7LightShellsPresenter(ShellsPresenter):

    @property
    def isShellState(self):
        from comp7_light.gui.impl.lobby.hangar.states import Comp7LightShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(Comp7LightShellsLoadoutState).isEntered()
