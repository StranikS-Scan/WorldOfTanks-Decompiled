# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/battle_result_stat_tooltip.py
from frameworks.wulf.view.view import ViewSettings
from gui.impl.gen import R
from story_mode.gui.impl.gen.view_models.views.lobby.battle_result_stat_tooltip_model import BattleResultStatTooltipModel, StatEnum, DetailedStatModel
from gui.impl.pub import ViewImpl

class BattleResultStatTooltip(ViewImpl):
    __slots__ = ('__stat', '__detailedStats')

    def __init__(self, stat, detailedStats):
        settings = ViewSettings(R.views.story_mode.lobby.BattleResultStatTooltip(), model=BattleResultStatTooltipModel())
        super(BattleResultStatTooltip, self).__init__(settings)
        self.__stat = stat
        self.__detailedStats = detailedStats

    @property
    def viewModel(self):
        return super(BattleResultStatTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BattleResultStatTooltip, self)._onLoading(*args, **kwargs)
        self.__fillViewModel()

    def __fillViewModel(self):
        self.viewModel.setStat(self.__stat)
        detailedStats = self.viewModel.getDetailedStats()
        for value, text in self.__detailedStats:
            detailedStat = DetailedStatModel()
            detailedStat.setValue(value)
            detailedStat.setText(text)
            detailedStats.addViewModel(detailedStat)
