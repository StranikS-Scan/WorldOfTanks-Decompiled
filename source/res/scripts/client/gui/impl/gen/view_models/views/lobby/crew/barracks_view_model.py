# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/barracks_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.range_model import RangeModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class BarracksViewModel(ViewModel):
    __slots__ = ('onResetFilters', 'onBuyBerth', 'onTankmanSelected', 'onTankmanRecruit', 'onTankmanDismiss', 'onPlayTankmanVoiceover', 'onTankmanRestore', 'onLoadCards', 'showHangar')

    def __init__(self, properties=7, commands=9):
        super(BarracksViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def berthsAmount(self):
        return self._getViewModel(0)

    @staticmethod
    def getBerthsAmountType():
        return RangeModel

    def getItemsAmount(self):
        return self._getNumber(1)

    def setItemsAmount(self, value):
        self._setNumber(1, value)

    def getItemsOffset(self):
        return self._getNumber(2)

    def setItemsOffset(self, value):
        self._setNumber(2, value)

    def getTankmanList(self):
        return self._getArray(3)

    def setTankmanList(self, value):
        self._setArray(3, value)

    @staticmethod
    def getTankmanListType():
        return TankmanModel

    def getIsBerthsOnSale(self):
        return self._getBool(4)

    def setIsBerthsOnSale(self, value):
        self._setBool(4, value)

    def getIsBannerVisible(self):
        return self._getBool(5)

    def setIsBannerVisible(self, value):
        self._setBool(5, value)

    def getHasFilters(self):
        return self._getBool(6)

    def setHasFilters(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(BarracksViewModel, self)._initialize()
        self._addViewModelProperty('berthsAmount', RangeModel())
        self._addNumberProperty('itemsAmount', 0)
        self._addNumberProperty('itemsOffset', 0)
        self._addArrayProperty('tankmanList', Array())
        self._addBoolProperty('isBerthsOnSale', False)
        self._addBoolProperty('isBannerVisible', False)
        self._addBoolProperty('hasFilters', False)
        self.onResetFilters = self._addCommand('onResetFilters')
        self.onBuyBerth = self._addCommand('onBuyBerth')
        self.onTankmanSelected = self._addCommand('onTankmanSelected')
        self.onTankmanRecruit = self._addCommand('onTankmanRecruit')
        self.onTankmanDismiss = self._addCommand('onTankmanDismiss')
        self.onPlayTankmanVoiceover = self._addCommand('onPlayTankmanVoiceover')
        self.onTankmanRestore = self._addCommand('onTankmanRestore')
        self.onLoadCards = self._addCommand('onLoadCards')
        self.showHangar = self._addCommand('showHangar')
