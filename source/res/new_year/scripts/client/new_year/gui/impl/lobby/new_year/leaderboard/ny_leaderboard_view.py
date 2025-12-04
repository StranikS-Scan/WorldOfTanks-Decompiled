# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/leaderboard/ny_leaderboard_view.py
import typing
import BigWorld
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.Waiting import Waiting
from new_year.gui.shared.events import NewYearEvent
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from helpers.CallbackDelayer import CallbackDelayer
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import Tabs
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year_account_settings import getNYSetting, setNYSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_leaderboard_model import NyLeaderboardModel, State, LastAction
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_player_model import NyPlayerModel, PositionType
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.leaderboard.ny_tabs_model import NyTabsModel
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.ny_constants import InternalViewState, NY_LEADERBOARD_INFO_SEEN, NY_IS_LEADERBOARD_REWARDS_CHECKED, NY_IS_SECRET_REWARDS_CHECKED
from new_year.skeletons.new_year import ITamagotchiWebRequester, ITamagotchiDataProvider
from new_year.gui.shared.event_dispatcher import showNYLeaderboardInfoWindow, showNYWeeklyRewardsViewWindow
from new_year.tamagotchi.sys_msg.sys_msg_handler import TamagotchiSysMsgHandler
if typing.TYPE_CHECKING:
    from new_year.tamagotchi.dto.leaderboard import Leaderboard
_PAGE_SIZE = 50
_MIN_REQ_DELAY = 10
_HIDE_WAITING_DELAY = 30

