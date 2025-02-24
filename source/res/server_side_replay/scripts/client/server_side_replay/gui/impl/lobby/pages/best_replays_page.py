# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/pages/best_replays_page.py
import logging
import time
from typing import TYPE_CHECKING, Optional, List
import BigWorld
from BattleReplay import BattleReplay
from adisp import adisp_process
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui import layouts
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from server_side_replay.gui.impl.gen.view_models.views.lobby.filter_toggle_group_model import ToggleGroupType
from server_side_replay.gui.impl.gen.view_models.views.lobby.pages.best_replays_model import BestReplaysModel
from server_side_replay.gui.impl.gen.view_models.views.lobby.replay_model import ReplayModel, MarksOfMastery
from server_side_replay.gui.impl.gen.view_models.views.lobby.enums import ReplaysViews
from server_side_replay.gui.impl.gen.view_models.views.lobby.table_base_model import State
from server_side_replay.gui.impl.gen.view_models.views.lobby.top_replay_model import StatParams, TopReplayModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from server_side_replay.gui.impl.lobby.filter import getVehicleTypeSettings, getNationSettings, getVehicleTierSettings
from server_side_replay.gui.impl.lobby.filter.state import FilterState
from server_side_replay.gui.impl.lobby.pages import PageSubModelPresenter
from server_side_replay.gui.impl.lobby.popovers.replays_filter_popover_view import ReplaysFilterPopoverView
from server_side_replay.gui.impl.lobby.utils import WebReplaysHelper
from gui.impl.pub import PopOverWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.gui_items.dossier import getAchievementFactory
from gui.shared.gui_items.dossier.achievements import MarkOfMasteryAchievement
from server_side_replay.gui.wgcg.data_wrappers.server_replays import DataNames, StatParams as DataStatParams
from server_side_replay.gui.wgcg.providers.server_replays_provider import ServerReplaysProvider
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from server_side_replay.gui.wgcg.data_wrappers import server_replays
_logger = logging.getLogger(__name__)
TOP_REPLAYS_COUNT = 3
_DataToModelStatParam = {DataStatParams.DAMAGE_ASSISTED: StatParams.DAMAGEASSISTED,
 DataStatParams.DAMAGE_DEALT: StatParams.DAMAGEDEALT,
 DataStatParams.DAMAGE_BLOCKED: StatParams.DAMAGEBLOCKEDBYARMOR,
 DataStatParams.EXP: StatParams.EARNEDXP,
 DataStatParams.KILLS: StatParams.KILLS,
 DataStatParams.MARK_OF_MASTERY: StatParams.MARKSOFMASTERY}
_ModelToDataStatParam = {v:k for k, v in _DataToModelStatParam.items()}
_DataToModelMarkOfMastery = {MarkOfMasteryAchievement.MARK_OF_MASTERY.MASTER: MarksOfMastery.MASTER,
 MarkOfMasteryAchievement.MARK_OF_MASTERY.STEP_3: MarksOfMastery.THIRD,
 MarkOfMasteryAchievement.MARK_OF_MASTERY.STEP_2: MarksOfMastery.SECOND,
 MarkOfMasteryAchievement.MARK_OF_MASTERY.STEP_1: MarksOfMastery.FIRST}

