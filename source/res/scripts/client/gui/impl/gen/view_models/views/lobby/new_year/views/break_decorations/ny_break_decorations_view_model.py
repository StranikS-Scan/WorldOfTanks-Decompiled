# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/break_decorations/ny_break_decorations_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.filter_counter_model import FilterCounterModel
from gui.impl.gen.view_models.views.lobby.new_year.views.break_decorations.ny_break_shards_tip_model import NyBreakShardsTipModel

class ShowState(IntEnum):
    TOYS_VISIBLE = 0
    TOYS_EMPTY = 1
    TOYS_NOT_FOUND = 2


class NyBreakDecorationsViewModel(ViewModel):
    __slots__ = ('onSelectedAllChanged', 'onSlotStatusIsNewChanged', 'onBreakDecorationsBtnClick', 'onBreakAnimationComplete', 'onQuestsBtnClick', 'onBoxBtnClick', 'onDecorationClicked')

    def __init__(self, properties=10, commands=7):
        super(NyBreakDecorationsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def shardsTip(self):
        return self._getViewModel(0)

    @staticmethod
    def getShardsTipType():
        return NyBreakShardsTipModel

    @property
    def filterCounter(self):
        return self._getViewModel(1)

    @staticmethod
    def getFilterCounterType():
        return FilterCounterModel

    def getShardsCount(self):
        return self._getNumber(2)

    def setShardsCount(self, value):
        self._setNumber(2, value)

    def getSelectedDecorationsCount(self):
        return self._getNumber(3)

    def setSelectedDecorationsCount(self, value):
        self._setNumber(3, value)

    def getIsAllSelected(self):
        return self._getBool(4)

    def setIsAllSelected(self, value):
        self._setBool(4, value)

    def getIsBreakInitiated(self):
        return self._getBool(5)

    def setIsBreakInitiated(self, value):
        self._setBool(5, value)

    def getShowState(self):
        return ShowState(self._getNumber(6))

    def setShowState(self, value):
        self._setNumber(6, value.value)

    def getExpectedShardsCount(self):
        return self._getNumber(7)

    def setExpectedShardsCount(self, value):
        self._setNumber(7, value)

    def getDecorationsJSON(self):
        return self._getString(8)

    def setDecorationsJSON(self, value):
        self._setString(8, value)

    def getSelectedIndicesJSON(self):
        return self._getString(9)

    def setSelectedIndicesJSON(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(NyBreakDecorationsViewModel, self)._initialize()
        self._addViewModelProperty('shardsTip', NyBreakShardsTipModel())
        self._addViewModelProperty('filterCounter', FilterCounterModel())
        self._addNumberProperty('shardsCount', -1)
        self._addNumberProperty('selectedDecorationsCount', 0)
        self._addBoolProperty('isAllSelected', False)
        self._addBoolProperty('isBreakInitiated', False)
        self._addNumberProperty('showState')
        self._addNumberProperty('expectedShardsCount', 0)
        self._addStringProperty('decorationsJSON', '')
        self._addStringProperty('selectedIndicesJSON', '')
        self.onSelectedAllChanged = self._addCommand('onSelectedAllChanged')
        self.onSlotStatusIsNewChanged = self._addCommand('onSlotStatusIsNewChanged')
        self.onBreakDecorationsBtnClick = self._addCommand('onBreakDecorationsBtnClick')
        self.onBreakAnimationComplete = self._addCommand('onBreakAnimationComplete')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onBoxBtnClick = self._addCommand('onBoxBtnClick')
        self.onDecorationClicked = self._addCommand('onDecorationClicked')
