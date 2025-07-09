# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/barracks_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.range_model import RangeModel
from gui.impl.gen.view_models.views.lobby.crew.tankman_model import TankmanModel

class BarracksViewModel(ViewModel):
    __slots__ = ('onResetFilters', 'onBuyBerth', 'onTankmanSelected', 'onTankmanRecruit', 'onTankmanDismiss', 'onPlayTankmanVoiceover', 'onTankmanRestore', 'onLoadCards', 'showHangar', 'onTankmanSelectedChange')

    def __init__(self, properties=12, commands=10):
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

    def getSelectedTankmanList(self):
        return self._getArray(4)

    def setSelectedTankmanList(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSelectedTankmanListType():
        return int

    def getIsSelectedLimitReached(self):
        return self._getBool(5)

    def setIsSelectedLimitReached(self, value):
        self._setBool(5, value)

    def getIsBerthsOnSale(self):
        return self._getBool(6)

    def setIsBerthsOnSale(self, value):
        self._setBool(6, value)

    def getHasFilters(self):
        return self._getBool(7)

    def setHasFilters(self, value):
        self._setBool(7, value)

    def getHeaderTitle(self):
        return self._getString(8)

    def setHeaderTitle(self, value):
        self._setString(8, value)

    def getIsSelectedMode(self):
        return self._getBool(9)

    def setIsSelectedMode(self, value):
        self._setBool(9, value)

    def getHeadersIndexes(self):
        return self._getArray(10)

    def setHeadersIndexes(self, value):
        self._setArray(10, value)

    @staticmethod
    def getHeadersIndexesType():
        return int

    def getIsAllTankmanFilter(self):
        return self._getBool(11)

    def setIsAllTankmanFilter(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(BarracksViewModel, self)._initialize()
        self._addViewModelProperty('berthsAmount', RangeModel())
        self._addNumberProperty('itemsAmount', 0)
        self._addNumberProperty('itemsOffset', 0)
        self._addArrayProperty('tankmanList', Array())
        self._addArrayProperty('selectedTankmanList', Array())
        self._addBoolProperty('isSelectedLimitReached', False)
        self._addBoolProperty('isBerthsOnSale', False)
        self._addBoolProperty('hasFilters', False)
        self._addStringProperty('headerTitle', '')
        self._addBoolProperty('isSelectedMode', False)
        self._addArrayProperty('headersIndexes', Array())
        self._addBoolProperty('isAllTankmanFilter', True)
        self.onResetFilters = self._addCommand('onResetFilters')
        self.onBuyBerth = self._addCommand('onBuyBerth')
        self.onTankmanSelected = self._addCommand('onTankmanSelected')
        self.onTankmanRecruit = self._addCommand('onTankmanRecruit')
        self.onTankmanDismiss = self._addCommand('onTankmanDismiss')
        self.onPlayTankmanVoiceover = self._addCommand('onPlayTankmanVoiceover')
        self.onTankmanRestore = self._addCommand('onTankmanRestore')
        self.onLoadCards = self._addCommand('onLoadCards')
        self.showHangar = self._addCommand('showHangar')
        self.onTankmanSelectedChange = self._addCommand('onTankmanSelectedChange')
