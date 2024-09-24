# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/lootbox_system_controller.py
from copy import deepcopy
from typing import TYPE_CHECKING
import Event
from account_helpers.AccountSettings import AccountSettings, LOOTBOX_SYSTEM, LOOT_BOXES_HAS_NEW, LOOT_BOXES_UNIQUE_ID
from adisp import adisp_process
from constants import LOOTBOX_TOKEN_PREFIX
from gui import SystemMessages
from gui.entitlements.entitlement_common import LOOT_BOX_COUNTER_ENTITLEMENT
from gui.lootbox_system.awards_manager import AwardsManager
from gui.lootbox_system.config_parsing import parseAllOfSection
from gui.lootbox_system.utils import getLootboxStatisticsKey
from gui.lootbox_system.views_loaders import registerViewsLoaders, unregisterViewsLoaders
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.gui_items.processors.loot_boxes import ResetLootBoxSystemStatisticsProcessor
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from helpers.events_handler import EventsHandler
from helpers.server_settings import LOOTBOX_SYSTEM_CONFIG
from helpers.time_utils import getServerUTCTime
from shared_utils import findFirst
from skeletons.gui.game_control import IEntitlementsController, ILootBoxSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if TYPE_CHECKING:
    from typing import Any, Dict
    from gui.shared.gui_items.loot_box import LootBox

class _SettingsMgr(object):
    __lootBoxes = dependency.descriptor(ILootBoxSystemController)

    def getSetting(self, setting):
        return (AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}).get(setting)

    def setSetting(self, setting, newValue):
        if setting == LOOT_BOXES_UNIQUE_ID:
            raise SoftException('You cannot change the "LOOT_BOXES_UNIQUE_ID" manually')
        settings = AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}
        oldValue = settings.get(setting)
        if oldValue != newValue:
            settings[setting] = newValue
            AccountSettings.setSettings(LOOTBOX_SYSTEM, settings)

    def update(self):
        settings = AccountSettings.getSettings(LOOTBOX_SYSTEM) or {}
        oldUniqueID = settings.get(LOOT_BOXES_UNIQUE_ID)
        newUniqueID = self.__generateUniqueID(self.__lootBoxes.eventName)
        if oldUniqueID != newUniqueID:
            defaults = AccountSettings.getSettingsDefault(LOOTBOX_SYSTEM) or {}
            defaults[LOOT_BOXES_UNIQUE_ID] = newUniqueID
            AccountSettings.setSettings(LOOTBOX_SYSTEM, defaults)

    def __generateUniqueID(self, eventName):
        return hash('_'.join((eventName, '_'.join((str(lbID) for lbID in self.__lootBoxes.getBoxesIDs(eventName))))))


