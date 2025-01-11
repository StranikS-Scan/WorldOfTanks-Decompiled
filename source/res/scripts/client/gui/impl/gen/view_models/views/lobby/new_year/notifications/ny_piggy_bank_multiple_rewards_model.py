# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_piggy_bank_multiple_rewards_model.py
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_piggy_bank_single_reward_model import NyPiggyBankSingleRewardModel
from gui.impl.gen.view_models.views.lobby.new_year.notifications.ny_reward_notification_model import NyRewardNotificationModel

class NyPiggyBankMultipleRewardsModel(NyPiggyBankSingleRewardModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=2):
        super(NyPiggyBankMultipleRewardsModel, self).__init__(properties=properties, commands=commands)

    @property
    def additionalRewards(self):
        return self._getViewModel(4)

    @staticmethod
    def getAdditionalRewardsType():
        return NyRewardNotificationModel

    def _initialize(self):
        super(NyPiggyBankMultipleRewardsModel, self)._initialize()
        self._addViewModelProperty('additionalRewards', UserListModel())
