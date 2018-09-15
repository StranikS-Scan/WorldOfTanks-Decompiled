# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/quests_controller.py
import weakref
from constants import EVENT_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from items import getTypeOfCompactDescr
from skeletons.gui.game_control import IQuestsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_MAX_LVL_FOR_TUTORIAL = 3

class _QuestCache(object):
    __slots__ = ('__invVehicles', '__cache', '__eventsCache')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, eventsCache):
        self.__eventsCache = weakref.proxy(eventsCache)
        self.__invVehicles = []
        self.__cache = {}

    def isNewbiePlayer(self):

        def _compareLvL(vehicle):
            return vehicle.level > _MAX_LVL_FOR_TUTORIAL

        vehicles = self.getInventoryVehicles()
        return not any(filter(_compareLvL, vehicles))

    def getInventoryVehicles(self):
        if not self.__invVehicles:
            self.__setInvVehicles()
        return self.__invVehicles

    def getAllAvailableQuests(self):
        return self.__eventsCache.getQuests(self.__filterFunc).values()

    def isAnyQuestAvailable(self):
        vehicles = self.getInventoryVehicles()
        for vehicle in vehicles:
            if self.getQuestForVehicle(vehicle):
                return True

        return False

    def getFirstAvailableQuest(self):
        for quests in self.__cache.itervalues():
            if quests:
                return quests

        vehicles = self.getInventoryVehicles()
        for vehicle in vehicles:
            if self.getQuestForVehicle(vehicle):
                return self.__cache[vehicle.intCD]

        return []

    def getQuestForVehicle(self, vehicle):
        if not vehicle:
            return []
        vehIntCD = vehicle.intCD
        if vehIntCD not in self.__cache:
            self.__update(vehicle=vehicle)
        return self.__cache.get(vehIntCD, [])

    def invalidate(self):
        self.clear()

    def clear(self):
        if self.__cache:
            self.__cache.clear()
            self.__cache = {}
        if self.__invVehicles:
            self.__invVehicles = []

    def __update(self, vehicle=None):
        quests = self.__eventsCache.getQuests(self.__filterFunc)
        for quest in quests.itervalues():
            suitableVehicles = quest.getSuitableVehicles()
            if vehicle and vehicle not in suitableVehicles:
                continue
            for veh in suitableVehicles:
                vehIntCD = veh.intCD
                if vehIntCD not in self.__cache:
                    self.__cache[vehIntCD] = {quest}
                self.__cache[vehIntCD].add(quest)

    def __setInvVehicles(self):
        requestCriteria = REQ_CRITERIA.INVENTORY
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.DISABLED_IN_PREM_IGR
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        requestCriteria |= ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        self.__invVehicles = self.itemsCache.items.getVehicles(requestCriteria).values() or []

    @classmethod
    def __filterFunc(cls, event):
        if event.getType() in (EVENT_TYPE.TOKEN_QUEST, EVENT_TYPE.REF_SYSTEM_QUEST):
            return False
        if not event.getFinishTimeLeft():
            return False
        return not event.isCompleted() and event.isAvailable()[0] if event.getType() == EVENT_TYPE.MOTIVE_QUEST else True


class QuestsController(IQuestsController):
    """Handle mapping between vehicle->available quests
    """
    __slots__ = ('__quests', 'eventsCache')
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(QuestsController, self).__init__()
        self.__quests = None
        return

    def fini(self):
        self.__stop()
        self.__clearCache()

    def onLobbyStarted(self, ctx):
        if not self.__quests:
            self.__quests = _QuestCache(self.eventsCache)
        else:
            self.__quests.invalidate()
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__invalidateEventsData,
         'stats.unlocks': self.__onStatsUnlocked})
        self.eventsCache.onSyncCompleted += self.__invalidateEventsData
        self.eventsCache.onProgressUpdated += self.__invalidateEventsData

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()
        self.__clearCache()

    def isNewbiePlayer(self):
        return self.__quests.isNewbiePlayer()

    def getInventoryVehicles(self):
        return self.__quests.getInventoryVehicles()

    def getAllAvailableQuests(self):
        return self.__quests.getAllAvailableQuests()

    def isAnyQuestAvailable(self):
        return self.__quests.isAnyQuestAvailable()

    def getFirstAvailableQuest(self):
        return self.__quests.getFirstAvailableQuest()

    def getQuestForVehicle(self, vehicle):
        return self.__quests.getQuestForVehicle(vehicle)

    def getQuestGroups(self):
        return self._getGroups()

    def __invalidateEventsData(self, *args):
        self.__quests.invalidate()

    def __onStatsUnlocked(self, ids):
        for intCD in ids:
            if getTypeOfCompactDescr(intCD) == GUI_ITEM_TYPE.VEHICLE:
                return self.__invalidateEventsData()

    def __stop(self):
        self.eventsCache.onSyncCompleted -= self.__invalidateEventsData
        self.eventsCache.onProgressUpdated -= self.__invalidateEventsData
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearCache(self):
        if self.__quests:
            self.__quests.clear()
            self.__quests = None
        return

    @classmethod
    def _getEvents(cls):
        return cls.eventsCache.getEvents()

    @classmethod
    def _getGroups(cls):
        return cls.eventsCache.getGroups()
