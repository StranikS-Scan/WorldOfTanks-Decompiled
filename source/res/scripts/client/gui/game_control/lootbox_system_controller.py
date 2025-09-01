# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/lootbox_system_controller.py
import logging
from copy import deepcopy
from functools import partial
from typing import TYPE_CHECKING
import Event
from account_helpers.AccountSettings import AccountSettings, LOOTBOX_SYSTEM, LOOT_BOXES_HAS_NEW, LOOT_BOXES_INTRO_VIDEO_SHOWN, LOOT_BOXES_OPEN_ANIMATION_ENABLED, LOOT_BOXES_SELECTED_BOX, LOOT_BOXES_UNIQUE_ID, LOOT_BOXES_WAS_FINISHED, LOOT_BOXES_WAS_STARTED
from adisp import adisp_process
from constants import LOOTBOX_TOKEN_PREFIX
from gui import SystemMessages
from gui.lootbox_system.base.awards_manager import AwardsManager
from gui.lootbox_system.base.config_parsing import parseAllOfSection
from gui.lootbox_system.base.utils import getLootboxStatisticsKey
from gui.lootbox_system.base.views_loaders import registerViewsLoaders, unregisterViewsLoaders
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.processors.loot_boxes import ResetLootBoxSystemStatisticsProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.server_settings import LOOTBOX_SYSTEM_CONFIG, LootBoxSystemEventConfig
from helpers.time_utils import getServerUTCTime
from shared_utils import findFirst
from skeletons.gui.game_control import ILootBoxSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Any, Dict
    from gui.shared.gui_items.loot_box import LootBox
_logger = logging.getLogger(__name__)

class _SettingsMgr(object):
    __DEFAULTS = {LOOT_BOXES_WAS_STARTED: False,
     LOOT_BOXES_WAS_FINISHED: False,
     LOOT_BOXES_INTRO_VIDEO_SHOWN: False,
     LOOT_BOXES_HAS_NEW: False,
     LOOT_BOXES_OPEN_ANIMATION_ENABLED: True,
     LOOT_BOXES_SELECTED_BOX: None}
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def get(self, eventName, setting):
        lootBoxSystemSettings = AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}
        return lootBoxSystemSettings.get(eventName, {}).get(setting, self.__DEFAULTS.get(setting))

    def set(self, eventName, setting, newValue):
        if setting == LOOT_BOXES_UNIQUE_ID:
            raise SoftException('You cannot change the "LOOT_BOXES_UNIQUE_ID" manually')
        settings = AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}
        settings.setdefault(eventName, {})
        oldValue = settings[eventName].get(setting, self.__DEFAULTS.get(setting))
        if oldValue != newValue:
            settings[eventName][setting] = newValue
            AccountSettings.setSettings(LOOTBOX_SYSTEM, settings)

    def update(self):
        settings = AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}
        for eventName in self.__lootBoxes.eventNames:
            settings.setdefault(eventName, {})
            oldUniqueID = settings[eventName].get(LOOT_BOXES_UNIQUE_ID)
            newUniqueID = self.__generateUniqueID(eventName)
            if oldUniqueID != newUniqueID:
                defaults = {LOOT_BOXES_UNIQUE_ID: newUniqueID}
                defaults.update(self.__DEFAULTS)
                settings[eventName] = defaults
                AccountSettings.setSettings(LOOTBOX_SYSTEM, settings)

    def __generateUniqueID(self, eventName):
        return hash('_'.join((eventName, '_'.join((str(lbID) for lbID in self.__lootBoxes.getBoxesIDs(eventName))))))


