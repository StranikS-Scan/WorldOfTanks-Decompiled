# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/submodel_presenters/comp7_progression.py
from __future__ import absolute_import
import typing
from shared_utils import findFirst
from comp7.gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS as COMP7_TOOLTIPS
from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel, WarningType
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.gen.view_models.views.lobby.progression_item_model import ProgressionItemModel
from comp7.gui.impl.gen.view_models.views.lobby.season_model import SeasonState
from comp7.gui.impl.gen.view_models.views.lobby.year_model import YearState
from comp7.gui.impl.lobby.battle_results.submodel_presenters.battle_info import isDeserter
from comp7.gui.impl.lobby.comp7_helpers import comp7_shared, comp7_model_helpers
from comp7.gui.impl.lobby.meta_view import meta_view_helper
from comp7_common.comp7_constants import ARENA_GUI_TYPE
from comp7_core.gui.impl.lobby.comp7_core_helpers import comp7_core_model_helpers
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.battle_results.stats_ctrl import BattleResults
    from frameworks.wulf import ViewModel

class Comp7ProgressionSubPresenter(BattleResultsSubPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def getViewModelType(cls):
        return Comp7BattleResultsViewModel

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        self.__packProgressionData(viewModel, battleResults)
        comp7_core_model_helpers.setScheduleInfo(viewModel.scheduleInfo, self.__comp7Controller, COMP7_TOOLTIPS.COMP7_CALENDAR_DAY_INFO, SeasonState, YearState, SeasonName)
        viewModel.setWarningType(WarningType.LEAVE if isDeserter(battleResults.reusable) else WarningType.NONE)

    def __packProgressionData(self, model, battleResults):
        avatarResults = battleResults.results['personal']['avatar']
        prevRating = avatarResults.get('comp7Rating', 0)
        ratingDelta = avatarResults.get('comp7RatingDelta', 0)
        rank, _, _ = avatarResults.get('comp7Rank', (0, 0, 0))
        currentRating = max(prevRating + ratingDelta, 0)
        self.__setUnRankedBattleTypes(model)
        self.__setProgressionItems(model, currentRating)
        isQualActive = battleResults.results['personal']['avatar'].get('comp7QualActive', False)
        if isQualActive:
            self.__setQualificationData(model, battleResults)
        else:
            self.__setRankData(model, prevRating, currentRating, ratingDelta, rank)

    @dependency.replace_none_kwargs(comp7Controller=IComp7Controller)
    def __setQualificationData(self, model, battleResults, comp7Controller=None):
        comp7QualBattleIndex = battleResults.results['personal']['avatar'].get('comp7QualBattleIndex', False)
        model.qualificationModel.setIsActive(True)
        model.qualificationModel.setBattlesCount(comp7QualBattleIndex + 1)
        model.qualificationModel.setMaxBattlesCount(comp7Controller.qualificationBattlesNumber)
        model.qualificationModel.setIsRatingCalculation(comp7Controller.isQualificationResultsProcessing())

    def __setRankData(self, model, prevRating, currentRating, ratingDelta, rank):
        model.setRatingDelta(ratingDelta)
        model.setPreviousScore(prevRating)
        model.setCurrentScore(currentRating)
        ranksConfig = self.__comp7Controller.getRanksConfig()
        if rank != meta_view_helper.getEliteRank():
            division = findFirst(lambda d: currentRating in d.range, ranksConfig.divisions)
            if division is not None:
                rank = division.rank
        rankIdx = ranksConfig.ranksOrder.index(rank)
        model.setCurrentItemIndex(rankIdx)
        comp7_model_helpers.setElitePercentage(model)
        return

    def __setProgressionItems(self, model, rating):
        ranksConfig = self.__comp7Controller.getRanksConfig()
        itemsArray = model.getProgressionItems()
        itemsArray.clear()
        for rank in ranksConfig.ranksOrder:
            itemModel = ProgressionItemModel()
            itemModel.setHasRankInactivity(comp7_shared.hasRankInactivity(rank))
            meta_view_helper.setRankData(itemModel, rank, ranksConfig)
            meta_view_helper.setDivisionData(itemModel, meta_view_helper.getRankDivisions(rank, ranksConfig), rating)
            itemsArray.addViewModel(itemModel)

        itemsArray.invalidate()

    def __setUnRankedBattleTypes(self, model):
        unrankedBattleTypes = model.getUnRankedBattleTypes()
        unrankedBattleTypes.clear()
        for unrankedBattleType in (ARENA_GUI_TYPE.TOURNAMENT_COMP7, ARENA_GUI_TYPE.TRAINING_COMP7):
            unrankedBattleTypes.addNumber(unrankedBattleType)

        unrankedBattleTypes.invalidate()
