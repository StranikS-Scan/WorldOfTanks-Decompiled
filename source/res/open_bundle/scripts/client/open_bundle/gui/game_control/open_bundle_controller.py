# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/gui/game_control/open_bundle_controller.py
from __future__ import absolute_import
import logging
from Event import EventManager, Event
from PlayerEvents import g_playerEvents
from functools import partial
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.server_settings import serverSettingsChangeListener
from helpers.time_utils import getServerUTCTime, ONE_DAY
from open_bundle.gui.constants import RARE_TAG, UNIC_NOTIFICATION_TAG
from open_bundle.helpers.bonuses.bonus_layout_config import BonusLayoutConfig
from open_bundle.helpers.bonuses.optional_bonuses import parseBonusData
from open_bundle.helpers.server_settings import BundlesConfig
from open_bundle.helpers.switch_hangar_helper import SwitchHangarHelper
from open_bundle.helpers.sync_data import OpenBundleSyncData
from open_bundle.skeletons.open_bundle_controller import IOpenBundleController
from open_bundle_common.constants import OPEN_BUNDLE_GAME_PARAMS_KEY, OPEN_BUNDLE_PDATA_KEY
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class OpenBundleController(IOpenBundleController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__settingsConfig = None
        self.__bonusLayoutConfig = BonusLayoutConfig()
        self.__syncData = OpenBundleSyncData()
        self.__switchHelper = SwitchHangarHelper()
        self.__eventsManager = EventManager()
        self.__statusChangeNotifiers = []
        self.onSettingsChanged = Event(self.__eventsManager)
        self.onStatusChanged = Event(self.__eventsManager)
        return

    @property
    def bundleIDs(self):
        return self.config.getBundleIDs()

    @property
    def config(self):
        if self.__settingsConfig is None:
            self.__settingsConfig = self.__createConfig()
        return self.__settingsConfig

    def onLobbyInited(self, _):
        self.__startNotifiers()
        self._subscribe()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()
        self.__clear()

    def init(self):
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__bonusLayoutConfig.init()

    def fini(self):
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__stop()
        self.__clear()
        self.__eventsManager.clear()
        self.__bonusLayoutConfig.clear()

    def isEnabled(self, bundleID):
        return self.config.getBundle(bundleID).enabled

    def getBundle(self, bundleID):
        return self.config.getBundle(bundleID)

    def isBundleActive(self, bundleID):
        if self.isEnabled(bundleID):
            return self.getBundle(bundleID).start <= getServerUTCTime() < self.getBundle(bundleID).finish
        return False

    def isRareCell(self, bundleID, cellName):
        return RARE_TAG in self.config.getBundle(bundleID).cells.get(cellName).tags

    def isUnicNotificationCell(self, bundleID, cellName):
        return UNIC_NOTIFICATION_TAG in self.config.getBundle(bundleID).cells.get(cellName).tags

    def getCellBonusInfo(self, bundleID, cellName):
        bonusData = self.config.getBundle(bundleID).bonus
        return parseBonusData(bonusData).get(cellName) or {}

    def getBundleTimeLeft(self, bundleID):
        return max(0, self.getBundle(bundleID).finish - getServerUTCTime())

    def isAllBundleCellsReceived(self, bundleID):
        return len(self.__syncData.getTrackedByNameSections(bundleID).keys()) == len(self.config.getBundle(bundleID).cells)

    def getReceivedCells(self, bundleID):
        return self.__syncData.getTrackedByNameSections(bundleID).keys()

    def getBonusPriority(self, bonus):
        return self.__bonusLayoutConfig.getPriority(bonus)

    def isBonusVisible(self, bonus):
        return self.__bonusLayoutConfig.getIsVisible(bonus)

    def isRandomPrb(self):
        return self.__switchHelper.isRandomPrbActive()

    def selectRandomBattle(self, callback):
        self.__switchHelper.selectRandomBattle(callback)

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def __createConfig(self):
        return BundlesConfig(self.__lobbyContext.getServerSettings().getSettings().get(OPEN_BUNDLE_GAME_PARAMS_KEY, {}))

    def __onClientUpdated(self, diff, _):
        if OPEN_BUNDLE_PDATA_KEY not in diff:
            return
        self.__syncData.update(diff)

    @serverSettingsChangeListener(OPEN_BUNDLE_GAME_PARAMS_KEY)
    def __onServerSettingsChanged(self, _):
        if self.__settingsConfig is not None:
            self.__settingsConfig = self.__createConfig()
        self.onSettingsChanged()
        self.__startNotifiers()
        return

    def __stop(self):
        self._unsubscribe()
        self.__switchHelper.stop()
        self.__settingsConfig = None
        return

    def __clear(self):
        self.__syncData.clear()

    def __startNotifiers(self):
        self.__statusChangeNotifiers = [ SimpleNotifier(partial(self.__getTimeToStatusChange, bundleID), partial(self.onStatusChanged, bundleID)) for bundleID in self.bundleIDs ]
        for notifier in self.__statusChangeNotifiers:
            notifier.startNotification()

    def __getTimeToStatusChange(self, bundleID):
        if self.isEnabled(bundleID):
            bundleConfig = self.getBundle(bundleID)
            currentTime = getServerUTCTime()
            if bundleConfig.start > currentTime:
                return bundleConfig.start - currentTime
            if bundleConfig.start < currentTime < bundleConfig.finish - ONE_DAY:
                return bundleConfig.finish - ONE_DAY - currentTime
            if bundleConfig.finish - ONE_DAY < currentTime < bundleConfig.finish:
                return bundleConfig.finish - currentTime
