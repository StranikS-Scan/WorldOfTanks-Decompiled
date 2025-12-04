# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/leaderboard/ny_weekly_rewards_view.py
import typing
from functools import partial
from gui.shared.event_dispatcher import showHangar
from shared_utils import findFirst
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_weekly_rewards_view_model import NyWeeklyRewardsViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_stage_model import NyStageModel, StageState
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.gui.shared import IItemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from new_year.ny_constants import ViewAliases
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import Tabs
from new_year.gui.impl.new_year.sounds import OVERLAY_HANGAR_SOUND_SPACE
from new_year.skeletons.new_year import ITamagotchiDataProvider, ITamagotchiWebRequester, INewYearController
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.new_year.new_year_model_helper import packNyLeaderboardRewards
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_top_reward_model import NyTopRewardModel
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.shared.event_dispatcher import showNYWeeklyRewardsViewWindow, showNyVehiclePreview
from new_year_common.items.components.ny_constants import CurrentNYConstants, NewYearObjects
from copy import deepcopy
if typing.TYPE_CHECKING:
    from new_year.tamagotchi.dto.leaderboard import Leaderboard
    from new_year.tamagotchi.dto.config import Config
    from frameworks.wulf import Array

class NewYearWeeklyRewardsView(ViewImpl):
    __slots__ = ('__tooltips', '__stageId')
    _COMMON_SOUND_SPACE = OVERLAY_HANGAR_SOUND_SPACE
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    _webRequester = dependency.descriptor(ITamagotchiWebRequester)
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, stageId=0):
        settings = ViewSettings(R.views.new_year.lobby.new_year.WeeklyRewardsView())
        settings.model = NyWeeklyRewardsViewModel()
        super(NewYearWeeklyRewardsView, self).__init__(settings)
        self.__tooltips = {}
        self.__stageId = stageId

    @property
    def viewModel(self):
        return super(NewYearWeeklyRewardsView, self).getViewModel()

    @property
    def currentSeasonId(self):
        seasons = self._dataProvider.config.seasons
        nowTime = getServerUTCTime()
        seasonAboutToStart = findFirst(lambda season: season.startTime - nowTime > 0, seasons)
        return self._dataProvider.currentSeason.id + 1 if seasonAboutToStart is None else seasonAboutToStart.id

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(NewYearWeeklyRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if R.views.dyn('gui_lootboxes').isValid() and contentID == R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__tooltips[event.getArgument('tooltipId')]
            return tooltipData.tooltip(*tooltipData.specialArgs)
        else:
            return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip() else None

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onInfoClick, self.__onInfoClick),
         (self.viewModel.onPreviewClick, self.__onPreviewVehicle),
         (self.viewModel.onTabSelected, self.__onTabSelected),
         (self._dataProvider.onLeaderBoardUpdated, self.__onLeaderboardUpdated),
         (self._dataProvider.onPlayerStatsUpdated, self.__onPlayerStatsUpdated),
         (self._dataProvider.onSeasonEnded, self.__onSeasonEnded),
         (self._dataProvider.onNextSeasonStarted, self.__onSeasonStarted),
         (self._itemsCache.onSyncCompleted, self.__onInventoryUpdate))

    def _onLoading(self, *args, **kwargs):
        super(NewYearWeeklyRewardsView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.__makeRequestPlayerStats()
        self.viewModel.setCurrentStage(self.__stageId or self._dataProvider.currentSeason.id - 1)

    def __onSeasonEnded(self, seasonId):
        self.__updateModel()
        self.__updateRecalcState(seasonId)

    def __onSeasonStarted(self, _):
        self.__updateModel()

    def __onLeaderboardUpdated(self, isSuccess):
        if not isSuccess:
            return
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            self.__fillModel(tx)

    def __fillModel(self, model):
        stagesModel = model.getStages()
        stagesModel.clear()
        seasons = self._dataProvider.config.seasons
        user = self._dataProvider.leaderboard.user
        leaderboard = self._dataProvider.leaderboard
        currSeasonId = self.currentSeasonId
        for season in seasons:
            stageState = self.__getStageState(season.startTime, season.endTime, season.id, currSeasonId)
            stageModel = NyStageModel()
            stageModel.setId(season.id)
            stageModel.setStartDate(season.startTime)
            stageModel.setEndDate(season.endTime)
            stageModel.setState(stageState)
            stageModel.setIsRecalc(leaderboard.isRecalcTime if season.id == currSeasonId - 1 else False)
            stageModel.setPosition(user.position)
            self.__fillTops(stageModel, season, user)
            stagesModel.addViewModel(stageModel)

        self.__updateReceivedTopRewards(model)
        stagesModel.invalidate()

    def __fillTops(self, stageModel, season, user):
        topsModel = stageModel.getTops()
        topsModel.clear()
        self.__fillDrawRewards(season, topsModel)
        self.__fillTopRewards(season, user, topsModel)
        topsModel.invalidate()

    def __fillDrawRewards(self, season, topsModel):
        drawReward = season.drawReward.rewards
        topRewardModel = NyTopRewardModel()
        packNyLeaderboardRewards(drawReward, topRewardModel.rewards, self.__tooltips)
        topsModel.addViewModel(topRewardModel)

    def __fillTopRewards(self, season, user, topsModel):
        nextUserTopIdx = 1
        topConfig = season.topConfig
        for i, top in enumerate(reversed(topConfig), start=len(topsModel)):
            topRewardModel = NyTopRewardModel()
            topRewardModel.setTop(top.endPos)
            if top.startPos <= user.position <= top.endPos:
                nextUserTopIdx = i + 1
            rewardsInTop = deepcopy(top.rewards.copy()) or {}
            packNyLeaderboardRewards(rewardsInTop, topRewardModel.rewards, self.__tooltips, (CurrentNYConstants.NY_STATIC_DOGTAG, partial(self.__ctxUpdater, top)))
            topsModel.addViewModel(topRewardModel)

        if nextUserTopIdx < len(topsModel):
            nextTopRewardModel = topsModel[nextUserTopIdx]
            nextTopRewardModel.setPointsToTop(user.pointsByNextTop)

    def __updateRecalcState(self, seasonId):
        with self.getViewModel().transaction() as tx:
            stagesModel = tx.getStages()
            leaderboard = self._dataProvider.leaderboard
            for stageModel in stagesModel:
                if stageModel.getId() == seasonId:
                    stageModel.setIsRecalc(leaderboard.isRecalcTime)

            stagesModel.invalidate()

    def __updateReceivedTopRewards(self, model):
        stagesModel = model.getStages()
        top = -1
        for stageModel in stagesModel:
            topsModels = stageModel.getTops()
            playerStat = self._dataProvider.getPlayerWeekStat(stageModel.getId())
            top = self._dataProvider.getRewardedTopThreshold(stageModel.getId())
            topsModel = findFirst(lambda topRewardModel: topRewardModel.getTop() == top, topsModels)
            if topsModel is None:
                continue
            isRewarded = bool(playerStat.rewards) and playerStat.isRewarded if playerStat is not None else False
            topsModel.setIsRewarded(isRewarded)
            topsModels.invalidate()

        stagesModel.invalidate()
        return

    def __onInventoryUpdate(self, _, invDiff):
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            self.__updateModel()

    def __getStageState(self, startTime, endTime, seasonId, currentSeasonId):
        currTime = getServerUTCTime()
        leaderboard = self._dataProvider.leaderboard
        isRecalc = leaderboard.isRecalcTime
        if startTime <= currTime < endTime:
            if isRecalc:
                return StageState.NOTSTARTED
            return StageState.ACTIVE
        if currTime < startTime:
            return StageState.NOTSTARTED
        if currTime > endTime:
            if isRecalc and seasonId == currentSeasonId - 1:
                return StageState.ACTIVE
            return StageState.FINISHED
        return StageState.FINISHED

    def __makeRequestPlayerStats(self):
        if self._dataProvider.raccoonState:
            self._webRequester.requestPlayerStats()

    def __onPlayerStatsUpdated(self, isSuccess):
        if isSuccess:
            with self.getViewModel().transaction() as tx:
                self.__updateReceivedTopRewards(tx)

    def __ctxUpdater(self, top):
        return top.endPos

    @args2params(int)
    def __onPreviewVehicle(self, vehicleCD):
        callback = partial(self.__vehiclePreviewCallback, stageId=self.__stageId)
        showNyVehiclePreview(vehicleCD, previewBackCb=callback)

    @args2params(int)
    def __onTabSelected(self, id):
        self.__stageId = id

    @classmethod
    def __vehiclePreviewCallback(cls, stageId):
        if cls._dataProvider.raccoonState and cls._nyController.isInProgress():
            NewYearNavigation.switchTo(NewYearObjects.CITY_VIEW, True, ViewAliases.QUESTS_VIEW, switchCallback=partial(showNYWeeklyRewardsViewWindow, stageId=stageId))
            return
        showHangar()

    def __onClose(self):
        self.destroyWindow()

    def __onInfoClick(self):
        self.destroyWindow()
        NewYearNavigation.showInfoView(startTab=Tabs.LEADERBOARD)


class NewYearWeeklyRewardsViewWindow(LobbyNotificationWindow):

    def __init__(self, parent=None, stageId=0):
        super(NewYearWeeklyRewardsViewWindow, self).__init__(content=NewYearWeeklyRewardsView(stageId), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW, decorator=None)
        return
