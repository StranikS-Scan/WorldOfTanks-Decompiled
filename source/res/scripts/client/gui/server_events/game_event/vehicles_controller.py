# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/vehicles_controller.py
import logging
import Event
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.doc_loaders.hw19_vehicle_settings import EventVehicleSettings
from constants import EVENT
from gui.ClientUpdateManager import g_clientUpdateManager
_logger = logging.getLogger(__name__)
_UPDATE_INTERVAL = 1
_DEFAULT_DISCOUNT_COEF = 1.0
_ZERO_TIMER_ERROR_CODE = -1
_ZERO_TIMER_ERROR_STR = 'has_energy'

class VehiclesController(object):
    INVALID_TIME = -1
    eventsCache = dependency.descriptor(IEventsCache)
    itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(VehiclesController, self).__init__()
        self._eventsManager = Event.EventManager()
        self.onTimeToRepairChanged = Event.Event(self._eventsManager)
        self.onDailyRewardsUpdated = Event.Event(self._eventsManager)
        self.__dailyKeysRewards = {}
        self.__vehiclesTime = {}
        self.__eventVehicles = None
        self.__eventVehiclesWithoutEnergy = set()
        self.__vehicleSettings = None
        return

    @property
    def vehiclesTime(self):
        return self.__vehiclesTime

    def start(self):
        self.__eventVehicles = self.eventsCache.getGameEventData().get('vehicles', {})
        self.__vehicleSettings = EventVehicleSettings()
        self.__initDailyKeysRewards()
        self._gameEventController.onQuestsUpdated += self.__onQuestsUpdated

    def stop(self):
        self._eventsManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._gameEventController.onQuestsUpdated -= self.__onQuestsUpdated

    def __onQuestsUpdated(self):
        self.__initDailyKeysRewards()
        self.onDailyRewardsUpdated()

    def hasDailyQuest(self, vehIntCD):
        return self.eventsCache.questsProgress.getTokenCount(EVENT.HW21_DAILY_TOKEN.format(vehIntCD)) > 0

    def getDailyKeysReward(self, vehIntCD):
        return self.__dailyKeysRewards.get(str(vehIntCD), 0)

    def getSumOfAvailableDailyKeysReward(self):
        return sum((self.getDailyKeysReward(v) for v in self.__dailyKeysRewards if self.hasDailyQuest(v)), 0)

    def getVehiclesOrder(self):
        return [ veh['id'] for veh in sorted(self.__vehicleSettings.getVehiclesSettings().values(), key=lambda v: v['weight']) ]

    def getVehiclesForRent(self):
        eventsData = self.eventsCache.getGameEventData()
        return eventsData.get('vehiclesForRent', {})

    def getVehicleSettings(self):
        return self.__vehicleSettings

    def getAllVehiclesInInventory(self):
        vehiclesAvailble = [ self.itemsCache.items.getItemByCD(cd) for cd in self.getVehiclesOrder() ]
        return [ v.intCD for v in vehiclesAvailble if v.isInInventory ]

    def __initDailyKeysRewards(self):

        def sumKeysBonuses(quest):
            result = 0
            for t in quest.getBonuses('tokens'):
                result += sum((v.count for k, v in t.getTokens().iteritems() if k == EVENT.REWARD_BOX.KEY_TOKEN), 0)

            return result

        quests = self.eventsCache.getHiddenQuests(lambda q: q.getGroupID() == EVENT.REWARD_BOX.KEY_DAILY_QUESTS_GROUP)
        for questID, quest in quests.iteritems():
            _, vehCD = questID.split(':')
            self.__dailyKeysRewards[vehCD] = sumKeysBonuses(quest)
