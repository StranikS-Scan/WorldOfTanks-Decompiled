# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/steam_email_confirm_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class SteamEmailConfirmRewardsViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=1, commands=1):
        super(SteamEmailConfirmRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(0)

    def setBonuses(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBonusesType():
        return ItemBonusModel

    def _initialize(self):
        super(SteamEmailConfirmRewardsViewModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self.onClose = self._addCommand('onClose')