class LootBoxSystemController(ILootBoxSystemController, EventsHandler):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(LootBoxSystemController, self).__init__()
        self.__em = Event.EventManager()
        self.__settings = _SettingsMgr()
        self.__isInited = False
        self.__boxesCount = {}
        self.__boxesInfo = {}
        self.__statusChangeNotifiers = []
        self.onBoxesAvailabilityChanged = Event.Event(self.__em)
        self.onStatusChanged = Event.Event(self.__em)
        self.onBoxesCountChanged = Event.Event(self.__em)
        self.onBoxesUpdated = Event.Event(self.__em)
        self.onBoxesInfoUpdated = Event.Event(self.__em)

    @property
    def eventNames(self):
        return self.__getConfig().events.keys()

    @property
    def mainEntryPoint(self):
        return self.__getConfig().mainEntryPoint

    @property
    def isLootBoxesAvailable(self):
        return self.__lobbyContext.getServerSettings().isLootBoxesEnabled()

    def isAvailable(self, eventName):
        return self.isLootBoxesAvailable and self.isActive(eventName)

    def isActive(self, eventName):
        if self.isEnabled(eventName):
            startTime, endTime = self.__getEventConfig(eventName).getActiveTime()
            return startTime <= getServerUTCTime() < endTime
        return False

    def isEnabled(self, eventName):
        return self.__getEventConfig(eventName).enabled

    def getActiveEvents(self):
        return [ eventName for eventName in self.eventNames if self.isActive(eventName) ]

    def getBoxesPriority(self, eventName):
        return {category:index for index, category in enumerate(self.__getEventConfig(eventName).boxesPriority)}

    def useStats(self, eventName):
        return all((box.getUseStats() for box in self.getActiveBoxes(eventName)))

    def getStatistics(self, eventName, boxID=None):
        rewardsData, boxesCount = {}, 0
        statsKey = getLootboxStatisticsKey(eventName, boxID)
        if statsKey is None:
            return (rewardsData, boxesCount)
        else:
            rewardsData, boxesCount, _ = self.__itemsCache.items.tokens.getLootBoxesStats().get(statsKey, (rewardsData, boxesCount, 0))
            return (rewardsData, boxesCount)

    @adisp_process
    def resetStatistics(self, boxesIDs):
        result = yield ResetLootBoxSystemStatisticsProcessor(boxesIDs).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType, priority=NotificationPriorityLevel.MEDIUM)
        g_eventBus.handleEvent(events.LootBoxSystemEvent(events.LootBoxSystemEvent.ON_STATISTICS_RESET, {'isCompleted': result.success and not bool(result.userMsg)}), EVENT_BUS_SCOPE.LOBBY)

    def getSetting(self, eventName, setting):
        return self.__settings.get(eventName, setting)

    def setSetting(self, eventName, setting, value):
        self.__settings.set(eventName, setting, value)

    def onLobbyInited(self, event):
        self.__start()
        self.__isInited = True

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__isInited = False
        AwardsManager.finalize()
        for event in self.eventNames:
            self.setSetting(event, LOOT_BOXES_SELECTED_BOX, None)

        self.__stop()
        self.__boxesInfo.clear()
        self.__boxesCount.clear()
        return

    def fini(self):
        self.__isInited = False
        self.__stop()
        self.__boxesInfo.clear()
        self.__boxesCount.clear()

    def getActiveTime(self, eventName):
        return self.__getEventConfig(eventName).getActiveTime()

    def getBoxesCountToGuaranteed(self, category):
        lootBox = findFirst(lambda b: b.getCategory() == category, self.__itemsCache.items.tokens.getLootBoxes().itervalues())
        return self.getBoxInfo(lootBox.getID())['boxCountToGuaranteedBonus']

    def getBoxesCount(self, eventName, category=None):
        return sum(self.__boxesCount.get(eventName, {}).itervalues()) if category is None else self.__boxesCount.get(eventName, {}).get(category, 0)

    def getBoxesIDs(self, boxType):
        return {lootBox.getID() for lootBox in self.getBoxes(boxType, lambda b: b.getType() == boxType)}

    def getActiveBoxes(self, eventName, criteria=None):

        def isCompatible(box):
            return box.getType() == eventName and box.isEnabled()

        return list(self.getBoxes(eventName, isCompatible) if not callable(criteria) else self.getBoxes(eventName, lambda b: isCompatible(b) and criteria(b)))

    def getBoxes(self, eventName, criteria=None):
        iterBoxes = self.__itemsCache.items.tokens.getLootBoxes().itervalues() if not callable(criteria) else (box for box in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if criteria(box))
        priority = self.getBoxesPriority(eventName)
        return sorted(iterBoxes, key=lambda c: priority.get(c.getCategory(), len(priority)))

    def getBoxInfo(self, boxID):
        return self.__boxesInfo.get(boxID, {})

    def getBoxInfoByCategory(self, boxCategory):
        return findFirst(lambda i: i.get('category') == boxCategory, self.__boxesInfo.itervalues())

    def getBoxesInfo(self):
        return deepcopy(self.__boxesInfo)

    def _getCallbacks(self):
        return (('tokens', self.__onTokensUpdated), ('lootBoxes', self.__onBoxesUpdate))

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),)

    def __getConfig(self):
        return self.__lobbyContext.getServerSettings().getLootBoxSystemConfig()

    def __getEventConfig(self, eventName):
        return self.__getConfig().events.get(eventName, LootBoxSystemEventConfig())

    def __getTooltipConfig(self):
        return self.__lobbyContext.getServerSettings().getLootBoxesTooltipConfig()

    def __start(self):
        AwardsManager.init()
        self.__settings.update()
        self.__startNotifiers()
        registerViewsLoaders()
        self.__updateBoxesCount()
        self.__updateBoxesInfo()
        if not self.__isInited:
            self.onBoxesInfoUpdated()
        self._subscribe()

    def __stop(self):
        for statusChangeNotifier in self.__statusChangeNotifiers:
            statusChangeNotifier.stopNotification()

        del self.__statusChangeNotifiers[:]
        unregisterViewsLoaders()
        self._unsubscribe()

    def __onServerSettingsChanged(self, settings):
        if 'isLootBoxesEnabled' in settings:
            self.onBoxesAvailabilityChanged()
        if any((name in settings for name in (LOOTBOX_SYSTEM_CONFIG, 'lootBoxes_config', 'lootboxes_tooltip_config'))):
            self.__settings.update()
            self.__updateBoxesCount()
            self.__updateBoxesInfo()
            self.onStatusChanged()
            self.__startNotifiers()

    def __onNotifyStatusChange(self):
        self.onStatusChanged()

    def __getTimeToStatusChange(self, eventName):
        if self.isEnabled(eventName):
            startTime, finishTime = self.getActiveTime(eventName)
            currentTime = getServerUTCTime()
            if startTime > currentTime:
                return startTime - currentTime
            if currentTime < finishTime:
                return finishTime - currentTime

    def __updateBoxesCount(self):
        self.__boxesCount = self.__getBoxesCount()

    def __getBoxesCount(self):
        result = {}
        for box in self.__itemsCache.items.tokens.getLootBoxes().itervalues():
            boxType = box.getType()
            if box.isEnabled() and boxType in self.eventNames:
                result.setdefault(boxType, {})
                boxCategory = box.getCategory()
                result[boxType].setdefault(boxCategory, 0)
                result[boxType][boxCategory] += box.getInventoryCount()

        return result

    def __onTokensUpdated(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            newBoxesCount = self.__getBoxesCount()
            for boxType, boxTypeInfo in self.__boxesCount.iteritems():
                for boxCategory, oldCount in boxTypeInfo.iteritems():
                    newCount = newBoxesCount.get(boxType, {}).get(boxCategory, 0)
                    if newCount != oldCount:
                        self.__boxesCount.update(newBoxesCount)
                        if newCount > oldCount:
                            self.setSetting(boxType, LOOT_BOXES_HAS_NEW, True)
                        self.onBoxesCountChanged()
                        break

    def __onBoxesUpdate(self, diff):
        for boxID, _ in diff.get('history', {}).iteritems():
            if boxID in self.__boxesInfo:
                guaranteedBonusLimit = self.__boxesInfo[boxID].get('limit', 0)
                lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
                opened = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
                self.__boxesInfo[boxID]['boxCountToGuaranteedBonus'] = max(guaranteedBonusLimit - opened, 0)

        self.onBoxesUpdated()

    def __updateBoxesInfo(self):
        boxes = self.__itemsCache.items.tokens.getLootBoxes().values()
        boxesInfoData = {}
        if boxes:
            self.__updateBoxes(boxes, boxesInfoData, self.__getTooltipConfig())
        self.__boxesInfo = boxesInfoData

    def __updateBoxes(self, boxes, boxesInfoData, config=None):
        for lootBox in boxes:
            boxID = lootBox.getID()
            bonusesData = config.get(boxID, {}) if config and boxID in config else lootBox.getBonusInfo()
            boxData = self.__fillBoxData(lootBox, bonusesData)
            boxesInfoData[boxID] = boxData

    def __fillBoxData(self, lootBox, bonusesData):
        boxData = {}
        limit = lootBox.getGuaranteedFrequency()
        opened = self.__itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootBox)
        boxData['category'] = lootBox.getCategory()
        boxData['limit'] = limit
        boxData['slots'] = parseAllOfSection(bonusesData.get('allof', {}))
        boxData['boxCountToGuaranteedBonus'] = max(limit - opened, 0) if opened is not None else limit
        return boxData

    def __startNotifiers(self):
        self.__statusChangeNotifiers = [ SimpleNotifier(partial(self.__getTimeToStatusChange, eventName), self.__onNotifyStatusChange) for eventName in self.eventNames ]
        for notifier in self.__statusChangeNotifiers:
            notifier.startNotification()
