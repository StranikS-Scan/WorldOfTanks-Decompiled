# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_break_decorations_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.ui_kit.filter_counter_model import FilterCounterModel
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_parts_tip_element_model import NewYearPartsTipElementModel

class NewYearBreakDecorationsViewModel(ViewModel):
    __slots__ = ('onQuestsBtnClick', 'onCelebrityBtnClick', 'onFilterResetBtnClick', 'onSelectedAllChanged', 'onSlotStatusIsNewChanged', 'onBreakDecorationsBtnClick', 'onBreakAnimationComplete', 'onViewResized', 'onBackBtnClick')

    def __init__(self, properties=13, commands=9):
        super(NewYearBreakDecorationsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def slotsList(self):
        return self._getViewModel(0)

    @property
    def shardsTip(self):
        return self._getViewModel(1)

    @property
    def filterCounter(self):
        return self._getViewModel(2)

    def getShardsCount(self):
        return self._getNumber(3)

    def setShardsCount(self, value):
        self._setNumber(3, value)

    def getSelectedDecorationsCount(self):
        return self._getNumber(4)

    def setSelectedDecorationsCount(self, value):
        self._setNumber(4, value)

    def getCurrentBreakDecorations(self):
        return self._getNumber(5)

    def setCurrentBreakDecorations(self, value):
        self._setNumber(5, value)

    def getTotalRegisterDecorations(self):
        return self._getNumber(6)

    def setTotalRegisterDecorations(self, value):
        self._setNumber(6, value)

    def getDecorationSelectedAll(self):
        return self._getBool(7)

    def setDecorationSelectedAll(self, value):
        self._setBool(7, value)

    def getDecorationSelectedAllEnable(self):
        return self._getBool(8)

    def setDecorationSelectedAllEnable(self, value):
        self._setBool(8, value)

    def getShowDummy(self):
        return self._getBool(9)

    def setShowDummy(self, value):
        self._setBool(9, value)

    def getShowNotFoundPage(self):
        return self._getBool(10)

    def setShowNotFoundPage(self, value):
        self._setBool(10, value)

    def getShowBackBtn(self):
        return self._getBool(11)

    def setShowBackBtn(self, value):
        self._setBool(11, value)

    def getExpectedShardsCount(self):
        return self._getNumber(12)

    def setExpectedShardsCount(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(NewYearBreakDecorationsViewModel, self)._initialize()
        self._addViewModelProperty('slotsList', UserListModel())
        self._addViewModelProperty('shardsTip', NewYearPartsTipElementModel())
        self._addViewModelProperty('filterCounter', FilterCounterModel())
        self._addNumberProperty('shardsCount', -1)
        self._addNumberProperty('selectedDecorationsCount', 0)
        self._addNumberProperty('currentBreakDecorations', 0)
        self._addNumberProperty('totalRegisterDecorations', 0)
        self._addBoolProperty('decorationSelectedAll', False)
        self._addBoolProperty('decorationSelectedAllEnable', True)
        self._addBoolProperty('showDummy', False)
        self._addBoolProperty('showNotFoundPage', False)
        self._addBoolProperty('showBackBtn', False)
        self._addNumberProperty('expectedShardsCount', 0)
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onCelebrityBtnClick = self._addCommand('onCelebrityBtnClick')
        self.onFilterResetBtnClick = self._addCommand('onFilterResetBtnClick')
        self.onSelectedAllChanged = self._addCommand('onSelectedAllChanged')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
        self.onBreakDecorationsBtnClick = self._addCommand('onBreakDecorationsBtnClick')
        self.onBreakAnimationComplete = self._addCommand('onBreakAnimationComplete')
        self.onViewResized = self._addCommand('onViewResized')
        self.onBackBtnClick = self._addCommand('onBackBtnClick')
