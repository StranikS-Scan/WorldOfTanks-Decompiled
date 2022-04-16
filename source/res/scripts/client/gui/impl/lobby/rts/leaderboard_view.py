# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/leaderboard_view.py
import logging
import typing
from contextlib import contextmanager
import BigWorld
from adisp import process, async
from gui.impl.lobby.rts import LeaderboardIDSuffix
from helpers import dependency
from helpers.time_utils import getTimestampFromLocal, getTimeStructInLocal
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
from gui.impl.backport.backport_tooltip import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gui_decorators import args2params
from gui.event_boards.event_boards_timer import getCurrentUTCTimeTs
from gui.impl.pub import ViewImpl, ToolTipWindow
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IRTSBattlesController
from gui.impl.gen.view_models.views.lobby.rts.leaderboard_view.leaderboard_view_model import LeaderboardViewModel, LeaderboardType, PlayerState, LeaderboardRankingViewModel, LeaderboardErrorViewModel
from gui.impl.gen.view_models.views.lobby.rts.tooltips.timer_tooltip_view_model import TimerTooltipViewModel
from gui.impl.lobby.rts.tooltips.rts_points_tooltip_view import RTSPointsTooltipViewTanker, RTSPointsTooltipView1x7, RTSPointsTooltipView1x1
from gui.impl.lobby.rts.rts_bonuses_packers import getRTSBonusPacker
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
from constants import ARENA_BONUS_TYPE
from gui.impl.lobby.rts.rts_i_tab_view import ITabView
if typing.TYPE_CHECKING:
    from typing import Union, Optional, List, Callable
    from frameworks.wulf import ViewEvent, Window
    from gui.event_boards.event_boards_items import ExcelItem, LeaderBoard, EventSettings, MyInfoInLeaderBoard
    RankingItem = Union[ExcelItem, MyInfoInLeaderBoard]
_logger = logging.getLogger(__name__)
EVENT_ID_MAPPING = {LeaderboardType.STRATEGIST1X1: LeaderboardIDSuffix.STRATEGIST_1x1.value,
 LeaderboardType.STRATEGIST1X7: LeaderboardIDSuffix.STRATEGIST_1x7.value,
 LeaderboardType.TANKER: LeaderboardIDSuffix.TANKER.value}

