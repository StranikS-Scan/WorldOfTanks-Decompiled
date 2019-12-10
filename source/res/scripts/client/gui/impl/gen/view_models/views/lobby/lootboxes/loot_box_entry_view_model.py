# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_entry_view_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class LootBoxEntryViewModel(ViewModel):
    __slots__ = ('onBoxTypeSelected', 'onCloseBtnClick', 'onBackToHangarBtnClick', 'onOpenBoxBtnClick', 'onOpenBoxesBtnClick', 'onBuyBoxBtnClick', 'onVideoChangeClick', 'onVideoStarted', 'onVideoStopped', 'onFadeInCompleted', 'onFadeOutStarted', 'needShowBlackOverlay')

    def __init__(self, properties=19, commands=12):
        super(LootBoxEntryViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def boxSelector(self):
        return self._getViewModel(0)

    @property
    def topBar(self):
        return self._getViewModel(1)

    def getCurrentIndex(self):
        return self._getNumber(2)

    def setCurrentIndex(self, value):
        self._setNumber(2, value)

    def getSelectedBoxIcon(self):
        return self._getResource(3)

    def setSelectedBoxIcon(self, value):
        self._setResource(3, value)

    def getSelectedBoxType(self):
        return self._getString(4)

    def setSelectedBoxType(self, value):
        self._setString(4, value)

    def getSelectedBoxCategory(self):
        return self._getString(5)

    def setSelectedBoxCategory(self, value):
        self._setString(5, value)

    def getIsEmptySwitch(self):
        return self._getBool(6)

    def setIsEmptySwitch(self, value):
        self._setBool(6, value)

    def getBoxInformation(self):
        return self._getString(7)

    def setBoxInformation(self, value):
        self._setString(7, value)

    def getIsOpenBoxBtnVisible(self):
        return self._getBool(8)

    def setIsOpenBoxBtnVisible(self, value):
        self._setBool(8, value)

    def getIsBuyBoxBtnVisible(self):
        return self._getBool(9)

    def setIsBuyBoxBtnVisible(self, value):
        self._setBool(9, value)

    def getIsBackBtnVisible(self):
        return self._getBool(10)

    def setIsBackBtnVisible(self, value):
        self._setBool(10, value)

    def getIsVideoOff(self):
        return self._getBool(11)

    def setIsVideoOff(self, value):
        self._setBool(11, value)

    def getIsVideoPlaying(self):
        return self._getBool(12)

    def setIsVideoPlaying(self, value):
        self._setBool(12, value)

    def getIsNeedSetFocus(self):
        return self._getBool(13)

    def setIsNeedSetFocus(self, value):
        self._setBool(13, value)

    def getIsGiftBuyBtnVisible(self):
        return self._getBool(14)

    def setIsGiftBuyBtnVisible(self, value):
        self._setBool(14, value)

    def getShowBlackOverlay(self):
        return self._getBool(15)

    def setShowBlackOverlay(self, value):
        self._setBool(15, value)

    def getIsTopBarVisible(self):
        return self._getBool(16)

    def setIsTopBarVisible(self, value):
        self._setBool(16, value)

    def getOpenBoxesCounter(self):
        return self._getNumber(17)

    def setOpenBoxesCounter(self, value):
        self._setNumber(17, value)

    def getIsMultiOpenBtnVisible(self):
        return self._getBool(18)

    def setIsMultiOpenBtnVisible(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(LootBoxEntryViewModel, self)._initialize()
        self._addViewModelProperty('boxSelector', UserListModel())
        self._addViewModelProperty('topBar', UserListModel())
        self._addNumberProperty('currentIndex', 0)
        self._addResourceProperty('selectedBoxIcon', R.invalid())
        self._addStringProperty('selectedBoxType', '')
        self._addStringProperty('selectedBoxCategory', '')
        self._addBoolProperty('isEmptySwitch', False)
        self._addStringProperty('boxInformation', '')
        self._addBoolProperty('isOpenBoxBtnVisible', True)
        self._addBoolProperty('isBuyBoxBtnVisible', False)
        self._addBoolProperty('isBackBtnVisible', False)
        self._addBoolProperty('isVideoOff', False)
        self._addBoolProperty('isVideoPlaying', False)
        self._addBoolProperty('isNeedSetFocus', False)
        self._addBoolProperty('isGiftBuyBtnVisible', True)
        self._addBoolProperty('showBlackOverlay', False)
        self._addBoolProperty('isTopBarVisible', False)
        self._addNumberProperty('openBoxesCounter', 0)
        self._addBoolProperty('isMultiOpenBtnVisible', False)
        self.onBoxTypeSelected = self._addCommand('onBoxTypeSelected')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBackToHangarBtnClick = self._addCommand('onBackToHangarBtnClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onOpenBoxesBtnClick = self._addCommand('onOpenBoxesBtnClick')
        self.onBuyBoxBtnClick = self._addCommand('onBuyBoxBtnClick')
        self.onVideoChangeClick = self._addCommand('onVideoChangeClick')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
        self.onFadeInCompleted = self._addCommand('onFadeInCompleted')
        self.onFadeOutStarted = self._addCommand('onFadeOutStarted')
        self.needShowBlackOverlay = self._addCommand('needShowBlackOverlay')
