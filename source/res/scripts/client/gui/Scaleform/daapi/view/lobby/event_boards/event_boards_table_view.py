# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_table_view.py
import BigWorld
from functools import partial
from collections import namedtuple
from adisp import process
from helpers import dependency
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from helpers.i18n import makeString as _ms
from helpers.time_utils import ONE_MINUTE
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.functions import makeTooltip
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_maintenance import EventBoardsMaintenance
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_award_group import EventBoardsAwardGroup
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_pagination import EventBoardsPagination
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vos import makeTableViewHeaderVO, makeEventBoardsTableDataVO, makeEventBoardsTableViewStatusVO, makeTableHeaderVO, makeTableViewBackgroundVO, makeCantJoinReasonTextVO, makeAwardGroupDataTooltipVO, makeParameterTooltipVO
from gui.Scaleform.daapi.view.lobby.event_boards.formaters import getStatusTitleStyle, getStatusCountStyle, formatUpdateTime, formatErrorTextWithIcon, getFullName
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.daapi.view.meta.EventBoardsTableViewMeta import EventBoardsTableViewMeta
from gui.event_boards.event_boards_items import EVENT_STATE as _es, EventSettings, LeaderBoard, PLAYER_STATE_REASON as _psr
MyInfo = namedtuple('MyInfo', ('fullData', 'pageNumber', 'rank', 'battlesCount'))
LeaderboardData = namedtuple('LeaderboardData', ('excelItems', 'pageNumber'))

