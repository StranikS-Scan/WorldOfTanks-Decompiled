# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/ny_reward_kit_main_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_reward_kit_statistics_model import NyRewardKitStatisticsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.reward_kit_guaranteed_reward_model import RewardKitGuaranteedRewardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_sidebar_common_model import NySidebarCommonModel

class NyRewardKitMainViewModel(ViewModel):
    __slots__ = ('onWindowClose', 'onChangeTab', 'onCountSelected', 'onOpenBoxFromHitArea', 'onOpenBox', 'onBuyBox', 'onAnimationSwitch', 'onSwitchBoxHover')

    def __init__(self, properties=17, commands=8):
        super(NyRewardKitMainViewModel, self).__init__(properties=properties, commands=commands)

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
    def rewardKitStatistics(self):
        return self._getViewModel(2)

    @staticmethod
    def getRewardKitStatisticsType():
        return NyRewardKitStatisticsModel

    @property
    def guaranteedReward(self):
        return self._getViewModel(3)

    @staticmethod
    def getGuaranteedRewardType():
        return RewardKitGuaranteedRewardModel

    def getCurrentName(self):
        return self._getString(4)

    def setCurrentName(self, value):
        self._setString(4, value)

    def getSelectedBoxType(self):
        return self._getString(5)

    def setSelectedBoxType(self, value):
        self._setString(5, value)

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

    def getIsRewardKitEnable(self):
        return self._getBool(15)

    def setIsRewardKitEnable(self, value):
        self._setBool(15, value)

    def getIsExternalLink(self):
        return self._getBool(16)

    def setIsExternalLink(self, value):
        self._setBool(16, value)

    def _initialize(self):
        super(NyRewardKitMainViewModel, self)._initialize()
        self._addViewModelProperty('sidebar', NySidebarCommonModel())
        self._addViewModelProperty('boxesCountButtons', UserListModel())
        self._addViewModelProperty('rewardKitStatistics', NyRewardKitStatisticsModel())
        self._addViewModelProperty('guaranteedReward', RewardKitGuaranteedRewardModel())
        self._addStringProperty('currentName', '')
        self._addStringProperty('selectedBoxType', '')
        self._addBoolProperty('isOpenBoxBtnVisible', False)
        self._addNumberProperty('currentCountButton', 0)
        self._addBoolProperty('isBoxChangeAnimation', False)
        self._addBoolProperty('isBoxOpenEnabled', True)
        self._addBoolProperty('isViewHidden', False)
        self._addBoolProperty('isVideoOff', False)
        self._addBoolProperty('isBoxesAvailable', False)
        self._addBoolProperty('isStatisticsHintActive', False)
        self._addStringProperty('realm', '')
        self._addBoolProperty('isRewardKitEnable', False)
        self._addBoolProperty('isExternalLink', False)
        self.onWindowClose = self._addCommand('onWindowClose')
        self.onChangeTab = self._addCommand('onChangeTab')
        self.onCountSelected = self._addCommand('onCountSelected')
        self.onOpenBoxFromHitArea = self._addCommand('onOpenBoxFromHitArea')
        self.onOpenBox = self._addCommand('onOpenBox')
        self.onBuyBox = self._addCommand('onBuyBox')
        self.onAnimationSwitch = self._addCommand('onAnimationSwitch')
        self.onSwitchBoxHover = self._addCommand('onSwitchBoxHover')
