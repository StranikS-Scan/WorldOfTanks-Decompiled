# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_lootbox_controller.py
import logging
import Event
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.game_control import IEventLootBoxesController
from helpers import dependency
from gui.ClientUpdateManager import g_clientUpdateManager
_logger = logging.getLogger(__name__)

class EventLootBoxController(IEventLootBoxesController):
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(EventLootBoxController, self).__init__()
        self.onUpdated = Event.Event()
        self.__enabled = False
        self.__lastViewed = None
        return

    def init(self):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})

    def fini(self):
        self.onUpdated.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def onAvatarBecomePlayer(self):
        self.__lastViewed = None
        return

    def onDisconnected(self):
        self.__lastViewed = None
        return

    def onAccountBecomeNonPlayer(self):
        self.__lastViewed = None
        return

    def __onTokensUpdate(self, *args):
        lootBoxCount = self.getEventLootBoxesCount()
        if self.__lastViewed is not None and lootBoxCount < self.__lastViewed:
            self.__lastViewed = lootBoxCount
        self.onUpdated()
        return

    def isEnabled(self):
        return self.__enabled

    def isDisabled(self):
        return False

    def getOwnedLootBoxByType(self, lootBoxType=None):
        if lootBoxType is None:
            return
        else:
            boxes = self.getAllAvailableEventLootBoxes()
            for box in boxes:
                if box is not None and box.getType() == lootBoxType:
                    return box

            return

    def getLootBoxByID(self, lootBoxId=None, ignoreCount=False):
        if lootBoxId is None:
            return
        else:
            box = self._itemsCache.items.tokens.getLootBoxByTokenID(lootBoxId)
            return box if box is not None and (box.getInventoryCount() > 0 or ignoreCount) else None

    def getAllAvailableEventLootBoxes(self):
        result = []
        for _, box in self._itemsCache.items.tokens.getLootBoxes().iteritems():
            if box.isEvent() and box.getInventoryCount() > 0:
                result.append(box)

        return result

    def getAllEventLootBoxes(self):
        result = []
        for _, box in self._itemsCache.items.tokens.getLootBoxes().iteritems():
            if box.isEvent():
                result.append(box)

        return result

    def getEventLootBoxesCount(self):
        return sum((lootBox.getInventoryCount() for lootBox in self.getAllEventLootBoxes()))

    def getEventLootBoxesCountByType(self, boxType):
        return sum((lootBox.getInventoryCount() for lootBox in self.getAllEventLootBoxes() if lootBox.getType() == boxType))

    def getLootBoxTypeByID(self, lootBoxId=None):
        if lootBoxId is None:
            return
        else:
            box = self._itemsCache.items.tokens.getLootBoxByTokenID(lootBoxId)
            return box.getType() if box is not None else None

    def getLastViewed(self):
        return self.__getLastViewed()

    def setLastViewed(self):
        self.__lastViewed = self.getEventLootBoxesCount()
        self.saveLastViewed()

    def saveLastViewed(self):
        if self.__lastViewed is not None and self._settingsCore.isReady:
            self._settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, {'count': self.__lastViewed})
        return

    def __getLastViewed(self):
        if self.__lastViewed is None and self._settingsCore.isReady:
            self.__lastViewed = self._settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, 'count', 0)
            lootBoxCount = self.getEventLootBoxesCount()
            if self.__lastViewed > lootBoxCount:
                self.__lastViewed = lootBoxCount
                self.saveLastViewed()
        return self.__lastViewed