class EventBoardsTableView(LobbySubView, EventBoardsTableViewMeta):
    eventsController = dependency.descriptor(IEventBoardController)
    itemsCache = dependency.descriptor(IItemsCache)
    MIN_CATEGORY = 1
    MAX_CATEGORY = 5
    TOP_POSITION_RANK = -1
    MY_RANK = -2
    MAX_AWARD_GROUPS = 4

    def __init__(self, ctx):
        super(EventBoardsTableView, self).__init__()
        self.__pagination = None
        self.__awardGroup = None
        self.__maintenance = None
        self.__eventID = ctx['eventID']
        self.__leaderboardID = ctx['leaderboardID']
        self.__maintenanceVisible = False
        self.__cleanUp()
        return

    def changeLeaderboard(self, leaderboardID):
        """
        Clean up current leaderboard and get data for new
        :param leaderboardID: new leaderboard id
        """
        self.__cleanUp()
        self.__leaderboardID = leaderboardID
        self.__fetchEventData()

    def closeView(self):
        """
        Close view
        """
        self.destroy()

    @property
    def eventData(self):
        return self.__eventData

    @property
    def leaderboardID(self):
        return self.__leaderboardID

    def onStepPage(self, direction):
        self.__fetchMyLeaderboardInfo(partial(self.__fetchLeaderboardPageData, self.__leaderboardData.pageNumber + direction, self.TOP_POSITION_RANK))

    def onShowRewardCategory(self, categoryID):
        """
        Move to reward category
        :param categoryID: category number
        """
        categoryPage = self.__rewardCategories[categoryID]['page_number']
        if self.__leaderboardData.pageNumber != categoryPage:
            self.__fetchMyLeaderboardInfo(partial(self.__fetchLeaderboardPageData, categoryPage, self.__rewardCategories[categoryID]['rank_min']))
        else:
            self.__scrollToRank(self.__rewardCategories[categoryID]['rank_min'])

    def onRefresh(self):
        """
        Try to get table data
        """
        self.__fetchEventData()

    def setMyPlace(self):
        """
        Move to my place
        """
        myPage = self.__myInfo.pageNumber
        if self.__leaderboardData.pageNumber != myPage:
            self.__fetchMyLeaderboardInfo(self.__moveToMyPlace)
        else:
            self.__scrollToRank(self.MY_RANK)

    def showNextAward(self, visible):
        stripesLen = len(self.__stripes['tableDP'])
        if stripesLen > 0:
            if visible:
                stripesID = self.__stripes['tableDP'][1]['id']
            else:
                stripesID = self.__stripes['tableDP'][0]['id']
            self.__awardGroup.setActiveRewardGroup(stripesID)

    def playerClick(self, playerID):
        """
        Open details view for player
        :param playerID: player's spa id
        """
        for item in self.__leaderboardData.excelItems:
            if item.getSpaId() == playerID:
                g_eventBus.handleEvent(events.LoadViewEvent(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, ctx={'eventID': self.__eventID,
                 'leaderboard': self.__leaderboard,
                 'excelItem': item}), scope=EVENT_BUS_SCOPE.LOBBY)
                break

    @process
    def participateStatusClick(self):
        self.__setWaiting(True)
        yield self.eventsController.joinEvent(self.__eventID)
        yield self.eventsController.getEvents()
        self.__setWaiting(False)
        self.__setPlayerData()
        self.__updateStatus()

    def _populate(self):
        super(EventBoardsTableView, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.__fetchEventData()

    def _dispose(self):
        pagination = self.__pagination
        if pagination:
            pagination.onStepPage -= self.onStepPage
        if self.__awardGroup:
            self.__awardGroup.onShowRewardCategory -= self.onShowRewardCategory
        if self.__maintenance:
            self.__maintenance.onRefresh -= self.onRefresh
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(EventBoardsTableView, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventBoardsTableView, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, EventBoardsPagination):
            self.__pagination = viewPy
            viewPy.onStepPage += self.onStepPage
        if isinstance(viewPy, EventBoardsAwardGroup):
            self.__awardGroup = viewPy
            viewPy.onShowRewardCategory += self.onShowRewardCategory
        if isinstance(viewPy, EventBoardsMaintenance):
            self.__maintenance = viewPy
            viewPy.onRefresh += self.onRefresh

    def __cleanUp(self):
        self.__eventData = None
        self.__myInfo = None
        self.__leaderboard = None
        self.__leaderboardData = None
        self.__rewardCategories = None
        self.__stripes = None
        self.__playerState = None
        self.__top = None
        return

    def __setMaintenance(self, visible):
        if self.__maintenanceVisible != visible:
            self.__maintenanceVisible = visible
            headerText = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON) + _ms(EVENT_BOARDS.MAINTENANCE_TITLE)
            bodyText = _ms(EVENT_BOARDS.MAINTENANCE_BODY)
            buttonText = _ms(EVENT_BOARDS.MAINTENANCE_UPDATE)
            self.as_setMaintenanceS(visible, headerText, bodyText, buttonText)

    def __setWaiting(self, visible):
        self.as_setWaitingS(visible, _ms('#waiting:loadContent'))

    def __updateStatus(self):
        event = self.__eventData
        playerState = self.__playerState
        top = self.__top
        myInfo = self.__myInfo
        state = playerState.getPlayerState() if playerState else None
        canJoin = playerState.getCanJoin() if playerState else True
        stateReasons = playerState.getPlayerStateReasons() if playerState else []
        joined = state is _es.JOINED
        cardinality = event.getCardinality()
        battleCount = myInfo.battlesCount if myInfo else 0
        notFull = cardinality is not None and battleCount < cardinality
        outOfScore = not myInfo.fullData.getIsInsideViewsize() if myInfo else False
        visible = True
        title = ''
        tooltip = None
        showPoints = False
        titleTooltip = None
        buttonVisible = False
        buttonEnabled = False
        buttonLabel = TOOLTIPS.ELEN_BUTTON_REGISTRATION_STARTED_HEADER
        buttonTooltip = makeTooltip(buttonLabel, TOOLTIPS.ELEN_BUTTON_REGISTRATION_STARTED_BODY)
        if event.isFinished():
            if not joined:
                title = getStatusTitleStyle(_ms(EVENT_BOARDS.EXCEL_PARTICIPATE_NOTPARTICIPATED))
            elif notFull:
                title = getStatusTitleStyle(_ms(EVENT_BOARDS.EXCEL_PARTICIPATE_NOTPARTICIPATED))
            elif outOfScore:
                showPoints = True
                title = getStatusTitleStyle(_ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_OUTOFRATING))
            else:
                visible = False
        elif joined:
            if notFull:
                showPoints = True
                count = getStatusCountStyle(str(cardinality - battleCount))
                title = getStatusTitleStyle(_ms(EVENT_BOARDS.EXCEL_HEADER_REASON_BATTLESLEFT, number=count))
            elif outOfScore:
                showPoints = True
                title = getStatusTitleStyle(_ms(EVENT_BOARDS.STATUS_CANTJOIN_REASON_OUTOFRATING))
            else:
                visible = False
        elif event.isRegistrationFinished():
            title = formatErrorTextWithIcon(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION)
            tooltip = makeTooltip(EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION, EVENT_BOARDS.STATUS_CANTJOIN_REASON_ENDREGISTRATION_TOOLTIP)
        elif canJoin:
            buttonVisible = _psr.SPECIALACCOUNT not in stateReasons
            buttonEnabled = True
        else:
            title, tooltip, buttonVisible = makeCantJoinReasonTextVO(event, self.__playerData)
        if joined and outOfScore and notFull and not event.isFinished():
            method = event.getMethod()
            amount = myInfo.fullData.getLastInLeaderboardValue()
            parameter = event.getObjectiveParameter()
            titleTooltip = makeParameterTooltipVO(method, amount, parameter)
        playerName = getattr(BigWorld.player(), 'name', '')
        playerName = getFullName(playerName, myInfo.fullData.getClanTag(), myInfo.fullData.getClanColor())
        self.as_setStatusVisibleS(visible)
        self.as_setMyPlaceVisibleS(not visible and top is not None)
        if visible:
            p1 = myInfo.fullData.getP1()
            p2 = myInfo.fullData.getP2()
            p3 = myInfo.fullData.getP3()
            self.as_setStatusDataS(makeEventBoardsTableViewStatusVO(title, tooltip, playerName, p1, p2, p3, showPoints, buttonLabel, buttonTooltip, buttonVisible, buttonEnabled, titleTooltip))
        return

    def __calculateRewardCategories(self, rewardGroups, leaderboardViewSize):
        rewardCategories = {}
        last = 0
        for group in rewardGroups:
            rankMin, rankMax = group.getRankMinMax()
            number = group.getRewardCategoryNumber()
            if number not in rewardCategories:
                rewardCategories[number] = {'rank_min': leaderboardViewSize,
                 'rank_max': 0,
                 'rewards': []}
            category = rewardCategories[number]
            category['rank_min'] = min(rankMin, category['rank_min'])
            category['rank_max'] = max(rankMax, category['rank_max'])
            category['rewards'].append(group.getRewards())
            last = max(last, rankMax)

        if last < leaderboardViewSize:
            rewardCategories[self.MAX_CATEGORY] = {'rank_min': last + 1,
             'rank_max': leaderboardViewSize,
             'rewards': []}
        return rewardCategories

    def __updateRewardCategoriesPlayers(self, rewardCategories, rewards, excelItems):
        last = 0
        categoryPages = {reward.getRewardCategoryNumber():reward.getPageNumber() for reward in rewards}
        for number in range(self.MIN_CATEGORY, self.MAX_CATEGORY + 1):
            if number not in rewardCategories:
                continue
            category = rewardCategories[number]
            category['page_number'] = categoryPages.get(number)
            players = category['players'] = []
            for item in excelItems[last:]:
                if category['rank_min'] <= item.getRank() <= category['rank_max']:
                    players.append(item)
                    last += 1
                if item.getRank() > category['rank_max']:
                    break

    def __setPlayerData(self):
        self.__playerData = self.eventsController.getPlayerEventsData()
        self.__playerState = self.__playerData.getPlayerStateByEventId(self.__eventID)

    def __fetchEventData(self):
        eventData = self.eventsController.getEventsSettingsData().getEvent(self.__eventID)
        rewardByRank = eventData.getRewardsByRank().getRewardByRank(self.__leaderboardID) if eventData else None
        if eventData is None or rewardByRank is None:
            self.__setMaintenance(True)
        else:
            self.__setMaintenance(False)
            self.__eventData = eventData
            self.__rewardCategories = self.__calculateRewardCategories(rewardByRank.getRewardGroups(), eventData.getLeaderboardViewSize())
            type = eventData.getType()
            leaderboardValue = eventData.getLeaderboard(self.__leaderboardID)
            objectiveParameter = eventData.getObjectiveParameter()
            self.__method = eventData.getMethod()
            self.as_setMyPlaceVisibleS(False)
            self.__updateHeader()
            self.as_setBackgroundS(makeTableViewBackgroundVO(type, leaderboardValue))
            self.as_setTableHeaderDataS(makeTableHeaderVO(self.__method, objectiveParameter, type))
            self.__setPlayerData()
            myEventsTop = self.eventsController.getMyEventsTopData()
            self.__top = myEventsTop.getMyLeaderboardEventTop(self.__eventID, self.__leaderboardID)
            self.__fetchMyLeaderboardInfo(self.__moveToMyPlace)
        return

    @process
    def __fetchLeaderboardPageData(self, page, rank):
        self.__setWaiting(True)
        leaderboard = yield self.eventsController.getLeaderboard(self.__eventID, self.__leaderboardID, page)
        self.__setWaiting(False)
        if leaderboard is None:
            self.__setMaintenance(True)
        else:
            self.__setMaintenance(False)
            excelItems = leaderboard.getExcelItems()
            pageNumber = leaderboard.getPageNumber()
            pagesAmount = leaderboard.getPagesAmount()
            rewards = leaderboard.getRewards()
            self.__leaderboard = leaderboard
            self.__leaderboardData = LeaderboardData(excelItems, pageNumber)
            self.__updateRewardCategoriesPlayers(self.__rewardCategories, rewards, excelItems)
            self.__pagination.updatePage(pageNumber, pagesAmount)
            self.__updateHeader()
            if excelItems:
                self.__updatePage()
                self.__scrollToRank(rank)
                enabledAncors = []
                for categoryIdx in range(self.MIN_CATEGORY, self.MAX_CATEGORY):
                    if categoryIdx in self.__rewardCategories:
                        enable = self.__rewardCategories[categoryIdx].get('page_number') is not None
                        self.__awardGroup.as_setEnabledS(categoryIdx - 1, enable)
                        enabledAncors.append(enable)

                self.__awardGroup.as_setDataS([ idx < len(enabledAncors) for idx in range(self.MAX_AWARD_GROUPS) ])
                self.__awardGroup.as_setTooltipsS(makeAwardGroupDataTooltipVO(self.__rewardCategories, enabledAncors))
                self.as_setMyPlaceTooltipS(makeTooltip(TOOLTIPS.ELEN_ANCOR_MYPOSITION_HEADER, TOOLTIPS.ELEN_ANCOR_MYPOSITION_BODY))
            else:
                self.as_setEmptyDataS(_ms(EVENT_BOARDS.EXCEL_NODATA))
        return

    @process
    def __fetchMyLeaderboardInfo(self, onSuccess):
        self.__setWaiting(True)
        myInfo = yield self.eventsController.getMyLeaderboardInfo(self.__eventID, self.__leaderboardID)
        self.__setWaiting(False)
        if myInfo is None:
            self.__setMaintenance(True)
        else:
            self.__setMaintenance(False)
            pageNumber = myInfo.getPageNumber()
            rank = myInfo.getRank()
            battlesCount = myInfo.getBattlesCount()
            self.__myInfo = MyInfo(myInfo, pageNumber, rank, battlesCount)
            self.__updateStatus()
            onSuccess()
        return

    def __moveToMyPlace(self):
        pageNumber = self.__myInfo.pageNumber
        rank = self.__myInfo.rank
        if pageNumber and rank and rank <= self.__eventData.getLeaderboardViewSize():
            self.__fetchLeaderboardPageData(pageNumber, self.MY_RANK)
        else:
            self.__fetchLeaderboardPageData(1, self.TOP_POSITION_RANK)

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.settings.alias == EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS:
            view.setData(self.__eventData, self.changeLeaderboard, self.__leaderboardID)
        elif view.settings.alias == EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS:
            view.setOpener(self)

    def __updateHeader(self):
        event = self.__eventData
        name = event.getName()
        type = event.getType()
        leaderboard = self.__leaderboard
        leaderboardValue = event.getLeaderboard(self.__leaderboardID)
        if event.isFinished():
            date = BigWorld.wg_getLongDateFormat(event.getEndDateTs())
            status = text_styles.main(_ms(EVENT_BOARDS.TIME_EVENTFINISHED, date=date))
            statusTooltip = None
        elif leaderboard:
            recalculationTS = leaderboard.getLastLeaderboardRecalculationTS()
            recalculationInterval = leaderboard.getRecalculationInterval()
            interval = int(recalculationInterval / ONE_MINUTE)
            status = text_styles.main(formatUpdateTime(recalculationTS))
            statusTooltip = _ms(EVENT_BOARDS.SUMMARY_STATUS_TOOLTIP, interval=interval)
        else:
            status = None
            statusTooltip = None
        self.as_setHeaderDataS(makeTableViewHeaderVO(type, leaderboardValue, name, status, statusTooltip))
        return

    def __updatePage(self):
        data, stripes = makeEventBoardsTableDataVO(self.__rewardCategories, self.__method)
        self.__stripes = stripes
        self.as_setTableDataS(data)
        self.as_setAwardsStripesS(stripes)
        if self.__myInfo.rank is not None:
            myPosition = self.__getMyPosition()
            if myPosition is not None:
                self.as_setMyPlaceS(myPosition)
        return

    def __scrollToRank(self, rank):
        if rank == self.TOP_POSITION_RANK:
            self.as_setScrollPosS(0, False)
            categoryNumber = self.__getCategoryByRank(self.__leaderboardData.excelItems[0].getRank())
        elif rank == self.MY_RANK:
            self.as_setScrollPosS(self.__getMyPosition(), True)
            categoryNumber = self.__getCategoryByRank(self.__myInfo.rank)
        else:
            self.as_setScrollPosS(self.__getPositionByRank(rank), False)
            categoryNumber = self.__getCategoryByRank(rank)
        if self.MIN_CATEGORY < categoryNumber <= self.MAX_CATEGORY - 1:
            self.__awardGroup.setActiveRewardGroup(categoryNumber)

    @dependency.replace_none_kwargs(connectionMgr=IConnectionManager)
    def __getMyPosition(self, connectionMgr=None):
        if connectionMgr is not None:
            mySpaID = connectionMgr.databaseID
            for idx, item in enumerate(self.__leaderboardData.excelItems):
                if item.getSpaId() == mySpaID:
                    startCategoryNumber = self.__getCategoryByRank(self.__leaderboardData.excelItems[0].getRank())
                    currentCategoryNumber = self.__getCategoryByRank(item.getRank())
                    if startCategoryNumber and currentCategoryNumber:
                        return idx + 1 + (currentCategoryNumber - startCategoryNumber)
                    break

        return

    def __getPositionByRank(self, rank):
        for idx, item in enumerate(self.__leaderboardData.excelItems):
            if item.getRank() >= rank:
                startCategoryNumber = self.__getCategoryByRank(self.__leaderboardData.excelItems[0].getRank())
                currentCategoryNumber = self.__getCategoryByRank(rank)
                if startCategoryNumber and currentCategoryNumber:
                    return idx + 1 + (currentCategoryNumber - startCategoryNumber)
                break

        return None

    def __getCategoryByRank(self, rank):
        for number, category in self.__rewardCategories.iteritems():
            if category['rank_min'] <= rank <= category['rank_max']:
                return number
