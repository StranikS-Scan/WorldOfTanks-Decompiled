# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/session_stats/session_stats_settings_controller.py
import copy
import logging
from account_helpers.settings_core.settings_constants import SESSION_STATS
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
MAX_STATS = 8
DEFAULT_CORE_SETTINGS = {SESSION_STATS.IS_NEEDED_SAVE_CURRENT_TAB: False,
 SESSION_STATS.IS_NOT_NEEDED_RESET_STATS_EVERY_DAY: False,
 SESSION_STATS.CURRENT_TAB: SESSION_STATS.BATTLES_TAB,
 SESSION_STATS.ECONOMIC_BLOCK_VIEW: 0,
 SESSION_STATS.SHOW_WTR: True,
 SESSION_STATS.SHOW_RATIO_DAMAGE: True,
 SESSION_STATS.SHOW_RATIO_KILL: True,
 SESSION_STATS.SHOW_WINS: True,
 SESSION_STATS.SHOW_AVERAGE_DAMAGE: True,
 SESSION_STATS.SHOW_HELP_DAMAGE: True,
 SESSION_STATS.SHOW_BLOCKED_DAMAGE: True,
 SESSION_STATS.SHOW_AVERAGE_XP: True,
 SESSION_STATS.SHOW_WIN_RATE: False,
 SESSION_STATS.SHOW_AVERAGE_VEHICLE_LEVEL: False,
 SESSION_STATS.SHOW_AVERAGE_FRAGS: False,
 SESSION_STATS.SHOW_SURVIVED_RATE: False,
 SESSION_STATS.SHOW_SPOTTED: False}

class SessionStatsSettingsController(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__cacheSettings = self.settingsCore.serverSettings.getSessionStatsSettings()

    def start(self):
        self.itemsCache.onSyncCompleted += self.__updateSettingsCache

    def stop(self):
        self.itemsCache.onSyncCompleted -= self.__updateSettingsCache

    def setSettings(self, settings):
        if not self.validateSettings(settings):
            _logger.warning('Efficiency block parameters more than max')
            return
        self.__cacheSettings = copy.deepcopy(settings)
        self.settingsCore.serverSettings.setSessionStatsSettings(settings)

    def setCurrentTab(self, currentTab):
        self.__cacheSettings.update({SESSION_STATS.CURRENT_TAB, currentTab})
        self.settingsCore.serverSettings.setSessionStatsSettings({SESSION_STATS.CURRENT_TAB, currentTab})

    def getSettings(self):
        return copy.deepcopy(self.__cacheSettings)

    def setDefaultSettings(self):
        self.__cacheSettings = copy.deepcopy(DEFAULT_CORE_SETTINGS)
        self.settingsCore.serverSettings.setSessionStatsSettings(DEFAULT_CORE_SETTINGS)

    def getDefaultSettings(self):
        return DEFAULT_CORE_SETTINGS.copy()

    @staticmethod
    def validateSettings(settings):
        efficiencyBlockParametersList = [ settings[key] for key in SESSION_STATS.getEfficiencyBlock() ]
        return False if sum(efficiencyBlockParametersList) > MAX_STATS else True

    def __updateSettingsCache(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self.__cacheSettings = self.settingsCore.serverSettings.getSessionStatsSettings()
