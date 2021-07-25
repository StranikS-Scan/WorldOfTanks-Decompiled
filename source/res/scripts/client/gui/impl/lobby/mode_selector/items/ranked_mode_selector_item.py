# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/ranked_mode_selector_item.py
import typing
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.constants import ModeSelectorRewardID
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from helpers import dependency, int2roman, time_utils
from skeletons.gui.game_control import IRankedBattlesController
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_ranked_model import ModeSelectorRankedModel
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_ranked_widget_model import ModeSelectorRankedWidgetModel
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_rank_model import ModeSelectorRankModel
    from gui.ranked_battles.ranked_models import Rank
CALENDAR_ICON = ' %(calendarIcon)'

class RankedModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorRankedModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.RANKED
    __rankedBattleController = dependency.instance(IRankedBattlesController)

    @property
    def viewModel(self):
        return super(RankedModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(RankedModeSelectorItem, self)._onInitializing()
        self.__onGameModeUpdated()
        self.__rankedBattleController.onGameModeStatusUpdated += self.__onGameModeUpdated
        self.__rankedBattleController.onUpdated += self.__onGameModeUpdated
        self._addReward(ModeSelectorRewardID.BONES)

    def _onDisposing(self):
        self.__rankedBattleController.onGameModeStatusUpdated -= self.__onGameModeUpdated
        self.__rankedBattleController.onUpdated -= self.__onGameModeUpdated

    def _getDisabledTooltipText(self):
        if self.__rankedBattleController.isUnset():
            return backport.text(R.strings.menu.headerButtons.battle.types.ranked.availability.notSet())
        return backport.text(R.strings.menu.headerButtons.battle.types.ranked.availability.frozen()) if self.__rankedBattleController.isFrozen() else super(RankedModeSelectorItem, self)._getDisabledTooltipText()

    def __onGameModeUpdated(self, *_):
        statusText = self.__getRankedStatus()
        timeLeft = self.__getTimeLeft()
        with self.viewModel.transaction() as vm:
            vm.setEventName(self.__getRankedName())
            vm.setStatus(statusText)
            vm.setTimeLeft(str(timeLeft))
            self.__fillRankedWidget(vm.widget)

    def __getRankedName(self):
        currentSeason = self.__rankedBattleController.getCurrentSeason()
        return self.__getRankedBattlesSeasonName(currentSeason) if currentSeason else ''

    def __getRankedStatus(self):
        msR = R.strings.mode_selector.event
        if self.__rankedBattleController.hasAnySeason():
            currentSeason = self.__rankedBattleController.getCurrentSeason()
            if currentSeason is None:
                nextSeason = self.__rankedBattleController.getNextSeason()
                if nextSeason is not None:
                    startDate = nextSeason.getStartDate()
                    name = self.__getRankedBattlesSeasonName(nextSeason)
                    return backport.text(msR.notStarted(), eventName=name, date=backport.getShortDateFormat(startDate))
                prevSeason = self.__rankedBattleController.getPreviousSeason()
                if prevSeason is not None:
                    name = self.__getRankedBattlesSeasonName(prevSeason)
                    return backport.text(msR.finished(), eventName=name)
        return ''

    def __getTimeLeft(self):
        currentSeason = self.__rankedBattleController.getCurrentSeason()
        return getFormattedTimeLeft(max(0, currentSeason.getEndDate() - time_utils.getServerUTCTime())) if currentSeason else ''

    def __fillRankedWidget(self, model):
        rankedController = dependency.instance(IRankedBattlesController)
        isEnabled = rankedController.isEnabled() and rankedController.getCurrentSeason() is not None
        model.setIsEnabled(isEnabled)
        if not isEnabled:
            return
        else:
            currentRankID = rankedController.getCurrentRank()[0]
            currentRank = rankedController.getRank(currentRankID)
            model.setIsFinal(currentRank.isFinal())
            if currentRank.isFinal():
                statsComposer = rankedController.getStatsComposer()
                prevWebSeasonInfo = rankedController.getClientSeasonInfo()
                currWebSeasonInfo = rankedController.getWebSeasonProvider().seasonInfo
                if currWebSeasonInfo.league == UNDEFINED_LEAGUE_ID:
                    currWebSeasonInfo = prevWebSeasonInfo
                currLeagueID = currWebSeasonInfo.league
                currEfficiency = statsComposer.currentSeasonEfficiency.efficiency
                currEfficiencyDiff = statsComposer.currentSeasonEfficiencyDiff
                currPosition = currWebSeasonInfo.position
                model.setLeagueID(currLeagueID)
                if currEfficiency:
                    model.setEfficiency(currEfficiency)
                if currEfficiencyDiff:
                    model.setEfficiencyDiff(currEfficiencyDiff)
                if currPosition:
                    model.setPosition(currPosition)
                model.setIsEfficiencyUnavailable(not currEfficiency)
                model.setIsPositionUnavailable(not currPosition)
                self.__fillRankData(model.rankRight, currentRank)
            else:
                nextRank = rankedController.getRank(currentRankID + 1)
                model.setHasLeftRank(not currentRank.isInitialForNextDivision())
                if not currentRank.isInitialForNextDivision():
                    self.__fillRankData(model.rankLeft, currentRank)
                self.__fillRankData(model.rankRight, nextRank)
                stepsCurrent = stepsTotal = 0
                progress = nextRank.getProgress()
                if progress is not None:
                    steps = progress.getSteps()
                    stepsTotal = len(steps)
                    stepsCurrent = sum([ 1 for step in steps if step.isAcquired() ])
                model.setSteps(stepsCurrent)
                model.setStepsTotal(stepsTotal)
                battlesInQualification = rankedController.getStatsComposer().amountBattles
                totalQualificationBattles = rankedController.getTotalQualificationBattles()
                model.setQualBattles(battlesInQualification)
                model.setQualTotalBattles(totalQualificationBattles)
            bonusBattles = 0
            if self.__rankedBattleController.getCurrentSeason():
                bonusBattles = rankedController.getClientBonusBattlesCount()
            model.setBonusBattles(bonusBattles)
            return

    @staticmethod
    def __fillRankData(model, rank):
        model.setRankID(rank.getID())
        model.setRankName(rank.getUserName())
        model.setDivisionID(rank.getDivision().getID())
        model.setIsQualification(rank.isQualification())
        model.setIsUnburnable(rank.isVisualUnburnable())
        shieldStatus = rank.getShieldStatus()
        if shieldStatus:
            shieldHP = shieldStatus[1]
            model.setShieldHP(shieldHP)

    @staticmethod
    def __getRankedBattlesSeasonName(season):
        seasonName = season.getUserName() or season.getNumber()
        if seasonName.isdigit():
            seasonName = int2roman(int(seasonName))
        return backport.text(R.strings.menu.headerButtons.battle.types.ranked.availability.season(), season=seasonName)
