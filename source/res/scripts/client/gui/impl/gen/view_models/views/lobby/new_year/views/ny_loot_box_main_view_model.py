# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_loot_box_main_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_guaranteed_reward_model import LootBoxGuaranteedRewardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_common_model import NySidebarCommonModel

class NyLootBoxMainViewModel(ViewModel):
    __slots__ = ('onWindowClose', 'onTabClick', 'onCountSelected', 'onOpenBoxHitAreaClick', 'onOpenBoxBtnClick', 'onBuyBoxBtnClick', 'onQuestsBtnClick', 'onAnimationSwitchClick', 'onStatisticsButtonClick', 'onSwitchBoxHover')

    def __init__(self, properties=15, commands=10):
        super(NyLootBoxMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def sidebar(self):
        return self._getViewModel(0)

    @staticmethod
    def getSidebarType():
        return NySidebarCommonModel

    @property
    def boxesCountButtons(self):
        return self._getViewModel(1)

    @staticmethod
    def getBoxesCountButtonsType():
        return UserListModel

    @property
    def guaranteedReward(self):
        return self._getViewModel(2)

    @staticmethod
    def getGuaranteedRewardType():
        return LootBoxGuaranteedRewardModel

    def getCurrentName(self):
        return self._getString(3)

    def setCurrentName(self, value):
        self._setString(3, value)

    def getSelectedBoxType(self):
        return self._getString(4)

    def setSelectedBoxType(self, value):
        self._setString(4, value)

    def getIsPremiumType(self):
        return self._getBool(5)

    def setIsPremiumType(self, value):
        self._setBool(5, value)

    def getIsOpenBoxBtnVisible(self):
        return self._getBool(6)

    def setIsOpenBoxBtnVisible(self, value):
        self._setBool(6, value)

    def getCurrentCountButton(self):
        return self._getNumber(7)

    def setCurrentCountButton(self, value):
        self._setNumber(7, value)

    def getIsBoxChangeAnimation(self):
        return self._getBool(8)

    def setIsBoxChangeAnimation(self, value):
        self._setBool(8, value)

    def getIsBoxOpenEnabled(self):
        return self._getBool(9)

    def setIsBoxOpenEnabled(self, value):
        self._setBool(9, value)

    def getIsViewHidden(self):
        return self._getBool(10)

    def setIsViewHidden(self, value):
        self._setBool(10, value)

    def getIsVideoOff(self):
        return self._getBool(11)

    def setIsVideoOff(self, value):
        self._setBool(11, value)

    def getIsBoxesAvailable(self):
        return self._getBool(12)

    def setIsBoxesAvailable(self, value):
        self._setBool(12, value)

    def getIsStatisticsHintActive(self):
        return self._getBool(13)

    def setIsStatisticsHintActive(self, value):
        self._setBool(13, value)

    def getRealm(self):
        return self._getString(14)

    def setRealm(self, value):
        self._setString(14, value)

    def _initialize(self):
        super(NyLootBoxMainViewModel, self)._initialize()
        self._addViewModelProperty('sidebar', NySidebarCommonModel())
        self._addViewModelProperty('boxesCountButtons', UserListModel())
        self._addViewModelProperty('guaranteedReward', LootBoxGuaranteedRewardModel())
        self._addStringProperty('currentName', '')
        self._addStringProperty('selectedBoxType', '')
        self._addBoolProperty('isPremiumType', False)
        self._addBoolProperty('isOpenBoxBtnVisible', False)
        self._addNumberProperty('currentCountButton', 0)
        self._addBoolProperty('isBoxChangeAnimation', False)
        self._addBoolProperty('isBoxOpenEnabled', True)
        self._addBoolProperty('isViewHidden', False)
        self._addBoolProperty('isVideoOff', False)
        self._addBoolProperty('isBoxesAvailable', False)
        self._addBoolProperty('isStatisticsHintActive', False)
        self._addStringProperty('realm', '')
        self.onWindowClose = self._addCommand('onWindowClose')
        self.onTabClick = self._addCommand('onTabClick')
        self.onCountSelected = self._addCommand('onCountSelected')
        self.onOpenBoxHitAreaClick = self._addCommand('onOpenBoxHitAreaClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onBuyBoxBtnClick = self._addCommand('onBuyBoxBtnClick')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onAnimationSwitchClick = self._addCommand('onAnimationSwitchClick')
        self.onStatisticsButtonClick = self._addCommand('onStatisticsButtonClick')
        self.onSwitchBoxHover = self._addCommand('onSwitchBoxHover')
