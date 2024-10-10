# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_progression_view.py
import logging
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.division_model import DivisionModel
from gui.impl.gen.view_models.views.lobby.ranked.rank_model import RankModel
from gui.impl.gen.view_models.views.lobby.ranked.ranked_progression_view_model import RankedProgressionViewModel, States
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.ranked_battles.ranked_formatters import getFloatPercentStrStat
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.ranked_battles.ranked_helpers.sound_manager import RANKED_MAIN_PAGE_SOUND_SPACE, Sounds
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from helpers.time_utils import getServerUTCTime
from shared_utils import first
from skeletons.gui.game_control import IRankedBattlesController
from visual_script_client.web_blocks import WWISE
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, Window
    from gui.impl.gen.view_models.views.lobby.ranked.ranked_statistics_model import RankedStatisticsModel
    from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
    from gui.ranked_battles.ranked_models import Division
_logger = logging.getLogger(__name__)
UNDEFINED_EFFICIENCY_VALUE = -1
EFFICIENCY_MULTIPLIER = 10000
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent
_DIVISION_TO_GF_PROGRESSION_SOUND = {0: Sounds.PROGRESSION_STATE_3_DIVISION,
 1: Sounds.PROGRESSION_STATE_2_DIVISION,
 2: Sounds.PROGRESSION_STATE_1_DIVISION}

