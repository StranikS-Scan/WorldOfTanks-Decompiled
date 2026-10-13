# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/presenters/loadout_presenter.py
from __future__ import absolute_import
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.gen import R
from gui.impl.lobby.hangar.presenters.consumables_presenter import ConsumablesPresenter
from gui.impl.lobby.hangar.presenters.equipments_presenter import EquipmentsPresenter
from gui.impl.lobby.hangar.presenters.instructions_presenter import InstructionsPresenter
from gui.impl.lobby.hangar.presenters.loadout_presenter import LoadoutPresenter, _LoadoutStatesObserver
from gui.impl.lobby.hangar.presenters.loadout_presenter_base import LoadoutEntityProvider
from gui.impl.lobby.hangar.presenters.shells_presenter import ShellsPresenter
from gui.impl.lobby.tank_setup.configurations.consumable import ConsumableTabs
from gui.impl.lobby.tank_setup.interactors.consumable import ConsumableInteractor
from fort_rush.gui.impl.lobby.tank_setup.array_provider import FortRushConsumableProvider
from gui.impl.gen.view_models.views.lobby.loadout.panel.ammunition.ammunition_panel_model import AmmunitionPanelModel

class _FortRushLoadoutStatesObserver(_LoadoutStatesObserver):

    @property
    def _stateID(self):
        from fort_rush.gui.impl.lobby.states import FortRushLoadoutState
        return FortRushLoadoutState.STATE_ID


class FortRushLoadoutPresenter(LoadoutPresenter):
    _VIEW_MODEL = AmmunitionPanelModel
    _STATES_OBSERVER = _FortRushLoadoutStatesObserver

    def _getChildComponents(self):
        hangar = R.aliases.hangar.shared
        return {hangar.Equipments(): lambda : EquipmentsPresenter(self._vehInteractingItem),
         hangar.Instructions(): lambda : InstructionsPresenter(self._vehInteractingItem),
         hangar.Shells(): lambda : FortRushShellsPresenter(self._vehInteractingItem),
         hangar.Consumables(): lambda : FortRushConsumablesPresenter(self._vehInteractingItem)}


class FortRushConsumablesPresenter(ConsumablesPresenter):

    def _createProvider(self, vehInteractingItem):
        self._provider = LoadoutEntityProvider(vehInteractingItem, ConsumableInteractor, {ConsumableTabs.DEFAULT: FortRushConsumableProvider})


class FortRushShellsPresenter(ShellsPresenter):

    @property
    def isShellState(self):
        from fort_rush.gui.impl.lobby.states import FortRushShellsLoadoutState
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(FortRushShellsLoadoutState).isEntered()
