# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/submodels/has_boxes_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.box_info_model import BoxInfoModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.submodels.statistics_model import StatisticsModel

class HasBoxesViewModel(ViewModel):
    __slots__ = ('onInfoOpen', 'onBoxesOpen', 'onBuyBoxes', 'onAnimationStateChanged', 'onOpeningOptionChanged', 'onBoxOptionChanged', 'onClose', 'onResetError')

    def __init__(self, properties=11, commands=8):
        super(HasBoxesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def statistics(self):
        return self._getViewModel(0)

    @staticmethod
    def getStatisticsType():
        return StatisticsModel

    def getEventName(self):
        return self._getString(1)

    def setEventName(self, value):
        self._setString(1, value)

    def getBoxesInfo(self):
        return self._getArray(2)

    def setBoxesInfo(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBoxesInfoType():
        return BoxInfoModel

    def getOpeningOptions(self):
        return self._getArray(3)

    def setOpeningOptions(self, value):
        self._setArray(3, value)

    @staticmethod
    def getOpeningOptionsType():
        return int

    def getSelectedBoxOption(self):
        return self._getNumber(4)

    def setSelectedBoxOption(self, value):
        self._setNumber(4, value)

    def getSelectedOpeningOption(self):
        return self._getNumber(5)

    def setSelectedOpeningOption(self, value):
        self._setNumber(5, value)

    def getIsAnimationActive(self):
        return self._getBool(6)

    def setIsAnimationActive(self, value):
        self._setBool(6, value)

    def getIsAwaitingResponse(self):
        return self._getBool(7)

    def setIsAwaitingResponse(self, value):
        self._setBool(7, value)

    def getIsError(self):
        return self._getBool(8)

    def setIsError(self, value):
        self._setBool(8, value)

    def getUseExternal(self):
        return self._getBool(9)

    def setUseExternal(self, value):
        self._setBool(9, value)

    def getUseStats(self):
        return self._getBool(10)

    def setUseStats(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(HasBoxesViewModel, self)._initialize()
        self._addViewModelProperty('statistics', StatisticsModel())
        self._addStringProperty('eventName', '')
        self._addArrayProperty('boxesInfo', Array())
        self._addArrayProperty('openingOptions', Array())
        self._addNumberProperty('selectedBoxOption', 0)
        self._addNumberProperty('selectedOpeningOption', 0)
        self._addBoolProperty('isAnimationActive', False)
        self._addBoolProperty('isAwaitingResponse', False)
        self._addBoolProperty('isError', False)
        self._addBoolProperty('useExternal', False)
        self._addBoolProperty('useStats', True)
        self.onInfoOpen = self._addCommand('onInfoOpen')
        self.onBoxesOpen = self._addCommand('onBoxesOpen')
        self.onBuyBoxes = self._addCommand('onBuyBoxes')
        self.onAnimationStateChanged = self._addCommand('onAnimationStateChanged')
        self.onOpeningOptionChanged = self._addCommand('onOpeningOptionChanged')
        self.onBoxOptionChanged = self._addCommand('onBoxOptionChanged')
        self.onClose = self._addCommand('onClose')
        self.onResetError = self._addCommand('onResetError')
