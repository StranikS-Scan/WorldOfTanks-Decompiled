# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/tooltips/not_profiled_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.not_profiled_tooltip_model import NotProfiledTooltipModel
from historical_battles.gui.impl.lobby.widgets.frontman_widget import FrontmanRoleIDToRole
from items import vehicles
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class NotProfiledTooltip(ViewImpl):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        settings = ViewSettings(R.views.historical_battles.lobby.tooltips.NotProfiledVehicleTooltip())
        settings.model = NotProfiledTooltipModel()
        super(NotProfiledTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NotProfiledTooltip, self).getViewModel()

    def _onLoading(self):
        super(NotProfiledTooltip, self)._onLoading()
        selectedFrontman = self._gameEventController.frontController.getSelectedFrontman()
        roleAblilityID = selectedFrontman.getRoleAbility()
        roleAbility = vehicles.g_cache.equipments()[roleAblilityID]
        with self.viewModel.transaction() as tx:
            tx.setFrontmanID(selectedFrontman.getID())
            tx.setVehicleName(selectedFrontman.getSelectedVehicle().userName)
            tx.setRoleName(FrontmanRoleIDToRole.get(selectedFrontman.getRoleID()).value)
            tx.setRoleAbilityName(roleAbility.userString)
