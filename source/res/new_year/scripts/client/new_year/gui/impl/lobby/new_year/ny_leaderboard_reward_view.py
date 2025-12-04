# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_leaderboard_reward_view.py
import BigWorld
from frameworks.wulf import ViewSettings, WindowLayer
from new_year.gui.impl.new_year.sounds import OVERLAY_HANGAR_SOUND_SPACE
from new_year.ny_constants import NewYearLootBoxes
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_leaderboard_reward_view_model import NyLeaderboardRewardViewModel
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.shared.event_dispatcher import showLootBoxEntry
from new_year.skeletons.new_year import ITamagotchiDataProvider, ITamagotchiWebRequester
from new_year.gui.impl.new_year.new_year_model_helper import packNyLeaderboardRewards
from new_year_common.items.components.ny_constants import CurrentNYConstants
from dog_tags_common.components_config import componentConfigAdapter as cca
from dog_tags_common.config.common import ComponentViewType
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from helpers import dependency
from shared_utils import findFirst

class NyLeaderboardRewardView(ViewImpl):
    __slots__ = ('__rewards', '__seasonID', '__top', '__isRequestInProgress', '__tooltips')
    _COMMON_SOUND_SPACE = OVERLAY_HANGAR_SOUND_SPACE
    __dataProvider = dependency.descriptor(ITamagotchiDataProvider)
    __webRequester = dependency.descriptor(ITamagotchiWebRequester)

    def __init__(self, layoutID, rewards, seasonID):
        settings = ViewSettings(layoutID)
        settings.model = NyLeaderboardRewardViewModel()
        self.__rewards = rewards
        self.__seasonID = seasonID
        self.__top = 0
        self.__isRequestInProgress = False
        self.__tooltips = {}
        super(NyLeaderboardRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyLeaderboardRewardView, self).getViewModel()

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltips.get(tooltipId)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(NyLeaderboardRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if R.views.dyn('gui_lootboxes').isValid() and contentID == R.views.dyn('gui_lootboxes').lobby.gui_lootboxes.tooltips.LootboxTooltip():
            tooltipData = self.__tooltips[event.getArgument('tooltipId')]
            return tooltipData.tooltip(*tooltipData.specialArgs)
        else:
            return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event)) if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip() else None

    def _getEvents(self):
        return ((self.getViewModel().onClose, self.__onClose), (self.getViewModel().onGoToLootbox, self.__onGoToLootbox), (self.__dataProvider.onPlayerStatsUpdated, self.__onPlayerStatsUpdated))

    def _onLoading(self, *args, **kwargs):
        super(NyLeaderboardRewardView, self)._onLoading(*args, **kwargs)
        self.__makeRequestPlayerStats()
        with self.getViewModel().transaction() as tx:
            self.__filterDogtags()
            if not self.__isRequestInProgress:
                self.__fillModel(tx)

    def __fillModel(self, model):
        playerPos, playerTop = self.__getPlayerPositionAndTop()
        model.setStage(self.__seasonID)
        model.setPosition(playerPos)
        model.setTop(playerTop)
        model.setIsFinal(self.__dataProvider.isLeaderboardFinished)
        packNyLeaderboardRewards(self.__rewards, model.rewards, self.__tooltips, (CurrentNYConstants.NY_STATIC_DOGTAG, self.__ctxUpdater))

    def __makeRequestPlayerStats(self):
        dogTagRewards = self.__rewards.get('dogTagComponents', [])
        if not dogTagRewards and self.__dataProvider.raccoonState:
            self.__webRequester.requestPlayerStats()
            self.__isRequestInProgress = True

    def __onPlayerStatsUpdated(self, isSuccess):
        self.__isRequestInProgress = False
        with self.getViewModel().transaction() as tx:
            self.__fillModel(tx)

    def __getPlayerPositionAndTop(self):
        dogTagRewards = self.__rewards.get('dogTagComponents', [])
        return self.__getDataFromDogTag(dogTagRewards[0]) if dogTagRewards else self.__getDataFromPlayerStats()

    def __getDataFromDogTag(self, dogTag):
        playerPos = 0
        playerTop = 0
        compId = dogTag.get('id')
        comp = cca.getComponentById(compId)
        if comp is None:
            return (playerPos, playerTop)
        else:
            componentProgress = BigWorld.player().dogTags.getComponentProgress(compId)
            playerPos = componentProgress.value
            playerGrade = componentProgress.grade
            if not comp.grades:
                return (playerPos, playerTop)
            playerTop = self.__getGrade(playerGrade, comp)
            self.__top = playerTop
            return (playerPos, playerTop)

    def __getDataFromPlayerStats(self):
        playerPos = -1
        playerTop = 0
        if self.__isRequestInProgress:
            return (playerPos, playerTop)
        playerStats = self.__dataProvider.playerStats
        config = self.__dataProvider.config
        if not (playerStats and config):
            return (playerPos, playerTop)
        top = self.__dataProvider.getRewardedTopThreshold(self.__seasonID)
        playerPos = self.__getPlayerPos(self.__seasonID)
        self.__top = top if top else playerTop
        return (playerPos, top)

    def __getGrade(self, playerGrade, comp):
        nextGrade = playerGrade + 1
        return self.__getMaxGrade() if nextGrade >= len(comp.grades) else comp.grades[nextGrade] - 1

    def __getMaxGrade(self):
        config = self.__dataProvider.config
        if not config:
            return 0
        else:
            rewardSeason = findFirst(lambda season: season.id == self.__seasonID, config.seasons)
            return 0 if rewardSeason is None or not rewardSeason.topConfig else rewardSeason.topConfig[-1].endPos

    def __getPlayerPos(self, seasonID):
        playerWeekStat = self.__dataProvider.getPlayerWeekStat(seasonID)
        if playerWeekStat is None:
            return -1
        else:
            return 0 if playerWeekStat.position == -1 else playerWeekStat.position

    def __filterDogtags(self):
        dogTagRewards = self.__rewards.get('dogTagComponents', [])
        if dogTagRewards:
            dogTagRewards = filter(self.__isEngraving, dogTagRewards)
            self.__rewards['dogTagComponents'] = dogTagRewards

    def __isEngraving(self, dogTag):
        compId = dogTag.get('id')
        if compId is None:
            return False
        else:
            comp = cca.getComponentById(compId)
            return comp is not None and comp.viewType == ComponentViewType.ENGRAVING

    def __ctxUpdater(self):
        return int(self.__top)

    def __onClose(self):
        self.destroyWindow()

    def __onGoToLootbox(self):
        showLootBoxEntry(lootBoxType=NewYearLootBoxes.NY_CUR_YEAR_SMALL)
        self.destroyWindow()


class NyLeaderboardRewardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, seasonID, parent=None):
        super(NyLeaderboardRewardsViewWindow, self).__init__(content=NyLeaderboardRewardView(R.views.new_year.lobby.new_year.NyLeaderboardRewardView(), rewards, seasonID), layer=WindowLayer.TOP_WINDOW, parent=parent)
