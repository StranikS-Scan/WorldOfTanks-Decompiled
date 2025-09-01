# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/progression_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.progression_tooltip_model import ProgressionTooltipModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class ProgressionTooltip(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.progression_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = ProgressionTooltipModel()
        super(ProgressionTooltip, self).__init__(settings)

    def _getEvents(self):
        return ((self.__comp7Controller.onRankUpdated, self.__updateData),
         (self.__comp7Controller.onModeConfigChanged, self.__updateData),
         (self.__comp7Controller.onComp7RanksConfigChanged, self.__updateData),
         (self.__comp7Controller.onQualificationBattlesUpdated, self.__updateData),
         (self.__comp7Controller.onQualificationStateUpdated, self.__updateData))

    @property
    def viewModel(self):
        return super(ProgressionTooltip, self).getViewModel()

    def _onLoading(self):
        super(ProgressionTooltip, self)._onLoading()
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum(self.__comp7Controller, SeasonName))
            if self.__comp7Controller.isQualificationActive():
                self.__updateQualificationdata(vm)
            else:
                self.__updateProgressionData(vm)

    def __updateQualificationdata(self, model):
        comp7_qualification_helpers.setQualificationInfo(model.qualificationModel)
        comp7_qualification_helpers.setQualificationBattles(model.qualificationModel.getBattles())

    def __updateProgressionData(self, model):
        division = comp7_shared.getPlayerDivision()
        rank = comp7_shared.getRankEnumValue(division)
        divisionByRank = comp7_shared.getPlayerDivisionByRankAndIndex(rank, division.index)
        model.setRank(rank)
        model.setCurrentScore(self.__comp7Controller.rating)
        comp7_model_helpers.setDivisionInfo(model=model.divisionInfo, division=division)
        comp7_model_helpers.setElitePercentage(model)
        if self.__comp7Controller.hasActiveSeason():
            model.setHasRankInactivity(comp7_shared.hasRankInactivity(rank))
            model.setRankInactivityPointsCount(divisionByRank.ratingPointsPenalty)
            model.setEarnedRankInactivityPerBattle(divisionByRank.activityPointsPerBattle)
            model.setRankInactivityCount(self.__comp7Controller.activityPoints)
        else:
            model.setHasRankInactivity(False)
