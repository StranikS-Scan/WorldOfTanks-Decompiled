# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_craft_view_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class NewYearCraftViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBackBtnClick', 'onFilterChanged', 'onGetPartsBtnClick', 'onCraftBtnClick', 'onAddCraftDecoration')

    @property
    def craftCarousel(self):
        return self._getViewModel(0)

    def getBackViewName(self):
        return self._getResource(1)

    def setBackViewName(self, value):
        self._setResource(1, value)

    def getPartsCount(self):
        return self._getNumber(2)

    def setPartsCount(self, value):
        self._setNumber(2, value)

    def getCraftPrice(self):
        return self._getNumber(3)

    def setCraftPrice(self, value):
        self._setNumber(3, value)

    def getPriceAnimTrigger(self):
        return self._getBool(4)

    def setPriceAnimTrigger(self, value):
        self._setBool(4, value)

    def getNotEnoughAnimTrigger(self):
        return self._getBool(5)

    def setNotEnoughAnimTrigger(self, value):
        self._setBool(5, value)

    def getCurrentLevelIndex(self):
        return self._getNumber(6)

    def setCurrentLevelIndex(self, value):
        self._setNumber(6, value)

    def getCurrentSettingIndex(self):
        return self._getNumber(7)

    def setCurrentSettingIndex(self, value):
        self._setNumber(7, value)

    def getCurrentTypeIndex(self):
        return self._getNumber(8)

    def setCurrentTypeIndex(self, value):
        self._setNumber(8, value)

    def getCraftIcon(self):
        return self._getString(9)

    def setCraftIcon(self, value):
        self._setString(9, value)

    def getLevelBtnTooltips(self):
        return self._getArray(10)

    def setLevelBtnTooltips(self, value):
        self._setArray(10, value)

    def getSettingBtnTooltips(self):
        return self._getArray(11)

    def setSettingBtnTooltips(self, value):
        self._setArray(11, value)

    def getTypeBtnTooltips(self):
        return self._getArray(12)

    def setTypeBtnTooltips(self, value):
        self._setArray(12, value)

    def getDecorationTypes(self):
        return self._getArray(13)

    def setDecorationTypes(self, value):
        self._setArray(13, value)

    def getCustomizationObjects(self):
        return self._getArray(14)

    def setCustomizationObjects(self, value):
        self._setArray(14, value)

    def getLineByTypeIndices(self):
        return self._getArray(15)

    def setLineByTypeIndices(self, value):
        self._setArray(15, value)

    def getTypeByLineIndices(self):
        return self._getArray(16)

    def setTypeByLineIndices(self, value):
        self._setArray(16, value)

    def getDisposeEnabled(self):
        return self._getBool(17)

    def setDisposeEnabled(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(NewYearCraftViewModel, self)._initialize()
        self._addViewModelProperty('craftCarousel', ListModel())
        self._addResourceProperty('backViewName', Resource.INVALID)
        self._addNumberProperty('partsCount', -1)
        self._addNumberProperty('craftPrice', 0)
        self._addBoolProperty('priceAnimTrigger', False)
        self._addBoolProperty('notEnoughAnimTrigger', False)
        self._addNumberProperty('currentLevelIndex', 0)
        self._addNumberProperty('currentSettingIndex', 0)
        self._addNumberProperty('currentTypeIndex', 0)
        self._addStringProperty('craftIcon', '')
        self._addArrayProperty('levelBtnTooltips', Array())
        self._addArrayProperty('settingBtnTooltips', Array())
        self._addArrayProperty('typeBtnTooltips', Array())
        self._addArrayProperty('decorationTypes', Array())
        self._addArrayProperty('customizationObjects', Array())
        self._addArrayProperty('lineByTypeIndices', Array())
        self._addArrayProperty('typeByLineIndices', Array())
        self._addBoolProperty('disposeEnabled', False)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onFilterChanged = self._addCommand('onFilterChanged')
        self.onGetPartsBtnClick = self._addCommand('onGetPartsBtnClick')
        self.onCraftBtnClick = self._addCommand('onCraftBtnClick')
        self.onAddCraftDecoration = self._addCommand('onAddCraftDecoration')
