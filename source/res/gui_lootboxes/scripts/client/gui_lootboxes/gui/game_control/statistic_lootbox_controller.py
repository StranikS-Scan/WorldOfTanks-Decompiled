# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/game_control/statistic_lootbox_controller.py
import logging
import Event
from account_helpers.AccountSettings import LOOT_BOXES_STATS_HINT_STATE, LOOT_BOXES_STATS_NO_BOX_HINT_STATE
from constants import Configs
from gui_lootboxes.gui.lb_gui_constants import TRIGGER_HINT_STATES
from gui_lootboxes.gui.statistic_helpers.pdata_fetcher import LBPDataFetcher
from gui_lootboxes.gui.statistic_helpers.statistic_data_provider import StatisticDataCache
from gui_lootboxes.skeletons.statistic_lootbox_controller import IStatisticLootBoxController
from helpers import dependency, server_settings
from lootboxes_common import mergeDiffStat
from skeletons.gui.game_control import IGuiLootBoxesController
from shared_utils import first
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class StatisticLootBoxController(IStatisticLootBoxController):
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__em = Event.EventManager()
        self._statLocalCache = StatisticDataCache()
        self.onStatusChanged = Event.Event(self.__em)

    @property
    def onBaseStatCollect(self):
        return self._statLocalCache.onBaseStatCollect

    def onLobbyInited(self, _):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange

    def init(self):
        self._statLocalCache.registerProvider('pdata', LBPDataFetcher)

    def fini(self):
        self._statLocalCache.fini()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def onAccountBecomePlayer(self):
        self._statLocalCache.onAccountBecomePlayer()
        if self.isShowStatistic():
            self.__guiLootBoxes.onOpenLootboxesComplete += self.__updateLocalStat

    def onAccountBecomeNonPlayer(self):
        self._statLocalCache.onAccountBecomeNonPlayer()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def onAvatarBecomePlayer(self):
        self.__guiLootBoxes.onOpenLootboxesComplete -= self.__updateLocalStat

    def onDisconnected(self):
        self._statLocalCache.onDisconnected()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange

    def getFullStatistic(self):
        result = {}
        for stat in self._statLocalCache.allCacheStat:
            mergeDiffStat(result, stat)

        return result

    def getMergeStatByLootboxIDs(self, lootboxIDs):
        result = {}
        for lbID in lootboxIDs:
            localStat = self._statLocalCache.getStatByLootboxID(lbID)
            mergeDiffStat(result, localStat)

        return result

    def getLootboxesExpireInfo(self):
        return self._statLocalCache.expiresInfo

    def getLootBoxesVersionInfo(self, lootboxID=None):
        return self._statLocalCache.getVersionByLootboxID(lootboxID)

    def isNeedShowHint(self, noBoxView=False):
        settingName = LOOT_BOXES_STATS_HINT_STATE
        if noBoxView:
            settingName = LOOT_BOXES_STATS_NO_BOX_HINT_STATE
        state = self.__guiLootBoxes.getSetting(settingName)
        return state == TRIGGER_HINT_STATES.HAVE_TO_SHOW

    def isShowStatistic(self):
        return self.__lobbyContext.getServerSettings().getLootBoxStatisticsConfig().get('enabled')

    def __updateLocalStat(self, res):
        auxData = res.auxData
        lootboxID = first(auxData['extData']['openedLootBoxes'].keys())
        lootbox = self.__itemsCache.items.tokens.getLootBoxByID(lootboxID)
        if lootbox and lootbox.isStatCollected():
            startVerStat = first(auxData['extData'].get('startVerStat', {}).values(), default=0)
            if self._statLocalCache.canApplySnapshot(lootboxID, startVerStat):
                count = auxData['extData']['openedLootBoxes'][lootboxID]
                self._statLocalCache.applyOpenResult(lootboxID, auxData['bonus'], count)
            else:
                self._statLocalCache.requestBaseStat()

    @server_settings.serverSettingsChangeListener(Configs.LOOTBOX_STATISTICS_CONFIG.value)
    def __onServerSettingsChange(self, diff):
        diff = diff[Configs.LOOTBOX_STATISTICS_CONFIG.value]
        self.onStatusChanged(diff)
        self._statLocalCache.onServerSettingsChanged(diff)
        if diff['enabled']:
            self.__guiLootBoxes.onOpenLootboxesComplete += self.__updateLocalStat
        else:
            self.__guiLootBoxes.onOpenLootboxesComplete -= self.__updateLocalStat
