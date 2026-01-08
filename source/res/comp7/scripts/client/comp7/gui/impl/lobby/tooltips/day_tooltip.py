# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/day_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.day_tooltip_model import DayTooltipModel
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl

class DayTooltip(ViewImpl):
    __slots__ = ('__params',)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.day_tooltip(), params=None):
        settings = ViewSettings(layoutID)
        settings.model = DayTooltipModel()
        super(DayTooltip, self).__init__(settings)
        self.__params = params

    @property
    def viewModel(self):
        return super(DayTooltip, self).getViewModel()

    def _onLoading(self):
        super(DayTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            vm.setIndex(self.__params['index'])
            vm.setIsQualification(self.__params['isQualification'])
            vm.setSeasonName(self.__params['seasonName'])
            vm.setDiff(self.__params['diff'])
            vm.setHasBattles(self.__params['hasBattles'])
            vm.setRatingPoints(self.__params['ratingPoints'])
            vm.setRankInactivityPenalty(self.__params['rankInactivityPenalty'])
            vm.setCurrentDayIndex(self.__params['currentDayIndex'])
            rank = self.__params['rank']
            if rank:
                vm.setRank(rank)
            division = self.__params['division']
            if division:
                vm.setDivision(division)
