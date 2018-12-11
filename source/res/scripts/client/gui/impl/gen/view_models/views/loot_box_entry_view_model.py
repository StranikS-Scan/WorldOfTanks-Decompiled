# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_entry_view_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class LootBoxEntryViewModel(ViewModel):
    __slots__ = ('onBoxTypeSelected', 'onCloseBtnClick', 'onBackToHangarBtnClick', 'onOpenBoxBtnClick', 'onOpenBoxesBtnClick', 'onBuyBoxBtnClick', 'onVideoChangeClick', 'onVideoStarted', 'onVideoStopped', 'needShowBlackOverlay')

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
        return self._getResource(7)

    def setBoxInformation(self, value):
        self._setResource(7, value)

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

    def getOpenBoxesCounter(self):
        return self._getNumber(11)

    def setOpenBoxesCounter(self, value):
        self._setNumber(11, value)

    def getIsMulitOpenBtnVisible(self):
        return self._getBool(12)

    def setIsMulitOpenBtnVisible(self, value):
        self._setBool(12, value)

    def getIsVideoOff(self):
        return self._getBool(13)

    def setIsVideoOff(self, value):
        self._setBool(13, value)

    def getIsVideoPlaying(self):
        return self._getBool(14)

    def setIsVideoPlaying(self, value):
        self._setBool(14, value)

    def getIsNeedSetFocus(self):
        return self._getBool(15)

    def setIsNeedSetFocus(self, value):
        self._setBool(15, value)

    def getIsGiftBuyBtnVisible(self):
        return self._getBool(16)

    def setIsGiftBuyBtnVisible(self, value):
        self._setBool(16, value)

    def getShowBlackOverlay(self):
        return self._getBool(17)

    def setShowBlackOverlay(self, value):
        self._setBool(17, value)

    def getIsTopBarVisible(self):
        return self._getBool(18)

    def setIsTopBarVisible(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(LootBoxEntryViewModel, self)._initialize()
        self._addViewModelProperty('boxSelector', UserListModel())
        self._addViewModelProperty('topBar', UserListModel())
        self._addNumberProperty('currentIndex', 0)
        self._addResourceProperty('selectedBoxIcon', Resource.INVALID)
        self._addStringProperty('selectedBoxType', '')
        self._addStringProperty('selectedBoxCategory', '')
        self._addBoolProperty('isEmptySwitch', False)
        self._addResourceProperty('boxInformation', Resource.INVALID)
        self._addBoolProperty('isOpenBoxBtnVisible', True)
        self._addBoolProperty('isBuyBoxBtnVisible', False)
        self._addBoolProperty('isBackBtnVisible', False)
        self._addNumberProperty('openBoxesCounter', 0)
        self._addBoolProperty('isMulitOpenBtnVisible', True)
        self._addBoolProperty('isVideoOff', False)
        self._addBoolProperty('isVideoPlaying', False)
        self._addBoolProperty('isNeedSetFocus', False)
        self._addBoolProperty('isGiftBuyBtnVisible', True)
        self._addBoolProperty('showBlackOverlay', False)
        self._addBoolProperty('isTopBarVisible', False)
        self.onBoxTypeSelected = self._addCommand('onBoxTypeSelected')
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBackToHangarBtnClick = self._addCommand('onBackToHangarBtnClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onOpenBoxesBtnClick = self._addCommand('onOpenBoxesBtnClick')
        self.onBuyBoxBtnClick = self._addCommand('onBuyBoxBtnClick')
        self.onVideoChangeClick = self._addCommand('onVideoChangeClick')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
        self.needShowBlackOverlay = self._addCommand('needShowBlackOverlay')
