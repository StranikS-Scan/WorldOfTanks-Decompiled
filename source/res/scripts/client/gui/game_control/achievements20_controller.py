# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/achievements20_controller.py
import logging
import Event
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ACHIEVEMENTS_INFO, ACHIEVEMENTS_WTR_RANKS, ACHIEVEMENTS_WTR_INFO, ACHIEVEMENTS_WTR_PREV_POINTS, ACHIEVEMENTS_WTR_PREV_RANK, ACHIEVEMENTS_WTR_PREV_SUB_RANK, ACHIEVEMENTS_RATING_CALCULATED_STATUS, ACHIEVEMENTS_MEDAL_ADDED_STATUS, ACHIEVEMENTS_EDITING_ENABLED_STATUS, ACHIEVEMENTS_RATING_CHANGED_STATUS, ACHIEVEMENTS_FIRST_ENTRY_STATUS, ACHIEVEMENTS_MEDAL_COUNT_INFO, PREV_ACHIEVEMENTS_NAME_LIST, ACHIEVEMENTS_WTR_PREV_POINTS_NOTIFICATION, ACHIEVEMENTS_INITIAL_BATTLE_COUNT, ACHIEVEMENTS_MAX_WTR_POINTS
from achievements20.WTRStageChecker import WTRStageChecker
from bootcamp.Bootcamp import g_bootcamp
from constants import Configs
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.achievements.achievements_constants import Achievements20SystemMessages
from gui.impl.lobby.achievements.notifications_utils import NotificationsRuleProcessor, FLAG_STATUS
from gui.impl.lobby.achievements.profile_utils import isWTREnabled, getStagesOfWTR, getNormalizedValue
from helpers import dependency, server_settings
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IAchievements20Controller, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)

