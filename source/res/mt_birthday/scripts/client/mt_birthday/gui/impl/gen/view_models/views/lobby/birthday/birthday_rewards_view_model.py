# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/birthday_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class BirthdayRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'goToContainers', 'goToGoldCarriage')

    def __init__(self, properties=8, commands=3):
        super(BirthdayRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getBloggerName(self):
        return self._getString(0)

    def setBloggerName(self, value):
        self._setString(0, value)

    def getPhraseID(self):
        return self._getNumber(1)

    def setPhraseID(self, value):
        self._setNumber(1, value)

    def getStage(self):
        return self._getNumber(2)

    def setStage(self, value):
        self._setNumber(2, value)

    def getIsRewardSeen(self):
        return self._getBool(3)

    def setIsRewardSeen(self, value):
        self._setBool(3, value)

    def getIsFinalReward(self):
        return self._getBool(4)

    def setIsFinalReward(self, value):
        self._setBool(4, value)

    def getIsNameLoading(self):
        return self._getBool(5)

    def setIsNameLoading(self, value):
        self._setBool(5, value)

    def getMainRewards(self):
        return self._getArray(6)

    def setMainRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(BirthdayRewardsViewModel, self)._initialize()
        self._addStringProperty('bloggerName', '')
        self._addNumberProperty('phraseID', 1)
        self._addNumberProperty('stage', 0)
        self._addBoolProperty('isRewardSeen', True)
        self._addBoolProperty('isFinalReward', False)
        self._addBoolProperty('isNameLoading', False)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.goToContainers = self._addCommand('goToContainers')
        self.goToGoldCarriage = self._addCommand('goToGoldCarriage')