class LootBoxSystemController(ILootBoxSystemController, EventsHandler):
    __entitlements = dependency.descriptor(IEntitlementsController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(LootBoxSystemController, self).__init__()
        self.__em = Event.EventManager()
        self.__settings = _SettingsMgr()
        self.__boxesCount = {}
        self.__boxesInfo = {}
        self.__statusChangeNotifier = SimpleNotifier(self.__getTimeToStatusChange, self.__onNotifyStatusChange)
        self.onBoxesAvailabilityChanged = Event.Event(self.__em)
        self.onStatusChanged = Event.Event(self.__em)
        self.onBoxesCountChanged = Event.Event(self.__em)
        self.onBoxesInfoUpdated = Event.Event(self.__em)
        self.onBoxesUpdated = Event.Event(self.__em)

    @property
    def eventName(self):
        return self.__getConfig().eventName

    @property
    def isConsumesEntitlements(self):
        return self.isAvailable

    @property
    def isAvailable(self):
        return self.isLootBoxesAvailable and self.isActive

    @property
    def isActive(self):
        if self.isEnabled:
            startTime, endTime = self.__getConfig().getActiveTime()
            return startTime <= getServerUTCTime() < endTime
        return False

    @property
    def isEnabled(self):
        return self.__getConfig().isEnabled

    @property
    def boxesPriority(self):
        return {category:index for index, category in enumerate(self.__getConfig().boxesPriority)}

    @property
    def isLootBoxesAvailable(self):
        return self.__lobbyContext.getServerSettings().isLootBoxesEnabled()

    @property
    def useStats(self):
        return all((box.getUseStats() for box in self.getActiveBoxes()))

    def getStatistics(self, boxID=None):
        rewardsData, boxesCount = {}, 0
        statsKey = getLootboxStatisticsKey(boxID)
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

    def getSetting(self, setting):
        return self.__settings.getSetting(setting)

    def setSetting(self, setting, value):
        self.__settings.setSetting(setting, value)

    def onLobbyInited(self, event):
        self.__start()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        AwardsManager.finalize()
        self.__stop()

    def fini(self):
        self.__stop()

    def getActiveTime(self):
        return self.__getConfig().getActiveTime()

    def getBoxesCountToGuaranteed(self, category):
        lootBox = findFirst(lambda b: b.getCategory() == category, self.__itemsCache.items.tokens.getLootBoxes().itervalues())
        return self.getBoxInfo(lootBox.getID())['boxCountToGuaranteedBonus']

    def getBoxesCount(self, category=None):
        return sum(self.__boxesCount.itervalues()) if category is None else self.__boxesCount.get(category, 0)

    def getBoxesIDs(self, boxType):
        return {lootBox.getID() for lootBox in self.getBoxes(lambda b: b.getType() == boxType)}

    def getActiveBoxes(self, criteria=None):
        return list(self.getBoxes(lambda b: b.getType() == self.eventName) if not callable(criteria) else self.getBoxes(lambda b: b.getType() == self.eventName and criteria(b)))

    def getBoxes(self, criteria=None):
        iterBoxes = self.__itemsCache.items.tokens.getLootBoxes().itervalues() if not callable(criteria) else (box for box in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if criteria(box))
        priority = self.boxesPriority
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

    def __getTooltipConfig(self):
        return self.__lobbyContext.getServerSettings().getLootBoxesTooltipConfig()

    def __start(self):
        AwardsManager.init()
        self.__settings.update()
        self.__statusChangeNotifier.startNotification()
        registerViewsLoaders()
        self.__updateBoxesCount()
        self.__updateBoxesInfo()
        self._subscribe()

    def __stop(self):
        self.__statusChangeNotifier.stopNotification()
        unregisterViewsLoaders()
        self._unsubscribe()
        self.__boxesInfo.clear()

    def __onServerSettingsChanged(self, settings):
        if 'isLootBoxesEnabled' in settings:
            self.onBoxesAvailabilityChanged()
        if any((name in settings for name in (LOOTBOX_SYSTEM_CONFIG, 'lootBoxes_config', 'lootboxes_tooltip_config'))):
            self.__settings.update()
            self.onStatusChanged()
            self.__statusChangeNotifier.startNotification()
            self.__updateBoxesInfo()
            self.__updateBoxesCount()

    def __onNotifyStatusChange(self):
        self.onStatusChanged()
        if self.isLootBoxesAvailable and self.isActive:
            self.__entitlements.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])

    def __getTimeToStatusChange(self):
        if self.isEnabled:
            startTime, finishTime = self.getActiveTime()
            currentTime = getServerUTCTime()
            if startTime > currentTime:
                return startTime - currentTime
            if currentTime < finishTime:
                return finishTime - currentTime

    def __updateBoxesCount(self):
        self.__boxesCount = self.__getBoxesCount()

    def __getBoxesCount(self):
        return {box.getCategory():box.getInventoryCount() for box in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if box.getType() == self.eventName}

    def __onTokensUpdated(self, diff):
        if any((token.startswith(LOOTBOX_TOKEN_PREFIX) for token in diff.iterkeys())):
            newBoxesCount = self.__getBoxesCount()
            for boxCategory, oldCount in self.__boxesCount.iteritems():
                newCount = newBoxesCount.get(boxCategory, 0)
                if newCount != oldCount:
                    self.__entitlements.updateCache([LOOT_BOX_COUNTER_ENTITLEMENT])
                    self.__boxesCount.update(newBoxesCount)
                    if newCount > oldCount:
                        self.setSetting(LOOT_BOXES_HAS_NEW, True)
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
        boxes = [ lb for lb in self.__itemsCache.items.tokens.getLootBoxes().itervalues() if lb.getType() == self.eventName ]
        boxesInfoData = {}
        if boxes:
            self.__updateBoxes(boxes, boxesInfoData, self.__getTooltipConfig())
        self.__boxesInfo = boxesInfoData
        self.onBoxesInfoUpdated()

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
