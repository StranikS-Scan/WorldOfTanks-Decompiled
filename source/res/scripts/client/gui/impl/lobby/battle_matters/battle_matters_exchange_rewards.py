# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_exchange_rewards.py
from functools import partial
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_exchange_rewards_model import BattleMattersExchangeRewardsModel
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.pub.dialog_window import DialogButtons

class BattleMattersExchangeRewards(FullScreenDialogBaseView):
    __slots__ = ()

    def __init__(self, vehicleName, vehicleUserName):
        settings = ViewSettings(R.views.lobby.battle_matters.BattleMattersExchangeRewards())
        settings.model = BattleMattersExchangeRewardsModel()
        settings.args = (vehicleName, vehicleUserName)
        super(BattleMattersExchangeRewards, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersExchangeRewards, self).getViewModel()

    def _onLoading(self, vehicleName, vehicleUserName):
        super(BattleMattersExchangeRewards, self)._onLoading()
        with self.viewModel.transaction() as tx:
            tx.setVehicleName(vehicleName)
            tx.setVehicleUserName(vehicleUserName)

    def _getEvents(self):
        return ((self.viewModel.onConfirm, partial(self._setResult, DialogButtons.SUBMIT)), (self.viewModel.onClose, partial(self._setResult, DialogButtons.CANCEL)))
