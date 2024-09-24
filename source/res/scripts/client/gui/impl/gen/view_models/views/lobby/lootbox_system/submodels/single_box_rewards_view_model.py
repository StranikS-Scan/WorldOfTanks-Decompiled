# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/single_box_rewards_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.bonus_model import BonusModel

class SingleBoxRewardsViewModel(ViewModel):
    __slots__ = ('onOpen', 'onGoBack', 'onPreview', 'onBuyBoxes', 'onAnimationStateChanged', 'onVideoPlaying', 'onClose')

    def __init__(self, properties=11, commands=7):
        super(SingleBoxRewardsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusesType():
        return BonusModel

    @property
    def extraBonuses(self):
        return self._getViewModel(1)

    @staticmethod
    def getExtraBonusesType():
        return BonusModel

    def getEventName(self):
        return self._getString(2)

    def setEventName(self, value):
        self._setString(2, value)

    def getBoxCategory(self):
        return self._getString(3)

    def setBoxCategory(self, value):
        self._setString(3, value)

    def getIsReopen(self):
        return self._getBool(4)

    def setIsReopen(self, value):
        self._setBool(4, value)

    def getUseExternal(self):
        return self._getBool(5)

    def setUseExternal(self, value):
        self._setBool(5, value)

    def getBoxesCount(self):
        return self._getNumber(6)

    def setBoxesCount(self, value):
        self._setNumber(6, value)

    def getBoxesCountToGuaranteed(self):
        return self._getNumber(7)

    def setBoxesCountToGuaranteed(self, value):
        self._setNumber(7, value)

    def getIsAnimationActive(self):
        return self._getBool(8)

    def setIsAnimationActive(self, value):
        self._setBool(8, value)

    def getIsAwaitingResponse(self):
        return self._getBool(9)

    def setIsAwaitingResponse(self, value):
        self._setBool(9, value)

    def getIsWindowAccessible(self):
        return self._getBool(10)

    def setIsWindowAccessible(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(SingleBoxRewardsViewModel, self)._initialize()
        self._addViewModelProperty('bonuses', UserListModel())
        self._addViewModelProperty('extraBonuses', UserListModel())
        self._addStringProperty('eventName', '')
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isReopen', False)
        self._addBoolProperty('useExternal', False)
        self._addNumberProperty('boxesCount', 0)
        self._addNumberProperty('boxesCountToGuaranteed', 0)
        self._addBoolProperty('isAnimationActive', False)
        self._addBoolProperty('isAwaitingResponse', False)
        self._addBoolProperty('isWindowAccessible', False)
        self.onOpen = self._addCommand('onOpen')
        self.onGoBack = self._addCommand('onGoBack')
        self.onPreview = self._addCommand('onPreview')
        self.onBuyBoxes = self._addCommand('onBuyBoxes')
        self.onAnimationStateChanged = self._addCommand('onAnimationStateChanged')
        self.onVideoPlaying = self._addCommand('onVideoPlaying')
        self.onClose = self._addCommand('onClose')
