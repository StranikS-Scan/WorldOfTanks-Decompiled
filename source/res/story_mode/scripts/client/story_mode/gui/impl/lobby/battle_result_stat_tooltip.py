# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/battle_result_stat_tooltip.py
from typing import Optional, Tuple
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from story_mode.gui.impl.gen.view_models.views.lobby.battle_result_stat_tooltip_model import BattleResultStatTooltipModel, StatEnum, DetailedStatModel
from gui.impl.pub import ViewImpl

class BattleResultStatTooltip(ViewImpl):
    __slots__ = ('__stat', '__detailedStats', '__infoList')

    def __init__(self, stat, detailedStats, infoList):
        settings = ViewSettings(R.views.story_mode.mono.lobby.tooltips.battle_result_stat_tooltip(), model=BattleResultStatTooltipModel())
        super(BattleResultStatTooltip, self).__init__(settings)
        self.__stat = stat
        self.__detailedStats = detailedStats
        self.__infoList = infoList

    @property
    def viewModel(self):
        return super(BattleResultStatTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultStatTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self.__fillViewModel(vm)

    def __fillViewModel(self, vm):
        vm.setStat(self.__stat)
        detailedStats = vm.getDetailedStats()
        for value, text in self.__detailedStats:
            detailedStat = DetailedStatModel()
            detailedStat.setValue(value)
            detailedStat.setText(text)
            detailedStats.addViewModel(detailedStat)

        vm.getInfoList().clear()
        for text in self.__infoList:
            vm.getInfoList().addString(text)
