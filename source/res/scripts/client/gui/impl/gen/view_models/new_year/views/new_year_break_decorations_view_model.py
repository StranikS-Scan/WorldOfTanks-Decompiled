# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/views/new_year_break_decorations_view_model.py
import typing
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.new_year.views.new_year_parts_tip_element_model import NewYearPartsTipElementModel
from gui.impl.gen.view_models.ui_kit.filter_counter_model import FilterCounterModel

class NewYearBreakDecorationsViewModel(ViewModel):
    __slots__ = ('onCloseBtnClick', 'onBackBtnClick', 'onQuestsBtnClick', 'onFilterResetBtnClick', 'onSelectedAllChanged', 'onSlotStatusIsNewChanged', 'onBreakDecorationsBtnClick', 'onBreakAnimationComplete', 'onCraftBtnClick')

    @property
    def slotsList(self):
        return self._getViewModel(0)

    @property
    def partsTip(self):
        return self._getViewModel(1)

    @property
    def filterCounter(self):
        return self._getViewModel(2)

    def getBackViewName(self):
        return self._getResource(3)

    def setBackViewName(self, value):
        self._setResource(3, value)

    def getPartsCount(self):
        return self._getNumber(4)

    def setPartsCount(self, value):
        self._setNumber(4, value)

    def getSelectedDecorationsCount(self):
        return self._getNumber(5)

    def setSelectedDecorationsCount(self, value):
        self._setNumber(5, value)

    def getCurrentBreakDecorations(self):
        return self._getNumber(6)

    def setCurrentBreakDecorations(self, value):
        self._setNumber(6, value)

    def getTotalRegisterDecorations(self):
        return self._getNumber(7)

    def setTotalRegisterDecorations(self, value):
        self._setNumber(7, value)

    def getDecorationSelectedAll(self):
        return self._getBool(8)

    def setDecorationSelectedAll(self, value):
        self._setBool(8, value)

    def getDecorationSelectedAllEnable(self):
        return self._getBool(9)

    def setDecorationSelectedAllEnable(self, value):
        self._setBool(9, value)

    def getShowDummy(self):
        return self._getBool(10)

    def setShowDummy(self, value):
        self._setBool(10, value)

    def getShowNotFoundPage(self):
        return self._getBool(11)

    def setShowNotFoundPage(self, value):
        self._setBool(11, value)

    def getExpectedPartsCount(self):
        return self._getNumber(12)

    def setExpectedPartsCount(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(NewYearBreakDecorationsViewModel, self)._initialize()
        self._addViewModelProperty('slotsList', UserListModel())
        self._addViewModelProperty('partsTip', NewYearPartsTipElementModel())
        self._addViewModelProperty('filterCounter', FilterCounterModel())
        self._addResourceProperty('backViewName', Resource.INVALID)
        self._addNumberProperty('partsCount', -1)
        self._addNumberProperty('selectedDecorationsCount', 0)
        self._addNumberProperty('currentBreakDecorations', 0)
        self._addNumberProperty('totalRegisterDecorations', 0)
        self._addBoolProperty('decorationSelectedAll', False)
        self._addBoolProperty('decorationSelectedAllEnable', True)
        self._addBoolProperty('showDummy', False)
        self._addBoolProperty('showNotFoundPage', False)
        self._addNumberProperty('expectedPartsCount', 0)
        self.onCloseBtnClick = self._addCommand('onCloseBtnClick')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onFilterResetBtnClick = self._addCommand('onFilterResetBtnClick')
        self.onSelectedAllChanged = self._addCommand('onSelectedAllChanged')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
        self.onBreakDecorationsBtnClick = self._addCommand('onBreakDecorationsBtnClick')
        self.onBreakAnimationComplete = self._addCommand('onBreakAnimationComplete')
        self.onCraftBtnClick = self._addCommand('onCraftBtnClick')
