# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_entry_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class LootBoxEntryViewModel(ViewModel):
    __slots__ = ('onBoxSelected', 'onBuyBoxBtnClick', 'onDragNDropEnded', 'onOpenBoxHitAreaClick', 'onOpenBoxBtnClick', 'onCelebrityBtnClick', 'onQuestsBtnClick', 'onVideoChangeClick', 'onWindowClose', 'onVideoStarted', 'onVideoStopped', 'onVideoInterrupted', 'onFadeOutStarted', 'onFadeInCompleted', 'onGuaranteedRewardsInfo', 'onCountSelected', 'onLoadError')

    def __init__(self, properties=20, commands=17):
        super(LootBoxEntryViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def boxesCountButtons(self):
        return self._getViewModel(0)

    def getCurrentIndex(self):
        return self._getNumber(1)

    def setCurrentIndex(self, value):
        self._setNumber(1, value)

    def getSelectedBoxName(self):
        return self._getString(2)

    def setSelectedBoxName(self, value):
        self._setString(2, value)

    def getSelectedBoxType(self):
        return self._getString(3)

    def setSelectedBoxType(self, value):
        self._setString(3, value)

    def getIsEmptySwitch(self):
        return self._getBool(4)

    def setIsEmptySwitch(self, value):
        self._setBool(4, value)

    def getIsOpenBoxBtnVisible(self):
        return self._getBool(5)

    def setIsOpenBoxBtnVisible(self, value):
        self._setBool(5, value)

    def getIsBuyBoxBtnVisible(self):
        return self._getBool(6)

    def setIsBuyBoxBtnVisible(self, value):
        self._setBool(6, value)

    def getIsBackBtnVisible(self):
        return self._getBool(7)

    def setIsBackBtnVisible(self, value):
        self._setBool(7, value)

    def getIsGiftBuyBtnVisible(self):
        return self._getBool(8)

    def setIsGiftBuyBtnVisible(self, value):
        self._setBool(8, value)

    def getIsVideoOff(self):
        return self._getBool(9)

    def setIsVideoOff(self, value):
        self._setBool(9, value)

    def getIsVideoPlaying(self):
        return self._getBool(10)

    def setIsVideoPlaying(self, value):
        self._setBool(10, value)

    def getIsNeedSetFocus(self):
        return self._getBool(11)

    def setIsNeedSetFocus(self, value):
        self._setBool(11, value)

    def getOpenBoxesCounter(self):
        return self._getNumber(12)

    def setOpenBoxesCounter(self, value):
        self._setNumber(12, value)

    def getGuaranteedFrequency(self):
        return self._getNumber(13)

    def setGuaranteedFrequency(self, value):
        self._setNumber(13, value)

    def getAttemptsToGuaranteed(self):
        return self._getNumber(14)

    def setAttemptsToGuaranteed(self, value):
        self._setNumber(14, value)

    def getBoxTabs(self):
        return self._getArray(15)

    def setBoxTabs(self, value):
        self._setArray(15, value)

    def getIsViewAccessible(self):
        return self._getBool(16)

    def setIsViewAccessible(self, value):
        self._setBool(16, value)

    def getIsClientFocused(self):
        return self._getBool(17)

    def setIsClientFocused(self, value):
        self._setBool(17, value)

    def getIsBoxesUnavailable(self):
        return self._getBool(18)

    def setIsBoxesUnavailable(self, value):
        self._setBool(18, value)

    def getStreamBufferLength(self):
        return self._getNumber(19)

    def setStreamBufferLength(self, value):
        self._setNumber(19, value)

    def _initialize(self):
        super(LootBoxEntryViewModel, self)._initialize()
        self._addViewModelProperty('boxesCountButtons', UserListModel())
        self._addNumberProperty('currentIndex', 0)
        self._addStringProperty('selectedBoxName', '')
        self._addStringProperty('selectedBoxType', '')
        self._addBoolProperty('isEmptySwitch', False)
        self._addBoolProperty('isOpenBoxBtnVisible', False)
        self._addBoolProperty('isBuyBoxBtnVisible', False)
        self._addBoolProperty('isBackBtnVisible', False)
        self._addBoolProperty('isGiftBuyBtnVisible', False)
        self._addBoolProperty('isVideoOff', False)
        self._addBoolProperty('isVideoPlaying', False)
        self._addBoolProperty('isNeedSetFocus', False)
        self._addNumberProperty('openBoxesCounter', 0)
        self._addNumberProperty('guaranteedFrequency', 0)
        self._addNumberProperty('attemptsToGuaranteed', 0)
        self._addArrayProperty('boxTabs', Array())
        self._addBoolProperty('isViewAccessible', True)
        self._addBoolProperty('isClientFocused', True)
        self._addBoolProperty('isBoxesUnavailable', False)
        self._addNumberProperty('streamBufferLength', 1)
        self.onBoxSelected = self._addCommand('onBoxSelected')
        self.onBuyBoxBtnClick = self._addCommand('onBuyBoxBtnClick')
        self.onDragNDropEnded = self._addCommand('onDragNDropEnded')
        self.onOpenBoxHitAreaClick = self._addCommand('onOpenBoxHitAreaClick')
        self.onOpenBoxBtnClick = self._addCommand('onOpenBoxBtnClick')
        self.onCelebrityBtnClick = self._addCommand('onCelebrityBtnClick')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onVideoChangeClick = self._addCommand('onVideoChangeClick')
        self.onWindowClose = self._addCommand('onWindowClose')
        self.onVideoStarted = self._addCommand('onVideoStarted')
        self.onVideoStopped = self._addCommand('onVideoStopped')
        self.onVideoInterrupted = self._addCommand('onVideoInterrupted')
        self.onFadeOutStarted = self._addCommand('onFadeOutStarted')
        self.onFadeInCompleted = self._addCommand('onFadeInCompleted')
        self.onGuaranteedRewardsInfo = self._addCommand('onGuaranteedRewardsInfo')
        self.onCountSelected = self._addCommand('onCountSelected')
        self.onLoadError = self._addCommand('onLoadError')
