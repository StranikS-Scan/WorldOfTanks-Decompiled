# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/quests/ny_quests_reward_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyQuestsRewardModel(ViewModel):
    __slots__ = ('onClose', 'onGoToMachine', 'onGoToQuests', 'onGoToLootbox')

    def __init__(self, properties=1, commands=4):
        super(NyQuestsRewardModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return RewardItemModel

    def _initialize(self):
        super(NyQuestsRewardModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self.onClose = self._addCommand('onClose')
        self.onGoToMachine = self._addCommand('onGoToMachine')
        self.onGoToQuests = self._addCommand('onGoToQuests')
        self.onGoToLootbox = self._addCommand('onGoToLootbox')