class Achievements20Controller(IAchievements20Controller):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(Achievements20Controller, self).__init__()
        self.__eventManager = Event.EventManager()
        self.onUpdate = Event.Event(self.__eventManager)
        self.onRankIncrease = Event.Event(self.__eventManager)
        self.onRankDecrease = Event.Event(self.__eventManager)
        self.__accSettings = Achievements20SettingsManager()
        self.__notificationsProcessor = NotificationsRuleProcessor(self)
        self.__newSessionStarted = False

    def fini(self):
        self.__eventManager.clear()
        self.__stop()
        if self.__accSettings is not None:
            self.__accSettings.stop()
            self.__accSettings = None
        if self.__notificationsProcessor is not None:
            self.__notificationsProcessor.fini()
            self.__notificationsProcessor = None
        return

    def onLobbyStarted(self, ctx):
        if g_bootcamp.isRunning():
            return
        self.__accSettings.start()
        if not self.__newSessionStarted and self.getFirstEntryStatus() != FLAG_STATUS.VISITED:
            self.setFirstEntryStatus(FLAG_STATUS.UNSET)
        self.__notificationsProcessor.start()
        if self.getInitialBattleCount() < 0:
            stats = self.__itemsCache.items.getAccountDossier().getRandomStats()
            self.setInitialBattleCount(stats.getBattlesCount())
        self.__newSessionStarted = True
        self.__update()

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_playerEvents.onBattleResultsReceived += self.__onUpdate
        g_playerEvents.onDossiersResync += self.__onUpdate
        g_playerEvents.onClientUpdated += self.__onUpdate
        g_clientUpdateManager.addCallbacks({'stats.credits': self.__onUpdate,
         'stats.gold': self.__onUpdate,
         'goodies': self.__onUpdate})

    def onAccountBecomeNonPlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__newSessionStarted = False
        self.__stop()

    def showNewSummaryEnabled(self):
        data = {}
        if isWTREnabled():
            data['type'] = Achievements20SystemMessages.FIRST_ENTRY
        else:
            data['type'] = Achievements20SystemMessages.FIRST_ENTRY_WITHOUT_WTR
        self.__pushAchievements20SystemMessage(data)

    def showRatingUpgrade(self):
        checker = WTRStageChecker(getStagesOfWTR())
        rating = getNormalizedValue(self.__itemsCache.items.sessionStats.getAccountWtr())
        rank, subRank, _ = checker.getStage(rating)
        self.__pushAchievements20SystemMessage({'type': Achievements20SystemMessages.RATING_UPGRADE,
         'rank': rank,
         'subRank': subRank})

    def showRatingChanged(self):
        self.__pushAchievements20SystemMessage({'type': Achievements20SystemMessages.RATING_DOWNGRADE})

    def showRankedComplete(self):
        checker = WTRStageChecker(getStagesOfWTR())
        rating = getNormalizedValue(self.__itemsCache.items.sessionStats.getAccountWtr())
        rank, subRank, _ = checker.getStage(rating)
        self.__pushAchievements20SystemMessage({'type': Achievements20SystemMessages.RATING_COMPLETE,
         'rank': rank,
         'subRank': subRank})

    def showEditAvailable(self):
        self.__pushAchievements20SystemMessage({'type': Achievements20SystemMessages.EDITING_AVAILABLE})

    def getAchievementsTabCounter(self):
        return int(self.getFirstEntryStatus() == FLAG_STATUS.SET or self.getAchievementEditingEnabledStatus() == FLAG_STATUS.SET or self.getMedalAddedStatus() == FLAG_STATUS.SET or self.getRatingCalculatedStatus() == FLAG_STATUS.SET or self.getRatingChangedStatus() == FLAG_STATUS.SET)

    def getFirstEntryStatus(self):
        return self.__accSettings.getFirstEntryStatus()

    def setFirstEntryStatus(self, value):
        self.__accSettings.setFirstEntryStatus(value)

    def getPrevAchievementsList(self):
        return self.__accSettings.getPrevAchievementsList()

    def setPrevAchievementsList(self, value):
        self.__accSettings.setPrevAchievementsList(value)

    def getInitialBattleCount(self):
        return self.__accSettings.getInitialBattleCount()

    def setInitialBattleCount(self, value):
        self.__accSettings.setInitialBattleCount(value)

    def getMaxWtrPoints(self):
        return self.__accSettings.getMaxWtrPoints()

    def setMaxWtrPoints(self, points):
        self.__accSettings.setMaxWtrPoints(points)

    def getWtrPrevPointsNotification(self):
        return self.__accSettings.getWtrPrevPointsNotification()

    def setWtrPrevPointsNotification(self, points):
        self.__accSettings.setWtrPrevPointsNotification(points)

    def getWtrPrevPoints(self):
        return self.__accSettings.getWtrPrevPoints()

    def setWtrPrevPoints(self, points):
        self.__accSettings.setWtrPrevPoints(points)

    def getWtrPrevRank(self):
        return self.__accSettings.getWtrPrevRank()

    def setWtrPrevRank(self, rank):
        self.__accSettings.setWtrPrevRank(rank)

    def getWtrPrevSubRank(self):
        return self.__accSettings.getWtrPrevSubRank()

    def setWtrPrevSubRank(self, subRank):
        self.__accSettings.setWtrPrevSubRank(subRank)

    def getRatingCalculatedStatus(self):
        return self.__accSettings.getRatingCalculatedStatus()

    def setRatingCalculatedStatus(self, value):
        self.__accSettings.setRatingCalculatedStatus(value)
        self.onUpdate()

    def getMedalAddedStatus(self):
        return self.__accSettings.getMedalAddedStatus()

    def setMedalAddedStatus(self, value):
        self.__accSettings.setMedalAddedStatus(value)
        self.onUpdate()

    def getRatingChangedStatus(self):
        return self.__accSettings.getRatingChangedStatus()

    def setRatingChangedStatus(self, value):
        self.__accSettings.setRatingChangedStatus(value)
        self.onUpdate()

    def getAchievementEditingEnabledStatus(self):
        return self.__accSettings.getAchievementEditingEnabledStatus()

    def setAchievementEditingEnabledStatus(self, value):
        self.__accSettings.setAchievementEditingEnabledStatus(value)
        self.onUpdate()

    def getMedalCountInfo(self):
        return self.__accSettings.getMedalCountInfo()

    def setMedalCountInfo(self, value):
        self.__accSettings.setMedalCountInfo(value)

    def onSummaryPageVisited(self):
        if self.getFirstEntryStatus() == FLAG_STATUS.SET:
            self.setFirstEntryStatus(FLAG_STATUS.VISITED)
        if self.getAchievementEditingEnabledStatus() == FLAG_STATUS.SET:
            self.setAchievementEditingEnabledStatus(FLAG_STATUS.VISITED)
        if self.getRatingCalculatedStatus() == FLAG_STATUS.SET:
            self.setRatingCalculatedStatus(FLAG_STATUS.VISITED)
        if self.getRatingChangedStatus() == FLAG_STATUS.SET:
            self.setRatingChangedStatus(FLAG_STATUS.UNSET)
        if self.getMedalAddedStatus() == FLAG_STATUS.SET:
            self.setMedalAddedStatus(FLAG_STATUS.UNSET)
        self.onUpdate()

    def __stop(self):
        self.__removeListeners()
        if self.__accSettings is not None:
            self.__accSettings.stop()
        if self.__notificationsProcessor is not None:
            self.__notificationsProcessor.stop()
        return

    def __removeListeners(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated -= self.__onUpdate
        g_playerEvents.onDossiersResync -= self.__onUpdate
        g_playerEvents.onBattleResultsReceived -= self.__onUpdate
        g_clientUpdateManager.removeObjectCallbacks(self)

    @server_settings.serverSettingsChangeListener(Configs.ACHIEVEMENTS20_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__update()

    def __onUpdate(self, *args):
        self.__update()

    def __update(self):
        self.__notificationsProcessor.process()

    def __pushAchievements20SystemMessage(self, data):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(data, SCH_CLIENT_MSG_TYPE.ACHIEVEMENTS20_SM_TYPE)


class Achievements20SettingsManager(object):
    __slots__ = ('__settings',)
    __bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        self.__settings = dict()

    def start(self):
        self.__settings = AccountSettings.getSettings(ACHIEVEMENTS_INFO)

    def stop(self):
        if self.__settings:
            if not self.__bootcampController.isInBootcamp():
                AccountSettings.setSettings(ACHIEVEMENTS_INFO, self.__settings)
            self.__settings.clear()

    def getFirstEntryStatus(self):
        return self.__settings.get(ACHIEVEMENTS_FIRST_ENTRY_STATUS, 0)

    def setFirstEntryStatus(self, value):
        self.__settings[ACHIEVEMENTS_FIRST_ENTRY_STATUS] = value

    def getWtrRanks(self):
        return self.__settings[ACHIEVEMENTS_WTR_RANKS]

    def updateWtrRanks(self, rank):
        self.__settings.update(rank)

    def getPrevAchievementsList(self):
        return self.__settings.get(PREV_ACHIEVEMENTS_NAME_LIST, [])

    def setPrevAchievementsList(self, value):
        self.__settings[PREV_ACHIEVEMENTS_NAME_LIST] = value

    def getInitialBattleCount(self):
        return self.__settings.get(ACHIEVEMENTS_INITIAL_BATTLE_COUNT, -1)

    def setInitialBattleCount(self, value):
        self.__settings[ACHIEVEMENTS_INITIAL_BATTLE_COUNT] = value

    def getMaxWtrPoints(self):
        return self.__settings.get(ACHIEVEMENTS_MAX_WTR_POINTS, 0)

    def setMaxWtrPoints(self, points):
        self.__settings[ACHIEVEMENTS_MAX_WTR_POINTS] = points

    def getWtrPrevPointsNotification(self):
        return self.__settings.get(ACHIEVEMENTS_WTR_PREV_POINTS_NOTIFICATION, 0)

    def setWtrPrevPointsNotification(self, points):
        self.__settings[ACHIEVEMENTS_WTR_PREV_POINTS_NOTIFICATION] = points

    def getWtrPrevPoints(self):
        return self.__settings.setdefault(ACHIEVEMENTS_WTR_INFO, {}).get(ACHIEVEMENTS_WTR_PREV_POINTS, 0)

    def setWtrPrevPoints(self, points):
        self.__settings[ACHIEVEMENTS_WTR_INFO].update({ACHIEVEMENTS_WTR_PREV_POINTS: points})

    def getWtrPrevRank(self):
        return self.__settings.setdefault(ACHIEVEMENTS_WTR_INFO, {}).get(ACHIEVEMENTS_WTR_PREV_RANK, 0)

    def setWtrPrevRank(self, points):
        self.__settings[ACHIEVEMENTS_WTR_INFO].update({ACHIEVEMENTS_WTR_PREV_RANK: points})

    def getWtrPrevSubRank(self):
        return self.__settings.setdefault(ACHIEVEMENTS_WTR_INFO, {}).get(ACHIEVEMENTS_WTR_PREV_SUB_RANK, 0)

    def setWtrPrevSubRank(self, points):
        self.__settings[ACHIEVEMENTS_WTR_INFO].update({ACHIEVEMENTS_WTR_PREV_SUB_RANK: points})

    def getRatingCalculatedStatus(self):
        return self.__settings.get(ACHIEVEMENTS_RATING_CALCULATED_STATUS, 0)

    def setRatingCalculatedStatus(self, value):
        self.__settings[ACHIEVEMENTS_RATING_CALCULATED_STATUS] = value

    def getAchievementEditingEnabledStatus(self):
        return self.__settings.get(ACHIEVEMENTS_EDITING_ENABLED_STATUS, 0)

    def setAchievementEditingEnabledStatus(self, value):
        self.__settings[ACHIEVEMENTS_EDITING_ENABLED_STATUS] = value

    def getMedalAddedStatus(self):
        return self.__settings.get(ACHIEVEMENTS_MEDAL_ADDED_STATUS, 0)

    def setMedalAddedStatus(self, value):
        self.__settings[ACHIEVEMENTS_MEDAL_ADDED_STATUS] = value

    def getRatingChangedStatus(self):
        return self.__settings.get(ACHIEVEMENTS_RATING_CHANGED_STATUS, 0)

    def setRatingChangedStatus(self, value):
        self.__settings[ACHIEVEMENTS_RATING_CHANGED_STATUS] = value

    def getMedalCountInfo(self):
        return self.__settings.get(ACHIEVEMENTS_MEDAL_COUNT_INFO, 0)

    def setMedalCountInfo(self, value):
        self.__settings[ACHIEVEMENTS_MEDAL_COUNT_INFO] = value
