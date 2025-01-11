# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_entry_video_view_model.py
from frameworks.wulf import ViewModel

class LootBoxEntryVideoViewModel(ViewModel):
    __slots__ = ('onDeliveryVideoStarted', 'onDeliveryVideoStopped', 'onDeliveryVideoInterrupted', 'onDeliveryShowControls', 'onVideoLoadError', 'onBoxTransitionEnd')

    def __init__(self, properties=7, commands=6):
        super(LootBoxEntryVideoViewModel, self).__init__(properties=properties, commands=commands)

    def getIsViewAccessible(self):
        return self._getBool(0)

    def setIsViewAccessible(self, value):
        self._setBool(0, value)

    def getIsClientFocused(self):
        return self._getBool(1)

    def setIsClientFocused(self, value):
        self._setBool(1, value)

    def getIsDeliveryVideoPlaying(self):
        return self._getBool(2)

    def setIsDeliveryVideoPlaying(self, value):
        self._setBool(2, value)

    def getStreamBufferLength(self):
        return self._getNumber(3)

    def setStreamBufferLength(self, value):
        self._setNumber(3, value)

    def getSelectedBoxName(self):
        return self._getString(4)

    def setSelectedBoxName(self, value):
        self._setString(4, value)

    def getIsBoxHovered(self):
        return self._getBool(5)

    def setIsBoxHovered(self, value):
        self._setBool(5, value)

    def getIsEmptySwitch(self):
        return self._getBool(6)

    def setIsEmptySwitch(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(LootBoxEntryVideoViewModel, self)._initialize()
        self._addBoolProperty('isViewAccessible', True)
        self._addBoolProperty('isClientFocused', True)
        self._addBoolProperty('isDeliveryVideoPlaying', False)
        self._addNumberProperty('streamBufferLength', 1)
        self._addStringProperty('selectedBoxName', '')
        self._addBoolProperty('isBoxHovered', False)
        self._addBoolProperty('isEmptySwitch', False)
        self.onDeliveryVideoStarted = self._addCommand('onDeliveryVideoStarted')
        self.onDeliveryVideoStopped = self._addCommand('onDeliveryVideoStopped')
        self.onDeliveryVideoInterrupted = self._addCommand('onDeliveryVideoInterrupted')
        self.onDeliveryShowControls = self._addCommand('onDeliveryShowControls')
        self.onVideoLoadError = self._addCommand('onVideoLoadError')
        self.onBoxTransitionEnd = self._addCommand('onBoxTransitionEnd')