class RankedProgressionView(ViewImpl):
    __slots__ = ('__tooltipItems', '__periodicNotifier')
    __rankedController = dependency.descriptor(IRankedBattlesController)
    _COMMON_SOUND_SPACE = RANKED_MAIN_PAGE_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = RankedProgressionViewModel()
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeasonEnd, self.__onDestroy)
        self.__tooltipItems = {}
        super(RankedProgressionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedProgressionView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self.getTooltipData(event)
            if tooltipData is not None:
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
            if tooltipId == TOOLTIPS_CONSTANTS.RANKED_BATTLES_RANK:
                rankID = int(event.getArgument('rankID'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(rankID,))
            if tooltipId == TOOLTIPS_CONSTANTS.RANKED_DIVISION_INFO:
                divisionId = str(event.getArgument('divisionId'))
                isCurrent = bool(event.getArgument('isCurrent'))
                isLocked = bool(event.getArgument('isLocked'))
                isCompleted = bool(event.getArgument('isCompleted'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(divisionId,
                 isCurrent,
                 isLocked,
                 isCompleted))
            return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(None,))
        else:
            return super(RankedProgressionView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(RankedProgressionView, self)._onLoading(*args, **kwargs)
        self.__setViewData()
        self._updateSounds()

    def _onLoaded(self, *args, **kwargs):
        super(RankedProgressionView, self)._onLoaded(*args, **kwargs)
        self.__periodicNotifier.startNotification()

    def _finalize(self):
        self.__tooltipItems = None
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        self._updateSounds(True)
        super(RankedProgressionView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.__rankedController.onRankedPrbClosing, self.__onDestroy),
         (self.__rankedController.onUpdated, self.__onUpdated),
         (self.__rankedController.onSelectableRewardsChanged, self.__onUpdated),
         (g_playerEvents.onEnqueued, self.__onDestroy),
         (self.viewModel.onClose, self.__onDestroy),
         (self.viewModel.onAbout, self.__onAbout),
         (self.viewModel.onSelectDivision, self.__onSelectDivision),
         (self.viewModel.onSelectReward, self.__onSelectReward))

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, EVENT_BUS_SCOPE.LOBBY),)

    def _updateSounds(self, onClose=False):
        self.__rankedController.getSoundManager().setAmbient()
        stateSound = _DIVISION_TO_GF_PROGRESSION_SOUND.get(self.__rankedController.getCurrentDivision().getID())
        if stateSound is not None:
            WWISE.WW_setState(Sounds.PROGRESSION_STATE, stateSound)
        self.__rankedController.getSoundManager().setProgressSound()
        return

    @replaceNoneKwargsModel
    def __setViewData(self, model=None):
        bonusBattles = 0
        if self.__rankedController.getCurrentSeason():
            bonusBattles = self.__rankedController.getClientBonusBattlesCount()
        model.setBonusBattles(bonusBattles)
        model.setHasRewardToSelect(self.__rankedController.hasAnyRewardToTake())
        divisions = self.__rankedController.getDivisions()
        self.__setSeasonInfo(model=model)
        self.__setStatisticsInfo(divisions=divisions, model=model)
        self.__setDivisionData(divisions=divisions, model=model)

    def __onUpdated(self):
        self.__periodicNotifier.stopNotification()
        self.__periodicNotifier.clear()
        self.__periodicNotifier = PeriodicNotifier(self.__getTimeTillCurrentSeasonEnd, self.__onDestroy)
        self.__periodicNotifier.startNotification()
        self.__setViewData()

    def __onDestroy(self, *_):
        self.destroyWindow()
        self.__rankedController.getSoundManager().setDefaultProgressSound()

    @staticmethod
    def __onAbout():
        url = GUI_SETTINGS.lookup('infoPageRanked')
        showBrowserOverlayView(url, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))

    def __onHeaderMenuClick(self, event):
        self.destroyWindow()

    @replaceNoneKwargsModel
    def __onSelectDivision(self, event, model=None):
        divisionID = int(event.get('divisionID', 0))
        model.setSelectedDivision(divisionID)
        if divisionID > self.__rankedController.getCurrentDivision().getID():
            WWISE.WW_setState(Sounds.SUBVIEW_HANGAR_GENERAL, Sounds.SUBVIEW_HANGAR_GENERAL_ON)
        else:
            WWISE.WW_setState(Sounds.SUBVIEW_HANGAR_GENERAL, Sounds.SUBVIEW_HANGAR_GENERAL_OFF)
        stateSound = _DIVISION_TO_GF_PROGRESSION_SOUND.get(divisionID)
        if stateSound is not None:
            WWISE.WW_setState(Sounds.PROGRESSION_STATE, stateSound)
        return

    def __getTimeTillCurrentSeasonEnd(self):
        return time_utils.getTimeDeltaFromNowInLocal(time_utils.makeLocalServerTime(self.__rankedController.getCurrentSeason().getEndDate()))

    @replaceNoneKwargsModel
    def __setSeasonInfo(self, model=None):
        seasonID = self.__rankedController.getCurrentSeason().getSeasonID()
        season = self.__rankedController.getSeason(seasonID)
        if season is not None:
            currentRank = self.__rankedController.getCurrentRank()
            maxRank = self.__rankedController.getMaxRank()
            model.setStartTimestamp(season.getStartDate())
            model.setEndTimestamp(season.getEndDate())
            model.setServerTimestamp(getServerUTCTime())
            model.setCurrentDivisionID(self.__rankedController.getCurrentDivision().getID())
            model.setSelectedDivision(self.__rankedController.getCurrentDivision().getID())
            model.setCurrentRank(currentRank.rank)
            model.setCurrentStep(currentRank.steps)
            model.setMaxRank(maxRank.rank)
            model.setSelectedState(States.FINAL if self.__rankedController.isAccountMastered() else States.PROGRESSION)
        else:
            _logger.error('Incorrect ranked season info!')
        return

    @replaceNoneKwargsModel
    def __setDivisionData(self, divisions, model=None):
        self.__tooltipItems.clear()
        divisionsModel = model.divisions
        divisionsModel.clearItems()
        for divisionID, ranksData in enumerate(divisions):
            division = DivisionModel()
            division.setDivisionID(divisionID)
            division.setFirstRank(ranksData.firstRank)
            division.setLastRank(ranksData.lastRank)
            division.setVehicleLevel(min(self.__rankedController.getSuitableVehicleLevels()))
            self.__setRanksData(division, ranksData.firstRank, ranksData.lastRank)
            divisionsModel.addViewModel(division)

        divisionsModel.invalidate()

    def __setRanksData(self, divisionModel, firstRank, lastRank):
        ranksModel = divisionModel.ranks
        ranksModel.clearItems()
        isSingleReward = True
        for rankID in range(firstRank, lastRank + 1):
            needTakeReward, canTakeReward = self.__rankedController.getCanTakeReward(rankID)
            rank = RankModel()
            rank.setRankID(rankID)
            rank.setStepsToRank(self.__rankedController.getStepsToEarnRank(rankID))
            rank.setIsUnburnable(self.__rankedController.isUnburnableRank(rankID))
            rank.setNeedTakeReward(needTakeReward)
            rank.setCanTakeReward(canTakeReward)
            self.__setRankBonuses(rank, rankID)
            ranksModel.addViewModel(rank)
            isSingleReward = isSingleReward and rank.rewards.getItemsLength() <= 1

        divisionModel.setIsSingleReward(isSingleReward)
        ranksModel.invalidate()

    def __setRankBonuses(self, model, rankID):
        rankQuest = first(self.__rankedController.getQuestsForRank(rankID).values())
        rewards = model.rewards
        rewards.clearItems()
        bonuses = self.__rankedController.replaceOfferByReward(rankQuest.getBonuses())
        packBonusModelAndTooltipData(bonuses, rewards, self.__tooltipItems)

    @replaceNoneKwargsModel
    def __setStatisticsInfo(self, divisions, model=None):
        statsComposer = self.__rankedController.getStatsComposer()
        seasonEfficiency = statsComposer.currentSeasonEfficiency.efficiency or UNDEFINED_EFFICIENCY_VALUE
        statistics = model.statistics
        statistics.setStagesCount(statsComposer.amountSteps)
        statistics.setBattlesCount(statsComposer.amountBattles)
        statistics.setTotalEfficiency(getFloatPercentStrStat(seasonEfficiency))
        efficiencies = statistics.getEfficiencyByDivision()
        efficiencies.clear()
        efficiencies.reserve(len(divisions))
        for division in divisions:
            efficiency = statsComposer.getDivisionEfficiencyPercent(division.getID()) or UNDEFINED_EFFICIENCY_VALUE
            efficiencies.addString(getFloatPercentStrStat(efficiency))

        efficiencies.invalidate()

    def __onSelectReward(self, args):
        rank = args.get('rankID')
        if rank is None:
            return
        else:
            self.__rankedController.takeRewardForRank(rank)
            return


class RankedProgressionWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(RankedProgressionWindow, self).__init__(wndFlags=WindowFlags.WINDOW, content=RankedProgressionView(R.views.lobby.ranked.RankedProgressionView()), parent=parent)
