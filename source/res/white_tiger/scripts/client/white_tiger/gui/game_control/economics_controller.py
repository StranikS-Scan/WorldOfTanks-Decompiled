# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/game_control/economics_controller.py
import math
import Event
from collections import namedtuple
from gui.game_control.season_provider import SeasonProvider
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, server_settings
from shared_utils import makeTupleByDict
from white_tiger.skeletons.economics_controller import IEconomicsController
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from white_tiger_common.wt_constants import WHITE_TIGER_GAME_PARAMS_KEY
from gui.ClientUpdateManager import g_clientUpdateManager
from white_tiger.gui.wt_bonus_packers import mergeWtProgressionBonuses
from skeletons.gui.server_events import IEventsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from white_tiger_common.wt_constants import WT_VEHICLE_TAGS
from shared_utils import first
from white_tiger.gui.white_tiger_account_settings import AccountSettingsKeys, setSettings, setWTFavorites
from white_tiger_common.wt_constants import WT_EVENT_TICKET_KEY, WT_FIRST_TIME_EVENT_ENTER_TANK, WT_EVENT_GOLDEN_TICKET_KEY
from gui.shared.items_cache import CACHE_SYNC_REASON

class _EconomicsConfig(namedtuple('_ProgressionConfig', ('ticketToken', 'quickBossTicketToken', 'quickHunterTicketToken', 'ticketsToDraw', 'progression', 'stampsPerProgressionStage', 'stamp', 'mainRewardTypeFilter'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(ticketToken='', quickBossTicketToken='', quickHunterTicketToken='', ticketsToDraw=0, progression=[], stampsPerProgressionStage=0, stamp='', mainRewardTypeFilter='')
        defaults.update(kwargs)
        return super(_EconomicsConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


class EconomicsController(IEconomicsController, IGlobalListener, SeasonProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(EconomicsController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onProgressUpdated = Event.Event(self.__eventManager)
        self.onProgressSeenByUser = Event.Event(self.__eventManager)
        self.onRewardsUpdated = Event.Event(self.__eventManager)
        self.__economicsSettings = None
        self.__prevTicketCount = 0
        self.__prevGoldenTicketObtained = 0
        return

    def onLobbyInited(self, ctx):
        super(EconomicsController, self).onLobbyInited(ctx)
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        if self.__prevTicketCount > 0 and self.getTicketCount() == 0:
            condition = lambda veh: veh.name == WT_FIRST_TIME_EVENT_ENTER_TANK
            vehicleID = self.__selectFirstVehicleByTag([WT_VEHICLE_TAGS.HUNTER], condition)
            self.__setFavoriteVehicleAndSelect(vehicleID)
        self.__prevTicketCount = self.getTicketCount()
        self.__prevGoldenTicketObtained = self.getGoldenTicketObtained()

    def fini(self):
        self._unsubscribe()
        super(EconomicsController, self).fini()

    def onDisconnected(self):
        super(EconomicsController, self).onDisconnected()
        self._unsubscribe()

    def onAvatarBecomePlayer(self):
        super(EconomicsController, self).onAvatarBecomePlayer()
        self._unsubscribe()

    def _unsubscribe(self):
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().getSettings().get(WHITE_TIGER_GAME_PARAMS_KEY, {})

    def getEconomicsSettings(self):
        if not self.__economicsSettings:
            config = self.getConfig()
            if config:
                self.__economicsSettings = makeTupleByDict(_EconomicsConfig, config)
        return self.__economicsSettings or _EconomicsConfig.defaults()

    def getTicketCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getTicketTokenName())

    def getGoldenTicketObtained(self):
        return bool(self.__itemsCache.items.tokens.getTokenCount(WT_EVENT_GOLDEN_TICKET_KEY))

    def getQuickTicketCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getQuickTicketTokenName())

    def getQuickBossTicketExpiryTime(self):
        return self.__itemsCache.items.tokens.getTokenExpiryTime(self.getQuickTicketTokenName())

    def getQuickHunterTicketCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getQuickHunterTicketTokenName())

    def getQuickHunterTicketExpiryTime(self):
        return self.__itemsCache.items.tokens.getTokenExpiryTime(self.getQuickHunterTicketTokenName())

    def getTicketTokenName(self):
        return self.getEconomicsSettings().ticketToken

    def getStampTokenName(self):
        return self.getEconomicsSettings().stamp

    def getQuickTicketTokenName(self):
        return self.getEconomicsSettings().quickBossTicketToken

    def getQuickHunterTicketTokenName(self):
        return self.getEconomicsSettings().quickHunterTicketToken

    def getStampsCountPerLevel(self):
        return self.getEconomicsSettings().stampsPerProgressionStage

    def getProgressionMaxLevel(self):
        return len(self.getEconomicsSettings().progression)

    def getLastProgressionStepID(self):
        progression = self.getEconomicsSettings().progression
        return self.getEconomicsSettings().progression[-1]['quest'] if progression else ''

    def getStampsCount(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getStampTokenName())

    def getMaxRequiredStampsCount(self):
        return self.getStampsCountPerLevel() * self.getProgressionMaxLevel()

    def getFinishedLevelsCount(self):
        stampsCount = self.getStampsCount()
        stampsPerLevel = self.getStampsCountPerLevel()
        totalLevels = self.getProgressionMaxLevel()
        return min(int(math.floor(stampsCount / stampsPerLevel)), totalLevels)

    def getCurrentLevel(self):
        finishedLevelsCount = self.getFinishedLevelsCount()
        totalLevels = self.getProgressionMaxLevel()
        return min(finishedLevelsCount + 1, totalLevels)

    def getProgressionRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        bonuses = quests[questID].getBonuses()
        return mergeWtProgressionBonuses(bonuses)

    def getProgressionPrioritisedRewards(self, questID):
        mainRewards = {}
        additionalRewards = {}
        bonuses = self.getProgressionRewards(questID)
        for bonus in bonuses:
            if bonus.getName() in self.getEconomicsSettings().mainRewardTypeFilter:
                mainRewards[bonus.getName()] = bonus.getValue()
            additionalRewards[bonus.getName()] = bonus.getValue()

        return (mainRewards, additionalRewards)

    def hasEnoughTickets(self):
        return self.getTicketCount() + self.getQuickTicketCount() > 0

    def notifyProgressSeen(self):
        currentStamps = self.getStampsCount()
        currentLevel = self.getCurrentLevel()
        setSettings(AccountSettingsKeys.WT_LAST_SEEN_STAMPS, currentStamps)
        setSettings(AccountSettingsKeys.WT_LAST_SEEN_LEVEL, currentLevel)
        self.onProgressSeenByUser(currentStamps, currentLevel)

    def __onTokensUpdate(self, diff):
        if self.getStampTokenName() in diff:
            self.onProgressUpdated()
        if WT_EVENT_TICKET_KEY in diff and self.__prevTicketCount == 0:
            currentTickets = self.getTicketCount()
            if currentTickets > 0:
                condition = lambda veh: WT_VEHICLE_TAGS.BOSS in veh.tags
                vehicleID = self.__selectFirstVehicleByTag([WT_VEHICLE_TAGS.BOSS], condition)
                self.__setFavoriteVehicleAndSelect(vehicleID)
            self.__prevTicketCount = currentTickets

    def __selectFirstVehicleByTag(self, tags, condition):
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.HAS_TAGS(tags)
        wtVehicles = dict([ (vehicle.invID, vehicle) for vehicle in self.__itemsCache.items.getVehicles(criteria=criteria).values() ])
        vehicleID = first([ veh.invID for veh in wtVehicles.values() if condition(veh) ])
        return vehicleID

    def __onSyncCompleted(self, reason, diff):
        if reason != CACHE_SYNC_REASON.CLIENT_UPDATE:
            return
        goldenTicketObtained = self.getGoldenTicketObtained()
        if goldenTicketObtained and not self.__prevGoldenTicketObtained:
            condition = lambda veh: WT_VEHICLE_TAGS.PRIORITY_BOSS in veh.tags
            vehicleID = self.__selectFirstVehicleByTag([WT_VEHICLE_TAGS.PRIORITY_BOSS], condition)
            if vehicleID:
                self.__prevGoldenTicketObtained = goldenTicketObtained
                self.__setFavoriteVehicleAndSelect(vehicleID)

    def __setFavoriteVehicleAndSelect(self, vehicleID):
        setWTFavorites(vehicleID)
        wtCtrl = dependency.instance(IWhiteTigerController)
        wtCtrl.selectVehicle(vehicleID)

    @server_settings.serverSettingsChangeListener(WHITE_TIGER_GAME_PARAMS_KEY)
    def __onServerSettingsChanged(self, diff):
        self.__economicsSettings = None
        return
