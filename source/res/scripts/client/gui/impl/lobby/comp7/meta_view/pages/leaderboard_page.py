# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/leaderboard_page.py
import logging
import typing
import BigWorld
import adisp
from gui.impl.backport import BackportContextMenuWindow, createContextMenuData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.division_info_model import Division
from gui.impl.gen.view_models.views.lobby.comp7.leaderboard_navigation_division_info import LeaderboardNavigationDivisionInfo
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.leaderboard_model import LeaderboardModel, State
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.table_record_model import TableRecordModel, Rank
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.comp7 import comp7_shared
from gui.impl.lobby.comp7.meta_view.meta_view_helper import setDivisionData
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from gui.impl.lobby.comp7.tooltips.division_tooltip import DivisionTooltip
from gui.impl.lobby.comp7.tooltips.leaderboard_reward_tooltip import LeaderboardRewardTooltip
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.event_boards.event_boards_items import ExcelItem
_logger = logging.getLogger(__name__)

def _getBackportContextMenuData(event):
    contextMenuArgs = {'dbID': event.getArgument('spaID'),
     'userName': event.getArgument('userName')}
    return createContextMenuData(CONTEXT_MENU_HANDLER_TYPE.COMP_LEADERBOARD_USER, contextMenuArgs)


class LeaderboardPage(PageSubModelPresenter):
    __slots__ = ('__elitePosition', '__loadingStateManager', '__requestedPageData', '__lastUpdateTime')
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, viewModel, parentView):
        super(LeaderboardPage, self).__init__(viewModel, parentView)
        self.__elitePosition = -1
        self.__loadingStateManager = None
        self.__requestedPageData = (self.viewModel.PAGE_SIZE, 0)
        self.__lastUpdateTime = 0
        return

    @property
    def pageId(self):
        return MetaRootViews.LEADERBOARD

    @property
    def viewModel(self):
        return super(LeaderboardPage, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.comp7.tooltips.DivisionTooltip():
            params = {'rank': Rank(event.getArgument('rank')),
             'division': Division(event.getArgument('division')),
             'from': event.getArgument('from'),
             'to': event.getArgument('to'),
             'type': event.getArgument('type'),
             'elitePercent': event.getArgument('elitePercent')}
            return DivisionTooltip(params=params)
        if contentID == R.views.lobby.comp7.tooltips.LeaderboardRewardTooltip():
            place = event.getArgument('place', 0)
            return LeaderboardRewardTooltip(place)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = _getBackportContextMenuData(event)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.parentView.getParentWindow())
                window.load()
                return window
        return

    def initialize(self, *args, **kwargs):
        super(LeaderboardPage, self).initialize(*args, **kwargs)
        self.viewModel.setState(State.INITIAL)
        self.viewModel.setTopPercentage(self.__comp7Controller.leaderboard.getEliteRankPercent())
        self.viewModel.setOwnSpaID(self.__connectionMgr.databaseID)
        self.viewModel.setFrom(self.__comp7Controller.leaderboard.getMinimumPointsNeeded())
        self.__loadingStateManager = _LoadingStateManager(self.viewModel)
        self.__updateData()

    def finalize(self):
        super(LeaderboardPage, self).finalize()
        self.__comp7Controller.leaderboard.flushTableRecords()
        self.__loadingStateManager = None
        return

    def _getEvents(self):
        return ((self.viewModel.onRefresh, self.__onRefresh), (self.viewModel.getTableRecords, self.__getTableRecords), (self.__comp7Controller.onComp7RanksConfigChanged, self.__onRanksConfigChanged))

    def __onRefresh(self, *_):
        self.viewModel.setState(State.INITIAL)
        self.__updateData()

    def __onRanksConfigChanged(self):
        self.viewModel.setTopPercentage(self.__comp7Controller.leaderboard.getEliteRankPercent())

    @args2params(int, int)
    def __getTableRecords(self, limit, offset):
        self.__requestedPageData = (limit, offset)
        self.__updateData()

    def __updateData(self):
        limit, offset = self.__requestedPageData
        loadingChainMark = BigWorld.time()
        self.__requestRecords(limit, offset, loadingChainMark)
        self.__updateCommonRemoteData(loadingChainMark)
        self.__updatePersonalData(loadingChainMark)

    @adisp.adisp_process
    def __requestRecords(self, limit, offset, loadingChainMark):
        managerGeneration = self.__loadingStateManager.startRequest(loadingChainMark)
        records = yield self.__comp7Controller.leaderboard.getTableRecords(limit, offset)
        if not self.__isResultExpected(managerGeneration):
            return
        else:
            if records is not None:
                self.__updateRecords(records)
            else:
                self.__updateRecords([])
                self.__loadingStateManager.finishRequest(loadingChainMark, False)
                return
            recordsCount, isSuccess = yield self.__comp7Controller.leaderboard.getRecordsCount()
            if not self.__isResultExpected(managerGeneration):
                return
            self.viewModel.setRecordsCount(recordsCount or 0)
            self.__loadingStateManager.finishRequest(loadingChainMark, isSuccess)
            return

    def __updateRecords(self, records):
        with self.viewModel.transaction() as vm:
            tableRecords = vm.getItems()
            tableRecords.clear()
            for record in records:
                itemModel = self.__getRecordModel(record)
                tableRecords.addViewModel(itemModel)

            tableRecords.invalidate()
            vm.setState(State.SUCCESS)

    @adisp.adisp_process
    def __updateCommonRemoteData(self, loadingChainMark):
        managerGeneration = self.__loadingStateManager.startRequest(loadingChainMark)
        lastUpdateTime, isSuccess = yield self.__comp7Controller.leaderboard.getLastUpdateTime()
        if not self.__isResultExpected(managerGeneration):
            return
        else:
            if isSuccess:
                self.__lastUpdateTime = lastUpdateTime
                self.viewModel.setLeaderboardUpdateTimestamp(lastUpdateTime)
            else:
                self.__loadingStateManager.finishRequest(loadingChainMark, False)
                return
            elitePosition, isSuccess = yield self.__comp7Controller.leaderboard.getLastElitePosition()
            if not self.__isResultExpected(managerGeneration):
                return
            self.__elitePosition = elitePosition - 1 if elitePosition is not None else -1
            self.viewModel.setLastBestUserPosition(self.__elitePosition)
            divisionsFirstPositions, isSuccess = yield self.__comp7Controller.leaderboard.getDivisionsFirstPositions()
            if not self.__isResultExpected(managerGeneration):
                return
            if isSuccess:
                self.__buildNavigation(divisionsFirstPositions)
            self.__loadingStateManager.finishRequest(loadingChainMark, isSuccess)
            return

    @adisp.adisp_process
    def __updatePersonalData(self, loadingChainMark):
        managerGeneration = self.__loadingStateManager.startRequest(loadingChainMark)
        result = yield self.__comp7Controller.leaderboard.getOwnData()
        if not self.__isResultExpected(managerGeneration):
            return
        else:
            if result.isSuccess:
                self.viewModel.setPersonalPosition(result.position - 1 if result.position is not None else -1)
                self.viewModel.setPersonalScore(result.points or 0)
                self.viewModel.setPersonalBattlesCount(result.battlesCount or 0)
                self.__loadingStateManager.finishRequest(loadingChainMark, True)
            else:
                self.__loadingStateManager.finishRequest(loadingChainMark, False)
            return

    def __isResultExpected(self, generation):
        return self.isLoaded and self.__loadingStateManager is not None and self.__loadingStateManager.isValidGeneration(generation)

    def __getRecordModel(self, record):
        position = record.getRank()
        model = TableRecordModel()
        rank = comp7_shared.getRankByDivisionId(record.getP1())
        model.setRank(rank if rank else Rank.FIRST)
        model.setScore(record.getP2())
        model.setBattlesCount(record.getP3())
        model.setPosition(position - 1)
        model.setSpaID(record.getSpaId())
        model.setClanTag(record.getClanTag() or '')
        model.setClanTagColor(record.getClanColor() or '')
        model.setUserName(record.getName())
        model.setDivision(comp7_shared.getDivisionNameById(record.getP1()))
        return model

    def __buildNavigation(self, positions):
        items = self.viewModel.getDivisions()
        items.clear()
        divisions = self.__comp7Controller.leaderboard.getLeaderboardDivisions()
        for division in divisions:
            divisionModel = LeaderboardNavigationDivisionInfo()
            divisionModel.setRankId(division.rank)
            setDivisionData(divisionModel, division)
            firstMemberPosition = positions.get(str(division.dvsnID))
            if firstMemberPosition is not None:
                divisionModel.setFirstMemberPosition(firstMemberPosition)
            items.addViewModel(divisionModel)

        items.invalidate()
        return


