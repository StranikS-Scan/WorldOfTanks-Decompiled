# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/multiple_boxes_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.bonus_model import BonusModel

class MultipleBoxesRewardsViewModel(ViewModel):
    __slots__ = ('onOpen', 'onGoBack', 'onPreview', 'onBuyBoxes', 'onAnimationStateChanged', 'onVideoPlaying', 'onClose')

    def __init__(self, properties=11, commands=7):
        super(MultipleBoxesRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getBoxCategory(self):
        return self._getString(1)

    def setBoxCategory(self, value):
        self._setString(1, value)

    def getIsReopen(self):
        return self._getBool(2)

    def setIsReopen(self, value):
        self._setBool(2, value)

    def getUseExternal(self):
        return self._getBool(3)

    def setUseExternal(self, value):
        self._setBool(3, value)

    def getBoxesCount(self):
        return self._getNumber(4)

    def setBoxesCount(self, value):
        self._setNumber(4, value)

    def getBoxesCountToGuaranteed(self):
        return self._getNumber(5)

    def setBoxesCountToGuaranteed(self, value):
        self._setNumber(5, value)

    def getOpeningCount(self):
        return self._getNumber(6)

    def setOpeningCount(self, value):
        self._setNumber(6, value)

    def getIsAnimationActive(self):
        return self._getBool(7)

    def setIsAnimationActive(self, value):
        self._setBool(7, value)

    def getIsAwaitingResponse(self):
        return self._getBool(8)

    def setIsAwaitingResponse(self, value):
        self._setBool(8, value)

    def getIsWindowAccessible(self):
        return self._getBool(9)

    def setIsWindowAccessible(self, value):
        self._setBool(9, value)

    def getBonuses(self):
        return self._getArray(10)

    def setBonuses(self, value):
        self._setArray(10, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(MultipleBoxesRewardsViewModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addStringProperty('boxCategory', '')
        self._addBoolProperty('isReopen', False)
        self._addBoolProperty('useExternal', False)
        self._addNumberProperty('boxesCount', 0)
        self._addNumberProperty('boxesCountToGuaranteed', 0)
        self._addNumberProperty('openingCount', 0)
        self._addBoolProperty('isAnimationActive', False)
        self._addBoolProperty('isAwaitingResponse', False)
        self._addBoolProperty('isWindowAccessible', False)
        self._addArrayProperty('bonuses', Array())
        self.onOpen = self._addCommand('onOpen')
        self.onGoBack = self._addCommand('onGoBack')
        self.onPreview = self._addCommand('onPreview')
        self.onBuyBoxes = self._addCommand('onBuyBoxes')
        self.onAnimationStateChanged = self._addCommand('onAnimationStateChanged')
        self.onVideoPlaying = self._addCommand('onVideoPlaying')
        self.onClose = self._addCommand('onClose')
