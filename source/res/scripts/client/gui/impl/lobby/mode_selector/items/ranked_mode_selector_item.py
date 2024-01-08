# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/ranked_mode_selector_item.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, formatSeasonLeftTime
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.ranked_battles.ranked_helpers.web_season_provider import UNDEFINED_LEAGUE_ID
from helpers import dependency, int2roman
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
    __rankedBattleController = dependency.descriptor(IRankedBattlesController)

    @property
    def viewModel(self):
        return super(RankedModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(RankedModeSelectorItem, self)._onInitializing()
        self.__onGameModeUpdated()
        self.__rankedBattleController.onGameModeStatusUpdated += self.__onGameModeUpdated
        self.__rankedBattleController.onUpdated += self.__onGameModeUpdated
        self._addReward(ModeSelectorRewardID.OTHER)

    def _onDisposing(self):
        self.__rankedBattleController.onGameModeStatusUpdated -= self.__onGameModeUpdated
        self.__rankedBattleController.onUpdated -= self.__onGameModeUpdated
        super(RankedModeSelectorItem, self)._onDisposing()

    def _getDisabledTooltipText(self):
        if self.__rankedBattleController.isUnset():
            return backport.text(R.strings.menu.headerButtons.battle.types.ranked.availability.notSet())
        return backport.text(R.strings.menu.headerButtons.battle.types.ranked.availability.frozen()) if self.__rankedBattleController.isFrozen() else super(RankedModeSelectorItem, self)._getDisabledTooltipText()

    def __onGameModeUpdated(self, *_):
        statusNotActive = self.__getRankedNotActiveStatus()
        timeLeft = self.__getTimeLeft()
        with self.viewModel.transaction() as vm:
            vm.setEventName(self.__getRankedName())
            vm.setStatusNotActive(statusNotActive)
            vm.setTimeLeft(str(timeLeft))
            self.__fillRankedWidget(vm.widget)
        setBattlePassState(self.viewModel)

    def __getRankedName(self):
        currentSeason = self.__rankedBattleController.getCurrentSeason()
        return self.__getRankedBattlesSeasonName(currentSeason) if currentSeason else ''

    def __getRankedNotActiveStatus(self):
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
        return formatSeasonLeftTime(currentSeason)

    def __fillRankedWidget(self, model):
        season = self.__rankedBattleController.getCurrentSeason()
        if season is None:
            season = self.__rankedBattleController.getPreviousSeason()
        isEnabled = self.__rankedBattleController.isEnabled() and season is not None
        model.setIsEnabled(isEnabled)
        if not isEnabled:
            return
        else:
            currentRankID = self.__rankedBattleController.getCurrentRank()[0]
            currentRank = self.__rankedBattleController.getRank(currentRankID)
            model.setIsFinal(currentRank.isFinal())
            if currentRank.isFinal():
                statsComposer = self.__rankedBattleController.getStatsComposer()
                prevWebSeasonInfo = self.__rankedBattleController.getClientSeasonInfo()
                currWebSeasonInfo = self.__rankedBattleController.getWebSeasonProvider().seasonInfo
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
                nextRank = self.__rankedBattleController.getRank(currentRankID + 1)
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
                battlesInQualification = self.__rankedBattleController.getStatsComposer().amountBattles
                totalQualificationBattles = self.__rankedBattleController.getTotalQualificationBattles()
                model.setQualBattles(battlesInQualification)
                model.setQualTotalBattles(totalQualificationBattles)
            bonusBattles = 0
            if self.__rankedBattleController.getCurrentSeason():
                bonusBattles = self.__rankedBattleController.getClientBonusBattlesCount()
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