class _LoadingStateManager(object):
    __REQUESTS_COUNT_KEY = 'requestsCount'
    __ERRORS_KEY = 'errors'
    __generation = 0

    def __init__(self, viewModel):
        self.__viewModel = viewModel
        self.__registeredChains = {}
        self.__class__.__generation += 1
        _logger.debug('Created new loading state manager, generation %d', self.__generation)

    def startRequest(self, chainMark):
        if chainMark not in self.__registeredChains:
            self.__registeredChains[chainMark] = self.__makeNewChainBlock()
            self.__viewModel.setIsLoading(True)
        self.__registeredChains[chainMark][self.__REQUESTS_COUNT_KEY] += 1
        return self.__generation

    def isValidGeneration(self, generation):
        return self.__generation == generation

    def finishRequest(self, chainMark, isSuccessfull):
        if chainMark not in self.__registeredChains:
            _logger.error('Finished not registered request')
            return
        chainInfo = self.__registeredChains[chainMark]
        chainInfo[self.__REQUESTS_COUNT_KEY] -= 1
        if not isSuccessfull:
            chainInfo[self.__ERRORS_KEY] += 1
            self.__viewModel.setState(State.ERROR)
        if chainInfo[self.__REQUESTS_COUNT_KEY] == 0:
            del self.__registeredChains[chainMark]
            self.__viewModel.setIsLoading(bool(self.__registeredChains))
            self.__viewModel.setState(State.ERROR if chainInfo[self.__ERRORS_KEY] > 0 else State.SUCCESS)

    @classmethod
    def __makeNewChainBlock(cls):
        return {cls.__REQUESTS_COUNT_KEY: 0,
         cls.__ERRORS_KEY: 0}
