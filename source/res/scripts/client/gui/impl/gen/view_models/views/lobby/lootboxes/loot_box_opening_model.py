# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/loot_box_opening_model.py
from frameworks.wulf import ViewModel

class LootBoxOpeningModel(ViewModel):
    __slots__ = ('onOpeningStart', 'onOpeningEnd', 'onReloadEnd', 'onNeedShowRewards', 'onVideoOffViewReady', 'onLoadError')

    def __init__(self, properties=10, commands=6):
        super(LootBoxOpeningModel, self).__init__(properties=properties, commands=commands)

    def getBoxCategory(self):
        return self._getString(0)

    def setBoxCategory(self, value):
        self._setString(0, value)

    def getIsFreeBox(self):
        return self._getBool(1)

    def setIsFreeBox(self, value):
        self._setBool(1, value)

    def getIsVideoOff(self):
        return self._getBool(2)

    def setIsVideoOff(self, value):
        self._setBool(2, value)

    def getSpecialRewardType(self):
        return self._getString(3)

    def setSpecialRewardType(self, value):
        self._setString(3, value)

    def getIsOpening(self):
        return self._getBool(4)

    def setIsOpening(self, value):
        self._setBool(4, value)

    def getIsIdleGuestCVisible(self):
        return self._getBool(5)

    def setIsIdleGuestCVisible(self, value):
        self._setBool(5, value)

    def getIsReloading(self):
        return self._getBool(6)

    def setIsReloading(self, value):
        self._setBool(6, value)

    def getIsWindowAccessible(self):
        return self._getBool(7)

    def setIsWindowAccessible(self, value):
        self._setBool(7, value)

    def getStreamBufferLength(self):
        return self._getNumber(8)

    def setStreamBufferLength(self, value):
        self._setNumber(8, value)

    def getIsForcedToEnd(self):
        return self._getBool(9)

    def setIsForcedToEnd(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(LootBoxOpeningModel, self)._initialize()
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isFreeBox', False)
        self._addBoolProperty('isVideoOff', False)
        self._addStringProperty('specialRewardType', '')
        self._addBoolProperty('isOpening', False)
        self._addBoolProperty('isIdleGuestCVisible', False)
        self._addBoolProperty('isReloading', False)
        self._addBoolProperty('isWindowAccessible', True)
        self._addNumberProperty('streamBufferLength', 1)
        self._addBoolProperty('isForcedToEnd', False)
        self.onOpeningStart = self._addCommand('onOpeningStart')
        self.onOpeningEnd = self._addCommand('onOpeningEnd')
        self.onReloadEnd = self._addCommand('onReloadEnd')
        self.onNeedShowRewards = self._addCommand('onNeedShowRewards')
        self.onVideoOffViewReady = self._addCommand('onVideoOffViewReady')
        self.onLoadError = self._addCommand('onLoadError')
