# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/promo_code_reward_screen/promo_code_reward_screen_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.promo_code_reward_screen.reward_bonus_model import RewardBonusModel

class PromoCodeRewardScreenViewModel(ViewModel):
    __slots__ = ('onClose', 'navigateToQuests')
    QUEST_REWARDS_NAME = 'questRewards'
    ARG_REWARD_INDEX = 'tooltipId'
    MAX_REWARDS = 10
    MAX_MAIN_REWARDS = 3

    def __init__(self, properties=10, commands=2):
        super(PromoCodeRewardScreenViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getSubtitle(self):
        return self._getString(2)

    def setSubtitle(self, value):
        self._setString(2, value)

    def getQuestsDescription(self):
        return self._getString(3)

    def setQuestsDescription(self, value):
        self._setString(3, value)

    def getBackgroundImage(self):
        return self._getString(4)

    def setBackgroundImage(self, value):
        self._setString(4, value)

    def getMainRewards(self):
        return self._getArray(5)

    def setMainRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getMainRewardsType():
        return RewardBonusModel

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return RewardBonusModel

    def getQuestRewards(self):
        return self._getArray(7)

    def setQuestRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getQuestRewardsType():
        return RewardBonusModel

    def getHasQuests(self):
        return self._getBool(8)

    def setHasQuests(self, value):
        self._setBool(8, value)

    def getShowToTasksButton(self):
        return self._getBool(9)

    def setShowToTasksButton(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(PromoCodeRewardScreenViewModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addStringProperty('title', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('questsDescription', '')
        self._addStringProperty('backgroundImage', '')
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('questRewards', Array())
        self._addBoolProperty('hasQuests', False)
        self._addBoolProperty('showToTasksButton', False)
        self.onClose = self._addCommand('onClose')
        self.navigateToQuests = self._addCommand('navigateToQuests')
