# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/reward_kit_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_model import NyRewardKitStatisticsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.reward_kit_guaranteed_reward_model import RewardKitGuaranteedRewardModel

class RewardKitRewardViewModel(ViewModel):
    __slots__ = ('onClose', 'onNextOpen', 'onVideoChange', 'onCloseEvent', 'onDestroyEvent', 'onReadyToRestart', 'showSpecialReward', 'onBuyBox', 'onSpecialAction')

    def __init__(self, properties=19, commands=9):
        super(RewardKitRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def guaranteedReward(self):
        return self._getViewModel(0)

    @staticmethod
    def getGuaranteedRewardType():
        return RewardKitGuaranteedRewardModel

    @property
    def rewardKitStatistics(self):
        return self._getViewModel(1)

    @staticmethod
    def getRewardKitStatisticsType():
        return NyRewardKitStatisticsModel

    def getIsVideoOff(self):
        return self._getBool(2)

    def setIsVideoOff(self, value):
        self._setBool(2, value)

    def getLeftLootBoxes(self):
        return self._getNumber(3)

    def setLeftLootBoxes(self, value):
        self._setNumber(3, value)

    def getBoxCategory(self):
        return self._getString(4)

    def setBoxCategory(self, value):
        self._setString(4, value)

    def getIsFreeBox(self):
        return self._getBool(5)

    def setIsFreeBox(self, value):
        self._setBool(5, value)

    def getFadeOut(self):
        return self._getBool(6)

    def setFadeOut(self, value):
        self._setBool(6, value)

    def getIsOpening(self):
        return self._getBool(7)

    def setIsOpening(self, value):
        self._setBool(7, value)

    def getIsReload(self):
        return self._getBool(8)

    def setIsReload(self, value):
        self._setBool(8, value)

    def getRewards(self):
        return self._getArray(9)

    def setRewards(self, value):
        self._setArray(9, value)

    def getIsNextBtnEnabled(self):
        return self._getBool(10)

    def setIsNextBtnEnabled(self, value):
        self._setBool(10, value)

    def getIsGiftBuyBtnVisible(self):
        return self._getBool(11)

    def setIsGiftBuyBtnVisible(self, value):
        self._setBool(11, value)

    def getHardReset(self):
        return self._getBool(12)

    def setHardReset(self, value):
        self._setBool(12, value)

    def getSpecialRewardType(self):
        return self._getString(13)

    def setSpecialRewardType(self, value):
        self._setString(13, value)

    def getIsSpecialRewardClosed(self):
        return self._getBool(14)

    def setIsSpecialRewardClosed(self, value):
        self._setBool(14, value)

    def getIsForcedRendering(self):
        return self._getBool(15)

    def setIsForcedRendering(self, value):
        self._setBool(15, value)

    def getIsMemoryRiskySystem(self):
        return self._getBool(16)

    def setIsMemoryRiskySystem(self, value):
        self._setBool(16, value)

    def getSyncInitiator(self):
        return self._getNumber(17)

    def setSyncInitiator(self, value):
        self._setNumber(17, value)

    def getRealm(self):
        return self._getString(18)

    def setRealm(self, value):
        self._setString(18, value)

    def _initialize(self):
        super(RewardKitRewardViewModel, self)._initialize()
        self._addViewModelProperty('guaranteedReward', RewardKitGuaranteedRewardModel())
        self._addViewModelProperty('rewardKitStatistics', NyRewardKitStatisticsModel())
        self._addBoolProperty('isVideoOff', False)
        self._addNumberProperty('leftLootBoxes', 0)
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isFreeBox', False)
        self._addBoolProperty('fadeOut', False)
        self._addBoolProperty('isOpening', True)
        self._addBoolProperty('isReload', False)
        self._addArrayProperty('rewards', Array())
        self._addBoolProperty('isNextBtnEnabled', True)
        self._addBoolProperty('isGiftBuyBtnVisible', True)
        self._addBoolProperty('hardReset', False)
        self._addStringProperty('specialRewardType', '')
        self._addBoolProperty('isSpecialRewardClosed', False)
        self._addBoolProperty('isForcedRendering', False)
        self._addBoolProperty('isMemoryRiskySystem', False)
        self._addNumberProperty('syncInitiator', 0)
        self._addStringProperty('realm', '')
        self.onClose = self._addCommand('onClose')
        self.onNextOpen = self._addCommand('onNextOpen')
        self.onVideoChange = self._addCommand('onVideoChange')
        self.onCloseEvent = self._addCommand('onCloseEvent')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.onBuyBox = self._addCommand('onBuyBox')
        self.onSpecialAction = self._addCommand('onSpecialAction')
