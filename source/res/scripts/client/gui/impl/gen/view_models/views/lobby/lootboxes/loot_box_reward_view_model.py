# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootboxes.friend_gift_loot_box_info import FriendGiftLootBoxInfo
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_guaranteed_reward_model import LootBoxGuaranteedRewardModel

class LootBoxRewardViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onNextBtnClick', 'onVideoChangeClick', 'onCloseEvent', 'onDestroyEvent', 'onReadyToRestart', 'showSpecialReward', 'onBuyBoxBtnClick', 'onSpecialActionBtnClick')

    def __init__(self, properties=21, commands=9):
        super(LootBoxRewardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def friendGiftLootBoxInfo(self):
        return self._getViewModel(0)

    @property
    def guaranteedReward(self):
        return self._getViewModel(1)

    def getIsVideoOff(self):
        return self._getBool(2)

    def setIsVideoOff(self, value):
        self._setBool(2, value)

    def getLeftLootBoxes(self):
        return self._getNumber(3)

    def setLeftLootBoxes(self, value):
        self._setNumber(3, value)

    def getBoxType(self):
        return self._getString(4)

    def setBoxType(self, value):
        self._setString(4, value)

    def getBoxCategory(self):
        return self._getString(5)

    def setBoxCategory(self, value):
        self._setString(5, value)

    def getIsFreeBox(self):
        return self._getBool(6)

    def setIsFreeBox(self, value):
        self._setBool(6, value)

    def getFadeOut(self):
        return self._getBool(7)

    def setFadeOut(self, value):
        self._setBool(7, value)

    def getIsOpening(self):
        return self._getBool(8)

    def setIsOpening(self, value):
        self._setBool(8, value)

    def getIsReload(self):
        return self._getBool(9)

    def setIsReload(self, value):
        self._setBool(9, value)

    def getRewards(self):
        return self._getArray(10)

    def setRewards(self, value):
        self._setArray(10, value)

    def getIsNextBtnEnabled(self):
        return self._getBool(11)

    def setIsNextBtnEnabled(self, value):
        self._setBool(11, value)

    def getIsGiftBuyBtnVisible(self):
        return self._getBool(12)

    def setIsGiftBuyBtnVisible(self, value):
        self._setBool(12, value)

    def getHardReset(self):
        return self._getBool(13)

    def setHardReset(self, value):
        self._setBool(13, value)

    def getSpecialRewardType(self):
        return self._getString(14)

    def setSpecialRewardType(self, value):
        self._setString(14, value)

    def getIsSpecialRewardClosed(self):
        return self._getBool(15)

    def setIsSpecialRewardClosed(self, value):
        self._setBool(15, value)

    def getIsForcedRendering(self):
        return self._getBool(16)

    def setIsForcedRendering(self, value):
        self._setBool(16, value)

    def getIsMemoryRiskySystem(self):
        return self._getBool(17)

    def setIsMemoryRiskySystem(self, value):
        self._setBool(17, value)

    def getSyncInitiator(self):
        return self._getNumber(18)

    def setSyncInitiator(self, value):
        self._setNumber(18, value)

    def getRealm(self):
        return self._getString(19)

    def setRealm(self, value):
        self._setString(19, value)

    def getIsBoxFromFriend(self):
        return self._getBool(20)

    def setIsBoxFromFriend(self, value):
        self._setBool(20, value)

    def _initialize(self):
        super(LootBoxRewardViewModel, self)._initialize()
        self._addViewModelProperty('friendGiftLootBoxInfo', FriendGiftLootBoxInfo())
        self._addViewModelProperty('guaranteedReward', LootBoxGuaranteedRewardModel())
        self._addBoolProperty('isVideoOff', False)
        self._addNumberProperty('leftLootBoxes', 0)
        self._addStringProperty('boxType', '')
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
        self._addBoolProperty('isBoxFromFriend', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onNextBtnClick = self._addCommand('onNextBtnClick')
        self.onVideoChangeClick = self._addCommand('onVideoChangeClick')
        self.onCloseEvent = self._addCommand('onCloseEvent')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
        self.onReadyToRestart = self._addCommand('onReadyToRestart')
        self.showSpecialReward = self._addCommand('showSpecialReward')
        self.onBuyBoxBtnClick = self._addCommand('onBuyBoxBtnClick')
        self.onSpecialActionBtnClick = self._addCommand('onSpecialActionBtnClick')