class BestReplaysPage(PageSubModelPresenter):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView):
        self.__tooltips = {}
        self.__selectedSortBy = None
        self.__callback = None
        self.__selectedVehID = 0
        self.__cachedBestReplaysData = None
        self.__cachedTopReplaysData = None
        self.__filterState = FilterState()
        self.__loadingData = []
        self.__serverReplayProvider = ServerReplaysProvider()
        self.__serverReplayProvider.start()
        super(BestReplaysPage, self).__init__(viewModel, parentView)
        return

    @property
    def pageId(self):
        return ReplaysViews.BESTREPLAYS

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        self.__updateState()
        super(BestReplaysPage, self).initialize(*args, **kwargs)

    def hasAppliedFilters(self):
        for groupID in self.__filterState:
            if self.__filterState[groupID]:
                return True
            if self.__filterState.isPrimeTime:
                return True
            if self.__filterState.lastDays != 14:
                return True

        return len(self.__filterState.searchString) > 0

    def createPopOver(self, event):
        if event.contentID == R.views.server_side_replay.lobby.popovers.ReplaysFilterPopover():
            content = ReplaysFilterPopoverView((getVehicleTypeSettings(), getNationSettings(), getVehicleTierSettings()), self.__onPopoverStateUpdated, self.__filterState, True, self.hasAppliedFilters)
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.load()
            return window
        super(BestReplaysPage, self).createPopOver(event)

    def _getEvents(self):
        return super(BestReplaysPage, self)._getEvents() + ((self.__serverReplayProvider.onDataReceived, self.__onDataReceived),
         (self.__serverReplayProvider.onDataFailed, self.__onDataFailed),
         (self.viewModel.onResetFilter, self.__onResetFilter),
         (self.viewModel.onLike, self.__onLike),
         (self.viewModel.onSort, self.__onSort),
         (self.viewModel.onRefresh, self.__onRefresh),
         (self.viewModel.onWatch, self.__onWatch),
         (self.viewModel.onTopReplaysWatch, self.__onTopReplaysWatch))

    def __onPopoverStateUpdated(self, clearCallback=False):
        _logger.warning('Popover updated')
        if clearCallback:
            self.__callback = None
        with self.viewModel.transaction() as tx:
            self.__updateFilter(tx)
            if self.__loadingData:
                if self.__callback is None:
                    self.__callback = BigWorld.callback(0.1, lambda : self.__onPopoverStateUpdated(True))
                return
            self.__updateState(model=tx)
        return

    @replaceNoneKwargsModel
    def __updateState(self, loadedData=None, model=None):
        if loadedData in self.__loadingData:
            self.__loadingData.remove(loadedData)
            if not self.__loadingData:
                model.setState(State.SUCCESS)
                model.setIsLoading(False)
            return
        else:
            bestReplaysObj = self.__serverReplayProvider.getBestReplays(useFake=False, vehicleType=list(self.__filterState[ToggleGroupType.VEHICLETYPE.value]), vehicleLevel=list(self.__filterState[ToggleGroupType.VEHICLETIER.value]), nation=list(self.__filterState[ToggleGroupType.NATION.value]), vehicleCDs=list(self.__filterState[ToggleGroupType.VEHICLECD.value]), fromDate=time.time() - self.__filterState.lastDays * 24 * 60 * 60, isPrimeTime=self.__filterState.isPrimeTime, sortBy=_ModelToDataStatParam.get(self.__selectedSortBy, StatParams.EARNEDXP.value))
            if bestReplaysObj.isWaitingResponse and DataNames.BEST_REPLAYS not in self.__loadingData:
                self.__loadingData.append(DataNames.BEST_REPLAYS)
            topReplaysObj = self.__serverReplayProvider.getTopReplays(useFake=False)
            if topReplaysObj.isWaitingResponse and DataNames.TOP_REPLAYS not in self.__loadingData:
                self.__loadingData.append(DataNames.TOP_REPLAYS)
            if topReplaysObj.data:
                self.__cachedTopReplaysData = topReplaysObj.data
            if bestReplaysObj.isWaitingResponse and bestReplaysObj.data is None or topReplaysObj.isWaitingResponse:
                model.setState(State.INITIAL)
            if self.__loadingData:
                model.setIsLoading(True)
                return
            self.__cachedBestReplaysData = bestReplaysObj.data
            if self.__cachedBestReplaysData is None or self.__cachedTopReplaysData is None:
                model.setState(State.ERROR)
                return
            model.setState(State.SUCCESS)
            self.__updateReplays(self.__cachedBestReplaysData, self.__cachedTopReplaysData)
            return

    @replaceNoneKwargsModel
    def __updateReplays(self, allReplaysData, topReplaysData, model=None):
        _logger.info('__updateReplays: %s', allReplaysData)
        replayArray = model.getItems()
        replayArray.clear()
        for replayInfo in allReplaysData.rankings:
            replayArray.addViewModel(self.__makeReplayModel(replayInfo))

        replayArray.invalidate()
        topReplaysArray = model.getTopReplays()
        topReplaysArray.clear()
        for stat in (DataStatParams.DAMAGE_DEALT, DataStatParams.DAMAGE_ASSISTED, DataStatParams.DAMAGE_BLOCKED):
            replayInfo = getattr(topReplaysData, stat)
            if len(topReplaysArray) >= TOP_REPLAYS_COUNT:
                _logger.warning('Count of top replays more than allowed - %s', TOP_REPLAYS_COUNT)
                break
            topReplaysArray.addViewModel(self.__makeTopReplayModel(replayInfo, stat))

        self.__updateFilter(model=model)

    def __makeReplayModel(self, replayInfo, model=None):
        replayModel = model or ReplayModel()
        replayModel.setId(str(replayInfo.replay_id))
        replayModel.setIsFavorite(False)
        replayModel.setArenaName(replayInfo.map)
        replayModel.setTimestamp(replayInfo.battle_start)
        replayModel.setEarnedXp(replayInfo.exp)
        replayModel.setDamageDealt(replayInfo.damage_dealt)
        replayModel.setDamageAssisted(replayInfo.damage_assisted)
        replayModel.setDamageBlockedByArmor(replayInfo.damage_blocked)
        replayModel.setKills(replayInfo.kills_made)
        replayModel.setMarksOfMastery(_DataToModelMarkOfMastery.get(replayInfo.mastery_mark, MarksOfMastery.NONE))
        epicMedals = replayModel.getEpicMedals()
        for record in replayInfo.achievements:
            a_id = record.get('achievement_type_id')
            a_value = record.get('achievement_value')
            record = DB_ID_TO_RECORD[a_id]
            factory = getAchievementFactory(record)
            if factory is not None and layouts.isAchievementRegistered(record):
                achievement = factory.create(value=a_value)
                a_name = achievement.getUserName()
                if a_name not in epicMedals:
                    epicMedals.addString(a_name)

        try:
            vehicle = self.__itemsCache.items.getItemByCD(replayInfo.vehicle_cd)
            fillVehicleModel(replayModel.vehicleInfo, vehicle)
        except:
            vehicle = self.__itemsCache.items.getItemByCD(13377)
            fillVehicleModel(replayModel.vehicleInfo, vehicle)
            replayModel.vehicleInfo.setName('UnknownVeihlce{}'.format(replayInfo.vehicle_cd))

        playerModel = replayModel.playerInfo
        playerModel.setSpaID(replayInfo.spa_id or 0)
        playerModel.setUserName(replayInfo.nickname)
        playerModel.setClanTag(replayInfo.clan_tag)
        playerModel.setClanTagColor('#' + hex(replayInfo.clan_color)[2:].zfill(6) if replayInfo.clan_color is not None else '')
        return replayModel

    def __makeTopReplayModel(self, replayInfo, stat):
        model = self.__makeReplayModel(replayInfo, TopReplayModel())
        model.setParam(_DataToModelStatParam.get(stat, StatParams.EARNEDXP))
        return model

    def __updateFilter(self, model=None):
        model.setIsPopoverEnabled(True)
        model.setIsPopoverHighlighted(self.hasAppliedFilters())

    def __onResetFilter(self, *args):
        _logger.info('__onResetFilter: %s', args)
        self.__filterState.clear()
        self.__updateState()

    @args2params(int)
    def __onWatch(self, index):
        _logger.info('__onLike: %s', index)
        if not self.__cachedBestReplaysData:
            return
        replayID = self.__cachedBestReplaysData.rankings[index].replay_id
        self.__selectedVehID = self.__cachedBestReplaysData.rankings[index].vehicle_entity_id
        self.__serverReplayProvider.getReplayLink(replayID, useFake=False)

    @args2params(int)
    def __onTopReplaysWatch(self, index):
        _logger.info('__onLike: %s', index)
        if not self.__cachedTopReplaysData:
            return
        replayM = self.viewModel.getTopReplays()[index]
        stat = _ModelToDataStatParam.get(replayM.getParam())
        replayD = getattr(self.__cachedTopReplaysData, stat)
        replayID = replayD.replay_id
        self.__selectedVehID = replayD.vehicle_entity_id
        self.__serverReplayProvider.getReplayLink(replayID, useFake=False)

    @args2params(int)
    def __onLike(self, index):
        _logger.info('__onLike: %s', index)
        if not self.__cachedBestReplaysData:
            return
        replayID = self.__cachedBestReplaysData.rankings[index].replay_id
        self.__selectedVehID = self.__cachedBestReplaysData.rankings[index].vehicle_entity_id
        self.__serverReplayProvider.getReplayLink(replayID, useFake=False)

    @adisp_process
    def __playReplay(self, replayLink):
        _logger.info('__playReplay: %s', replayLink)
        helper = WebReplaysHelper()
        relativePath = yield helper.getRelativePath(replayLink.replay_link)
        _logger.info('__downloaded replay: %s', relativePath)
        self.__playReplay2(relativePath)

    def __playReplay2(self, relativePath):
        _logger.info('__playReplay2: %s', relativePath)
        BattleReplay.predefinedVehicleID = self.__selectedVehID
        BigWorld.player().startWatchingReplay(relativePath)

    @args2params(unicode)
    def __onSort(self, param):
        _logger.info('__onSort: %s', param)
        self.__selectedSortBy = StatParams(param)
        with self.viewModel.transaction() as tx:
            tx.setSelectedSorting(self.__selectedSortBy)
            self.__updateState(model=tx)

    def __onRefresh(self):
        self.__filterState.clear()
        self.__updateState()

    def __onDataReceived(self, dataName, data):
        if dataName not in (DataNames.BEST_REPLAYS, DataNames.TOP_REPLAYS, DataNames.REPLAY_LINK):
            return
        if dataName == DataNames.BEST_REPLAYS:
            self.__cachedBestReplaysData = data
        elif dataName == DataNames.TOP_REPLAYS:
            self.__cachedTopReplaysData = data
        elif dataName == DataNames.REPLAY_LINK:
            self.__playReplay(data)
            return
        with self.viewModel.transaction() as tx:
            self.__updateState(loadedData=dataName, model=tx)
            if all((self.__cachedBestReplaysData, self.__cachedTopReplaysData)):
                self.__updateReplays(self.__cachedBestReplaysData, self.__cachedTopReplaysData, model=tx)

    def __onDataFailed(self, dataName):
        with self.viewModel.transaction() as tx:
            if dataName in self.__loadingData:
                self.__loadingData.remove(dataName)
                if not self.__loadingData:
                    tx.setState(State.SUCCESS)
                    tx.setIsLoading(False)
            if dataName in (DataNames.BEST_REPLAYS, DataNames.TOP_REPLAYS):
                tx.setState(State.ERROR)
            elif dataName == DataNames.REPLAY_LINK:
                pass
