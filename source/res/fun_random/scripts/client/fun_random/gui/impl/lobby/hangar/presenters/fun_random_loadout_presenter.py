# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/presenters/fun_random_loadout_presenter.py
from __future__ import absolute_import
import typing
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.impl.lobby.hangar.controllers.fun_random_ammo_groups_controller import FunRandomHangarAmmunitionGroupsController
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import LoadoutPresenter, _LoadoutStatesObserver
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from gui.Scaleform.lobby_entry import getLobbyStateMachine
if typing.TYPE_CHECKING:
    from gui.impl.pub.view_component import ViewComponent

class _FunRandomLoadoutStatesObserver(_LoadoutStatesObserver):

    @property
    def _stateID(self):
        from fun_random.gui.impl.lobby.hangar.states import FunRandomLoadoutState
        return FunRandomLoadoutState.STATE_ID


class FunRandomLoadoutPresenter(LoadoutPresenter, FunSubModesWatcher):
    _STATES_OBSERVER = _FunRandomLoadoutStatesObserver

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : FunRandomShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : ConsumablesPresenter(self._vehInteractingItem)}

    def _subscribe(self):
        super(FunRandomLoadoutPresenter, self)._subscribe()
        self.startSubSelectionListening(self.__onSubModeChanged)

    def _unsubscribe(self):
        self.stopSubSelectionListening(self.__onSubModeChanged)
        super(FunRandomLoadoutPresenter, self)._unsubscribe()

    def _createAmmunitionGroupsController(self, vehicle):
        return FunRandomHangarAmmunitionGroupsController(vehicle)

    def __onSubModeChanged(self, *_):
        self._updateAmmunitionGroupsController(True)


class FunRandomShellsPresenter(ShellsPresenter):

    @property
    def isShellState(self):
        from fun_random.gui.impl.lobby.hangar.states import FunRandomShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(FunRandomShellsLoadoutState).isEntered()
