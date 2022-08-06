# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_exchange_rewards.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_exchange_rewards_model import BattleMattersExchangeRewardsModel
from gui.impl.pub import ViewImpl

class BattleMattersExchangeRewards(ViewImpl):
    __slots__ = ()

    def __init__(self, vehicleName, vehicleUserName):
        settings = ViewSettings(R.views.dialogs.sub_views.content.BattleMattersExchangeRewards())
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