class NewYearLeaderboardView(HistorySubModelPresenter):
    __slots__ = ('__timer',)
    _WAITING_NAME = 'leaderboardRewards'
    _SECRET_REWARD_NAME = 'vehicles'
    _STOP_DELAY = -1.0
    _INTERNAL_VIEW_STATE = InternalViewState.RACCOON
    _webRequester = dependency.descriptor(ITamagotchiWebRequester)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, viewModel, parentView, soundConfig=None):
        super(NewYearLeaderboardView, self).__init__(viewModel, parentView, soundConfig)
        self.__timer = CallbackDelayer()

    @property
    def isLeaderboardReady(self):
        return not self.getViewModel().getIsLoading() and not self.__isRequiredDataMissed() and self.getViewModel().getState() != State.ERROR

    @property
    def timeToNextUpdate(self):
        return max(self._dataProvider.leaderboard.nextUpdateTime + _MIN_REQ_DELAY - getServerUTCTime(), _MIN_REQ_DELAY)

    def initialize(self, *args, **kwargs):
        self.getViewModel().setState(State.INITIAL)
        self._requestUpdate(isUserPage=True)
        if not getNYSetting(NY_LEADERBOARD_INFO_SEEN):
            setNYSettings(NY_LEADERBOARD_INFO_SEEN, True)
            showNYLeaderboardInfoWindow(self.getParentWindow())
        super(NewYearLeaderboardView, self).initialize(*args, **kwargs)

    def finalize(self):
        self.__timer.clearCallbacks()
        Waiting.hide(self._WAITING_NAME)
        super(NewYearLeaderboardView, self).finalize()

    def _getEvents(self):
        return ((self._nyController.onNySettingsChanged, self.__onNySettingsChanged),
         (self.getViewModel().onPageClick, self._onPageClick),
         (self.getViewModel().onPersonalPositionClick, self._onPersonalPositionClick),
         (self.getViewModel().onTopClick, self._onTopClick),
         (self.getViewModel().onInfoClick, self._onInfoClick),
         (self.getViewModel().onClose, self._onCloseClick),
         (self.getViewModel().onRewardsClick, self._onRewardsClick),
         (self.getViewModel().onRefresh, self._onRefresh),
         (self._dataProvider.onLeaderBoardUpdated, self._onLeaderBoardUpdated),
         (self._dataProvider.onSeasonEnded, self._onRefresh),
         (self._dataProvider.onNextSeasonStarted, self._onRefresh))

    def _getListeners(self):
        return ((NewYearEvent.ON_SWITCH_VIEW, self.__onSwitchViewEvent, EVENT_BUS_SCOPE.LOBBY),)

    def _onPersonalPositionClick(self):
        self._requestUpdate(isUserPage=True, actionType=LastAction.PLAYER)

    def _onPageClick(self, args):
        self._requestUpdate(args['page'], actionType=LastAction.PAGE)

    def _onInfoClick(self):
        NewYearNavigation.showInfoView(startTab=Tabs.LEADERBOARD)

    def _onTopClick(self, args):
        top = args['top']
        for reward in self._dataProvider.currentSeason.topConfig:
            if reward.endPos == top:
                page = int(reward.startPos / _PAGE_SIZE) + 1
                self._requestUpdate(page, actionType=LastAction.TOP)
                with self.getViewModel().transaction() as tx:
                    tx.setCurrentTab(top)
                break

    def _onCloseClick(self):
        NewYearNavigation.closeMainView()

    def __onNySettingsChanged(self):
        config = getNewYearGeneralConfig()
        if config is not None and not config.getPetVisible():
            NewYearNavigation.closeMainView()
        return

    def _onRewardsClick(self):
        if not self.isLeaderboardReady and not Waiting.isOpened(self._WAITING_NAME):
            Waiting.show(self._WAITING_NAME, isAlwaysOnTop=True, isSingle=True)
            self.__delayedHideWaiting()
            return
        self._goToRewards()

    def _goToRewards(self):
        showNYWeeklyRewardsViewWindow(self.getParentWindow())
        setNYSettings(NY_IS_LEADERBOARD_REWARDS_CHECKED, True)
        if self.getViewModel().getIsVehicleAvailable():
            setNYSettings(NY_IS_SECRET_REWARDS_CHECKED, True)

    def _onRefresh(self, _):
        lastRequestedPage = self.getViewModel().getCurrentPage()
        self._requestUpdate(lastRequestedPage, actionType=self.getViewModel().getLastAction())

    def _requestUpdate(self, page=0, isUserPage=False, actionType=LastAction.PLAYER):
        self._webRequester.requestLeaderboardPage(page, isUserPage)
        with self.getViewModel().transaction() as tx:
            tx.setCurrentPage(page)
            tx.setLastAction(actionType)
            tx.setIsLoading(True)

    def _onLeaderBoardUpdated(self, result):
        with self.getViewModel().transaction() as tx:
            if not result or self.__isRequiredDataMissed():
                tx.setState(State.ERROR)
                tx.setIsLoading(False)
                return
            self._updateModel(tx)
            self._updateTopTabs(tx)
            self.__runDelayedUpdate()
            self.__checkRunningWaiting()

    def _updateTopTabs(self, model):
        leaderboard = self._dataProvider.leaderboard
        season = self._dataProvider.currentSeason
        model.setFromTimestamp(season.startTime)
        model.setToTimestamp(season.endTime)
        model.setIsFinal(self._dataProvider.isLeaderboardFinished)
        model.setIsRewardsCheck(getNYSetting(NY_IS_LEADERBOARD_REWARDS_CHECKED))
        model.setIsVehicleAvailable(self.__checkIsVehicleAvailable())
        totalPages = leaderboard.page.totalPage
        userPos = leaderboard.user.position
        tabs = model.getTabs()
        tabs.clear()
        for item in reversed(season.topConfig):
            startPos = item.startPos
            endPos = item.endPos
            tab = NyTabsModel()
            tab.setTop(endPos)
            tab.setIsAvailable(totalPages * _PAGE_SIZE >= startPos)
            if startPos <= userPos <= endPos:
                model.selfRank.setTop(endPos)
            tabs.addViewModel(tab)

        tabs.invalidate()

    def _updateModel(self, model):
        leaderboard = self._dataProvider.leaderboard
        user = leaderboard.user
        page = leaderboard.page
        model.setUpdatedTimestamp(leaderboard.updateTime)
        model.setPagesCount(page.totalPage)
        model.setCurrentPage(page.currentPage)
        model.setStage(self._dataProvider.currentSeason.id)
        model.setPointsToTop(user.pointsByNextTop if user.position == 0 else 0)
        pointsModel = model.personalPoints
        pointsModel.setNextTopPoints(user.pointsByNextTop)
        pointsModel.setOpponentPoints(user.pointsByNextPlayer)
        model.selfRank.setPosition(user.position)
        model.selfRank.setUserName(BigWorld.player().name)
        model.selfRank.setScore(user.points)
        self.__updateLeaderboard(leaderboard, model)
        state = State.RECALC if leaderboard.isRecalcTime else State.SUCCESS
        model.setState(state)
        model.setIsLoading(False)

    def __updateLeaderboard(self, leaderboard, model):
        user = leaderboard.user
        page = leaderboard.page
        leaderboard = page.leaderboard
        pointsModel = model.personalPoints
        rows = []
        for row in leaderboard:
            playerModel = NyPlayerModel()
            playerModel.setUserName(row.nickname)
            playerModel.setPosition(row.position)
            playerModel.setScore(row.point)
            playerModel.setPositionType(self.__getPositionType(row.upDown))
            if row.position == user.position:
                model.selfRank.setPositionType(self.__getPositionType(row.upDown))
            if row.position + 1 == user.position:
                pointsModel.setOpponentPoints(max(row.point - user.points, 0))
            rows.append(playerModel)

        start, end = leaderboard[0].position, leaderboard[-1].position
        for top in reversed(self._dataProvider.currentSeason.topConfig):
            topStart, topEnd = top.startPos, top.endPos
            if start <= topStart <= end:
                topModel = NyPlayerModel()
                topModel.setTop(topEnd)
                topModel.setStartPos(topStart)
                topModel.setEndPos(topEnd)
                rows.insert(topStart - start, topModel)
            if topStart <= user.position <= topEnd:
                model.selfRank.setStartPos(topStart)
                model.selfRank.setEndPos(topEnd)
                model.setTop(topEnd)

        players = model.getPlayers()
        players.clear()
        for row in rows:
            players.addViewModel(row)

        players.invalidate()
        currentTab = self.__getCurrentTab(rows, model)
        model.setCurrentTab(currentTab)

    def __onSwitchViewEvent(self, event):
        switchCallback = event.ctx.kwargs.get('switchCallback')
        if switchCallback:
            switchCallback(parent=self.getParentWindow())

    def __runDelayedUpdate(self):
        self.__timer.delayCallback(self.timeToNextUpdate, self.__timerUpdate)

    def __delayedHideWaiting(self):
        self.__timer.delayCallback(_HIDE_WAITING_DELAY, self.__hideRewardWaiting)

    def __timerUpdate(self):
        if self._dataProvider.isLeaderboardFinished:
            return self._STOP_DELAY
        self._requestUpdate(self.getViewModel().getCurrentPage(), actionType=self.getViewModel().getLastAction())
        return self.timeToNextUpdate

    def __hideRewardWaiting(self):
        Waiting.hide(self._WAITING_NAME)
        TamagotchiSysMsgHandler.sendLeaderboardNotAvailableMessage()

    def __checkRunningWaiting(self):
        if self.isLeaderboardReady and Waiting.isOpened(self._WAITING_NAME):
            Waiting.hide(self._WAITING_NAME)
            self._goToRewards()

    def __isRequiredDataMissed(self):
        config = self._dataProvider.config
        leaderboard = self._dataProvider.leaderboard
        return not (config and leaderboard and leaderboard.page.totalPage and leaderboard.user and self._dataProvider.currentSeason)

    def __getPositionType(self, pos):
        if pos > 0:
            return PositionType.UP
        return PositionType.DOWN if pos < 0 else PositionType.NOCHANGES

    def __getCurrentTab(self, rows, model):
        if self.getViewModel().getLastAction() == LastAction.TOP:
            return model.getCurrentTab()
        for row in rows:
            if row.getTop():
                return row.getTop()

        playerPos = 0
        for row in rows:
            if not row.getTop():
                playerPos = row.getPosition()
                break

        for top in reversed(self._dataProvider.currentSeason.topConfig):
            if top.startPos <= playerPos <= top.endPos:
                return top.endPos

        return self._dataProvider.currentSeason.topConfig[-1].endPos

    def __checkIsVehicleAvailable(self):
        seasons = self._dataProvider.config.seasons
        wasRewardsChecked = getNYSetting(NY_IS_LEADERBOARD_REWARDS_CHECKED)
        wasSecretRewardsChecked = getNYSetting(NY_IS_SECRET_REWARDS_CHECKED)
        for season in seasons:
            for top in season.topConfig:
                rewards = top.rewards
                if self._SECRET_REWARD_NAME in rewards:
                    if wasRewardsChecked and not wasSecretRewardsChecked:
                        setNYSettings(NY_IS_LEADERBOARD_REWARDS_CHECKED, False)
                    return True

        return False
