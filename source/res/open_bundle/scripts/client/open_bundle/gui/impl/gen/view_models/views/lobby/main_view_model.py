# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/impl/gen/view_models/views/lobby/main_view_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.common.price_item_model import PriceItemModel
from open_bundle.gui.impl.gen.view_models.views.lobby.bonus_model import BonusModel
from open_bundle.gui.impl.gen.view_models.views.lobby.cell_model import CellModel

class MainViewModel(ViewModel):
    __slots__ = ('play', 'onItemShown', 'showPreview', 'resetInterruption')

    def __init__(self, properties=7, commands=4):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def stepPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getStepPriceType():
        return PriceItemModel

    def getBundleType(self):
        return self._getString(1)

    def setBundleType(self, value):
        self._setString(1, value)

    def getStartTime(self):
        return self._getNumber(2)

    def setStartTime(self, value):
        self._setNumber(2, value)

    def getFinishTime(self):
        return self._getNumber(3)

    def setFinishTime(self, value):
        self._setNumber(3, value)

    def getIsInterrupted(self):
        return self._getBool(4)

    def setIsInterrupted(self, value):
        self._setBool(4, value)

    def getCells(self):
        return self._getArray(5)

    def setCells(self, value):
        self._setArray(5, value)

    @staticmethod
    def getCellsType():
        return CellModel

    def getFixedReward(self):
        return self._getArray(6)

    def setFixedReward(self, value):
        self._setArray(6, value)

    @staticmethod
    def getFixedRewardType():
        return BonusModel

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('stepPrice', PriceItemModel())
        self._addStringProperty('bundleType', '')
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('finishTime', 0)
        self._addBoolProperty('isInterrupted', False)
        self._addArrayProperty('cells', Array())
        self._addArrayProperty('fixedReward', Array())
        self.play = self._addCommand('play')
        self.onItemShown = self._addCommand('onItemShown')
        self.showPreview = self._addCommand('showPreview')
        self.resetInterruption = self._addCommand('resetInterruption')
