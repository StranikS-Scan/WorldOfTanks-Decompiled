# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/rank_indicator_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.rank_indicator_tooltip_model import RankIndicatorTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class RankIndicatorTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.rank_indicator_tooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = RankIndicatorTooltipModel()
        super(RankIndicatorTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(RankIndicatorTooltip, self).getViewModel()

    def _onLoading(self):
        super(RankIndicatorTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setStatisticsMode(self.__params['statisticsMode'])
            vm.setRank(self.__params['rank'])
            vm.setSeasonName(self.__params['seasonName'])
            vm.setMaxAchievedRatingPoints(self.__params['maxAchievedRatingPoints'])
            division = self.__params['division']
            ratingPoints = self.__params['ratingPoints']
            diff = self.__params['diff']
            dayOfMaxRatingIndex = self.__params['dayOfMaxRatingIndex']
            if division:
                vm.setDivision(division)
            if ratingPoints:
                vm.setRatingPoints(ratingPoints)
            if diff:
                vm.setDiff(diff)
            if dayOfMaxRatingIndex:
                vm.setDayOfMaxRatingIndex(dayOfMaxRatingIndex)