class LeaderboardView(ViewImpl, ITabView):
    __slots__ = ('_eventId', '_leaderboardId', '_tooltipData', '_isEnabled')
    _eventsController = dependency.descriptor(IEventBoardController)
    _rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = LeaderboardViewModel()
        self._eventId = None
        self._leaderboardId = None
        self._tooltipData = None
        self._isEnabled = False
        super(LeaderboardView, self).__init__(settings)
        return

    def createToolTipContent(self, event, contentID):
        _logger.debug('LeaderboardView::createToolTipContent')
        if contentID == R.views.lobby.rts.TimerTooltip():
            model = TimerTooltipViewModel()
            return ViewImpl(ViewSettings(contentID, model=model))
        if contentID == R.views.lobby.rts.tooltips.RTSPointsTooltipView():
            leaderboardType = self.viewModel.getLeaderboardType()
            if leaderboardType == LeaderboardType.TANKER:
                return RTSPointsTooltipViewTanker()
            if leaderboardType == LeaderboardType.STRATEGIST1X1:
                return RTSPointsTooltipView1x1()
            if leaderboardType == LeaderboardType.STRATEGIST1X7:
                return RTSPointsTooltipView1x7()
            _logger.warning('No tooltip present for the %s mode.', leaderboardType)
        return super(LeaderboardView, self).createToolTipContent(event=event, contentID=contentID)

    @property
    def viewModel(self):
        return super(LeaderboardView, self).getViewModel()

    def createToolTip(self, event):
        content = None
        contentId = event.contentID
        tooltipData = None
        tooltipId = event.getArgument('tooltipId', None)
        if tooltipId is not None:
            tooltipData = self._tooltipData.get(int(tooltipId), None)
            if not tooltipData:
                _logger.warning('[LeaderboardView] Tooltip data is missing for tooltip id %s.', tooltipId)
        if contentId == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent() and tooltipData:
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
        else:
            return super(LeaderboardView, self).createToolTip(event)
        if content:
            window = ToolTipWindow(event, content, self.getParentWindow())
            window.move(event.mouse.positionX, event.mouse.positionY)
        if window:
            window.load()
        return window

    def showTab(self):
        self._loadData()

    def _initialize(self, *args, **kwargs):
        super(LeaderboardView, self)._initialize(*args, **kwargs)
        self.viewModel.onLeaderboardTypeSelect += self._onLeaderboardTypeSelect
        self.viewModel.onPageClick += self._onPageClick
        self.viewModel.onRefreshClick += self._loadData
        self._rtsController.onUpdated += self._onRtsSettingsUpdated

    def _finalize(self):
        self.viewModel.onLeaderboardTypeSelect -= self._onLeaderboardTypeSelect
        self.viewModel.onPageClick -= self._onPageClick
        self.viewModel.onRefreshClick -= self._loadData
        self._rtsController.onUpdated -= self._onRtsSettingsUpdated
        super(LeaderboardView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(LeaderboardView, self)._onLoading(*args, **kwargs)
        leaderboardType = self._getCurrentLeaderboardType()
        self.viewModel.setLeaderboardType(leaderboardType)
        self._isEnabled = self._rtsController.getSettings().isLeaderboardEnabled()

    def _getCurrentLeaderboardType(self):
        leaderboardType = LeaderboardType.STRATEGIST1X7
        if not self._rtsController.isCommander():
            leaderboardType = LeaderboardType.TANKER
        if self._rtsController.getBattleMode() == ARENA_BONUS_TYPE.RTS_1x1:
            leaderboardType = LeaderboardType.STRATEGIST1X1
        return leaderboardType

    @process
    def _loadData(self):
        with self._transaction() as vm:
            if self._isEnabled:
                self._fetchEvents()
                yield self._switchSubmode(vm, vm.getLeaderboardType())
            else:
                self._setUnavailableError(self.viewModel.error)
                yield lambda callback: callback(None)

    def _onRtsSettingsUpdated(self):
        isEnabled = self._rtsController.getSettings().isLeaderboardEnabled()
        if isEnabled != self._isEnabled:
            self._isEnabled = isEnabled
            self._loadData()

    @process
    @args2params(str)
    def _onLeaderboardTypeSelect(self, leaderboardType):
        _logger.debug('[LeaderboardView] _onLeaderboardTypeSelect: leaderboard type: %s', leaderboardType)
        with self._transaction() as vm:
            leaderboardTypeValue = LeaderboardType(leaderboardType)
            self.viewModel.setLeaderboardType(leaderboardTypeValue)
            yield self._switchSubmode(vm, leaderboardTypeValue)

    @process
    @args2params(int)
    def _onPageClick(self, pageNumber):
        _logger.debug('[LeaderboardView] _onPageClick: page number: %d', pageNumber)
        with self._transaction() as vm:
            yield self._updateLeaderboard(vm, page=pageNumber)

    def _getAllEvents(self):
        return self._eventsController.getEventsSettingsData().getEvents()

    def _getEvent(self, eventId):
        return self._eventsController.getEventsSettingsData().getEvent(eventId)

    @async
    @process
    def _switchSubmode(self, vm, leaderboardType, callback, page=1):
        self._eventId = self._getEventId(leaderboardType)
        self._leaderboardId = self._getLeaderboardId(self._eventId)
        _logger.debug('[LeaderboardView] _switchSubmode: event id: %s, leaderboard id: %s', self._eventId, self._leaderboardId)
        if self._eventId is not None and self._leaderboardId is not None:
            yield self._updateEvent(vm, page=page)
        else:
            self._setDataLoadError(vm.error)
            yield lambda callback: callback(None)
        callback(None)
        return

    @async
    @process
    def _updateEvent(self, viewModel, callback, page=1):
        eventData = self._getEvent(self._eventId)
        minBattleCount = eventData.getCardinality() or 0
        viewModel.setMinBattlesRequired(minBattleCount)
        viewModel.setCurrentPage(page)
        viewModel.setTotalPages(0)
        viewModel.setMaxRank(eventData.getLeaderboardViewSize())
        self._updateRewards(viewModel)
        yield self._updateLeaderboard(viewModel, page=page)
        yield self._updatePlayerInfo(viewModel)
        callback(None)
        return

    @process
    def _fetchEvents(self):
        yield self._eventsController.getEvents(isTabVisited=True)

    def _getEventId(self, leaderboardType):
        leaderboardName = EVENT_ID_MAPPING[leaderboardType]
        for event in self._getAllEvents():
            if leaderboardName not in event.getEventID():
                continue
            return event.getEventID()

        return None

    def _getLeaderboardId(self, eventId):
        if eventId is None:
            return
        else:
            eventData = self._getEvent(eventId)
            leaderboardIds = eventData.getLeaderboards()
            return leaderboardIds[0][0] if leaderboardIds else None

    @async
    @process
    def _updateLeaderboard(self, viewModel, callback, page=1):
        leaderboardData = yield self._eventsController.getLeaderboard(self._eventId, self._leaderboardId, page)
        if not viewModel.proxy:
            return
        else:
            rankingsModel = viewModel.getRankings()
            rankingsModel.clear()
            if leaderboardData:
                leaderboardRows = leaderboardData.getExcelItems()
                rankingsModel.reserve(len(leaderboardRows))
                for row in leaderboardRows:
                    rankingItem = self._fillRankingViewModelItem(row, row.getName(), spaId=row.getSpaId())
                    rankingsModel.addViewModel(rankingItem)

                rankingsModel.invalidate()
                viewModel.setCurrentPage(page)
                viewModel.setTotalPages(leaderboardData.getPagesAmount())
                lastUpdatedTimestamp = getTimeStructInLocal(leaderboardData.getLastLeaderboardRecalculationTS())
                viewModel.setLastUpdated(getTimestampFromLocal(lastUpdatedTimestamp))
            else:
                self._setDataLoadError(viewModel.error)
            callback(None)
            return

    def _fillRankingViewModelItem(self, data, playerName, viewModel=None, spaId=0):
        if not viewModel:
            viewModel = LeaderboardRankingViewModel()
        rank = data.getRank() or 0
        viewModel.setRank(rank)
        viewModel.setUserName(playerName)
        viewModel.setSpaId(spaId)
        clanTag = data.getClanTag()
        if clanTag:
            viewModel.setClanTag(clanTag)
            viewModel.setClanColor(data.getClanColor())
        gamePoints = data.getP1() or '-'
        viewModel.setGamePoints(gamePoints)
        averageDamage = data.getP2() or '-'
        viewModel.setAverageDamage(averageDamage)
        return viewModel

    @async
    @process
    def _updatePlayerInfo(self, viewModel, callback):
        playerInfo = yield self._eventsController.getMyLeaderboardInfo(self._eventId, self._leaderboardId)
        if not viewModel.proxy:
            return
        else:
            if playerInfo:
                playerName = getattr(BigWorld.player(), 'name', '')
                playerRankingViewModel = viewModel.currentPlayerRanking
                self._fillRankingViewModelItem(playerInfo, playerName, playerRankingViewModel)
                deadline = self._getEvent(self._eventId).getEndDateTs()
                participationState = self._getEventParticipationState(playerInfo.getRank(), deadline)
                viewModel.setCurrentPlayerState(participationState)
            else:
                self._setDataLoadError(viewModel.error)
            callback(None)
            return

    def _getEventParticipationState(self, rank, deadline):
        if rank:
            return PlayerState.INBOARD
        serverTime = getCurrentUTCTimeTs()
        return PlayerState.INSUFFICIENTBATTLES if serverTime < deadline else PlayerState.NOTPARTICIPATED

    def _updateRewards(self, viewModel):
        self._tooltipData = {}
        eventData = self._getEvent(self._eventId)
        rewardByRank = eventData.getRewardsByRank().getRewardByRank(self._leaderboardId) if eventData else None
        rewards = viewModel.rewards
        rewards.setMinRank(0)
        rewards.setMaxRank(0)
        bonusesListModel = rewards.getBonuses()
        bonusesListModel.clear()
        if eventData is None or rewardByRank is None:
            self._setDataLoadError(viewModel.error)
            return
        else:
            rewardGroups = rewardByRank.getRewardGroups()
            if not rewardGroups:
                return
            group = rewardGroups[0]
            rankMin, rankMax = group.getRankMinMax()
            rewards.setMinRank(rankMin)
            rewards.setMaxRank(rankMax)
            packBonusModelAndTooltipData(group.getRewards(), getRTSBonusPacker(), bonusesListModel, self._tooltipData)
            bonusesListModel.invalidate()
            return

    def _setUnavailableError(self, viewModel):
        _logger.warning('[LeaderboardView]: Leaderboards unavailable')
        self._setError(viewModel, 'unavailable', False)

    def _setDataLoadError(self, viewModel):
        _logger.warning('[LeaderboardView]: Error loading the data')
        self._setError(viewModel, 'loading', True)

    def _clearError(self, viewModel):
        self._setError(viewModel, None, False)
        return

    def _setError(self, viewModel, errorResourceName=None, showReloadButton=False):
        if errorResourceName:
            resource = R.strings.rts_battles.leaderboard.errors.dyn(errorResourceName)
            title = backport.text(resource.title())
            description = backport.text(resource.descr())
        else:
            title = ''
            description = ''
        viewModel.setTitle(title)
        viewModel.setDescription(description)
        viewModel.setShowReloadButton(showReloadButton)

    @contextmanager
    def _transaction(self):
        _logger.debug('[LeaderboardView]: Loading')
        self.viewModel.setIsLoading(True)
        with self.viewModel.transaction() as vm:
            self._clearError(vm.error)
            try:
                yield vm
            finally:
                if vm.proxy:
                    vm.setIsLoading(False)
                    _logger.debug('[LeaderboardView]: Finished loading')
