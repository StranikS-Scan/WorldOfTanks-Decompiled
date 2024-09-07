# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/early_access_controller.py
import typing
import CGF
from operator import attrgetter
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EarlyAccess
from cgf_components.hangar_camera_manager import HangarCameraManager
from constants import Configs, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL, QUEUE_TYPE
from early_access_common import makeEarlyAccessToken, getGroupName, getQuestFinisherName, EARLY_ACCESS_POSTPR_KEY, EARLY_ACCESS_PREFIX
from Event import Event, EventManager
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.lobby.early_access.hangar_feature_state import EarlyAccessHangarFeatureState
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.event_items import Group
from gui.server_events.conditions import EarlyAccessVehicleDescr
from gui.shared.money import Money, Currency
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils, server_settings
from helpers.server_settings import EarlyAccessConfig
from shared_utils import findFirst
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from gui.shared.money import CURRENCY_TYPE
    from season_common import GameSeasonCycle

class EarlyAccessController(IEarlyAccessController, SeasonProvider, IGlobalListener):
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __connectionMgr = dependency.descriptor(IConnectionManager)
    _VEHICLE_LVL_INDEX = 2
    _VEHICLE_CLASS_INDEX = 3
    _POST_PROGRESSION_QUEUES = (QUEUE_TYPE.RANDOMS, QUEUE_TYPE.COMP7)
    _EXCLUDE_FILTER_QUEUES = (QUEUE_TYPE.COMP7,)

    def __init__(self):
        self.__eventManager = EventManager()
        self.onQuestsUpdated = Event(self.__eventManager)
        self.onBalanceUpdated = Event(self.__eventManager)
        self.onUpdated = Event(self.__eventManager)
        self.onPayed = Event(self.__eventManager)
        self.onStartEvent = Event(self.__eventManager)
        self.onFinishEvent = Event(self.__eventManager)
        self.onStartAnnouncement = Event(self.__eventManager)
        self.onFinishAnnouncement = Event(self.__eventManager)
        self.onFeatureStateChanged = Event(self.__eventManager)
        self.__sysMessagesController = _EarlyAccessSystemMessagesController()
        self.sysMessageController.init()
        self.__hangarFeatureState = EarlyAccessHangarFeatureState()
        self.__firstVehicleCD = None
        self.__currProgressVehicleCD = None
        self.__currentEndSeasonDate = None
        self.__postProgressionVehicles = None
        return

    @property
    def sysMessageController(self):
        return self.__sysMessagesController

    @property
    def hangarFeatureState(self):
        return self.__hangarFeatureState

    @property
    @dependency.replace_none_kwargs(hangarSpace=IHangarSpace)
    def cgfCameraManager(self, hangarSpace=None):
        return CGF.getManager(hangarSpace.space.getSpaceID(), HangarCameraManager) if hangarSpace is not None and hangarSpace.space is not None else None

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.sysMessageController.startNotify()
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate,
         'quests': self.__onQuestsUpdated})
        if self.getCurrentSeason():
            self.sysMessageController.checkSeasonChanged()
            self.sysMessageController.checkNotify()
            self.__currentEndSeasonDate = self.getCurrentSeason().getEndDate()

    def onAccountBecomeNonPlayer(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.sysMessageController.stopNotify()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def fini(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.sysMessageController.fini()
        self.__sysMessagesController = None
        self.__hangarFeatureState = None
        return

    @staticmethod
    def isProgressionQuest(questID):
        return questID.startswith(getGroupName(''))

    @staticmethod
    def isPostProgressionQuest(questID):
        return questID.startswith(getGroupName(EARLY_ACCESS_POSTPR_KEY))

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().earlyAccessConfig

    def isEnabled(self):
        return self.getModeSettings().isEnabled and self.getCurrentSeasonID() != 0

    def isPaused(self):
        return self.getModeSettings().isPaused

    def getInfoPageLink(self):
        return self.getModeSettings().infoPageLink

    def getAffectedVehicles(self):
        return self.getModeSettings().getAffectedVehicles(self.getCurrentSeasonID())

    def getBlockedVehicles(self):
        return self.getModeSettings().getBlockedVehicles(self.getCurrentSeasonID())

    def getVehiclePrice(self, intCD):
        return self.getAffectedVehicles().get(intCD, 0)

    def getTokensBalance(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getEAToken())

    def getTokenCost(self):
        cost = self.getModeSettings().getTokenCost(self.getCurrentSeasonID())[Currency.GOLD]
        return Money.makeFrom(Currency.GOLD, cost)

    def getTokenCompensation(self, currency):
        cost = self.getModeSettings().getTokenCompensation(self.getCurrentSeasonID())[currency]
        return Money.makeFrom(currency, cost)

    def getReceivedTokensCount(self):
        getItemByCD = self.__itemsCache.items.getItemByCD
        return sum((self.getVehiclePrice(vehCD) for vehCD in self.getAffectedVehicles() if getItemByCD(vehCD).isUnlocked)) + self.getTokensBalance()

    def getTotalVehiclesPrice(self):
        return sum((self.getVehiclePrice(vehicleDescr) for vehicleDescr in self.getAffectedVehicles()))

    def getTokensForQuest(self, questID):
        quest = self.__eventsCache.getQuestByID(questID)
        if not quest:
            return 0
        tokens = quest.getBonuses('tokens')
        tokenStr = self.getEAToken()
        return sum((token.getCount() for token in tokens if tokenStr in token.getValue()))

    def getFirstVehicleCD(self):
        if self.__firstVehicleCD is None:
            self.__firstVehicleCD = self.__findVehicleWithMinLevel()
        return self.__firstVehicleCD

    def getCurrProgressVehicleCD(self):
        getItemByCD = self.__itemsCache.items.getItemByCD
        vehicles = sorted(set(self.getAffectedVehicles().keys()) - self.getBlockedVehicles(), key=lambda cd: getItemByCD(cd).level)
        return findFirst(lambda cd: not getItemByCD(cd).isUnlocked, vehicles, vehicles[-1])

    def getNationID(self):
        vehicleCDs = self.getAffectedVehicles()
        if not vehicleCDs:
            return -1
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCDs.keys()[0])
        return vehicle.nationID

    def getEAToken(self):
        seasonID = self.getCurrentSeasonID()
        return '' if seasonID == 0 else makeEarlyAccessToken(seasonID)

    def iterProgressionQuests(self):
        currentSeason = self.getCurrentSeason()
        cycles = sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID'))
        for cycle in cycles[:-1]:
            for quest in self.iterCycleProgressionQuests(str(cycle.ID)):
                yield (str(cycle.ID), quest)

    def iterCycleProgressionQuests(self, groupName):
        for questID in self.__eventsCache.getGroups().get(getGroupName(groupName), Group(0, {})).getGroupEvents():
            quest = self.__eventsCache.getQuestByID(questID)
            yield quest

    def iterAllCycles(self, now=None):
        currentSeason = self.getCurrentSeason(now)
        cycles = sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')) if currentSeason else []
        for cycle in cycles[:-1]:
            yield (str(cycle.ID), cycle)

    def isPostprogressionBlockedByQuestFinisher(self):
        quest = self.__eventsCache.getQuestByID(getQuestFinisherName(self.getCurrentSeasonID()))
        quesPostprtIter = self.iterCycleProgressionQuests(EARLY_ACCESS_POSTPR_KEY)
        questPostpr = next(quesPostprtIter, None)
        if not quest or not questPostpr:
            return False
        else:
            for item in questPostpr.accountReqs.getConditions().findAll('quest'):
                if item.getID() == getQuestFinisherName(self.getCurrentSeasonID()):
                    return item.isQuestCompleted()

            return False

    def isQuestActive(self):
        return self.isEnabled() and not self.isPaused()

    def getState(self):
        if self.__isCompletedState():
            return State.COMPLETED
        nowTime = time_utils.getServerUTCTime()
        _, endProgressionTime = self.getProgressionTimes()
        if nowTime < endProgressionTime:
            return State.ACTIVE
        return State.POSTPROGRESSION if self.__isAnyPostprogressionVehicleUnlocked() and not self.isPostprogressionBlockedByQuestFinisher() else State.BUY

    def getProgressionTimes(self):
        startProgressionTime = None
        finishProgressionTime = 0
        for _, data in self.iterAllCycles():
            if startProgressionTime is None or startProgressionTime > data.startDate:
                startProgressionTime = data.startDate
            if data.endDate > finishProgressionTime:
                finishProgressionTime = data.endDate

        return (startProgressionTime, finishProgressionTime)

    def getCycleProgressionTimes(self, cycleID=None):
        currSeason = self.getCurrentSeason()
        if cycleID is None:
            currCycle = currSeason.getLastActiveCycleInfo(time_utils.getServerUTCTime())
            if currCycle is not None:
                return (currCycle.startDate, currCycle.endDate)
        currCycle = currSeason.getCycleInfo(int(cycleID))
        return (currCycle.startDate, currCycle.endDate) if currCycle is not None else (0, 0)

    def getPostProgressionVehiclesForQuest(self, questID):
        if not self.isEnabled():
            return set()
        quest = self.__eventsCache.getQuestByID(questID)
        if not quest:
            return set()
        conditions = quest.vehicleReqs.getConditions().find('vehicleDescr')
        if not conditions:
            return self.__itemsCache.items.inventory.getIventoryVehiclesCDs()
        eaVehicleDescr = EarlyAccessVehicleDescr(conditions.getData())
        vehicleTypes = set((vehicleIntCD for vehicleIntCD in eaVehicleDescr.getVehiclesList()))
        return vehicleTypes

    def getPostProgressionVehicles(self):
        if self.__postProgressionVehicles is None:
            self.__updatePostProgressionVehicles()
        return self.__postProgressionVehicles

    def __updatePostProgressionVehicles(self):
        self.__postProgressionVehicles = set()
        for quest in self.iterCycleProgressionQuests(EARLY_ACCESS_POSTPR_KEY):
            self.__postProgressionVehicles.update(self.getPostProgressionVehiclesForQuest(quest.getID()))

    def getRequiredVehicleTypeAndLevelsForQuest(self, questID):
        vehicleType = ''
        vehicleLevels = set()
        if questID is None:
            vehicles = self.getPostProgressionVehicles()
            vehicleLevels = {self.getVehicleTypeAndLevelsByVehicleCD(vehicle)[1] for vehicle in vehicles}
            lastPostrpVehicle = self.__findPostrpVehicleWithMaxLevel()
            vehicleType = self.getVehicleTypeAndLevelsByVehicleCD(lastPostrpVehicle)[0] if lastPostrpVehicle else ''
        else:
            quest = self.__eventsCache.getQuestByID(questID)
            if quest is not None:
                conditions = quest.vehicleReqs.getConditions().find('vehicleDescr')
                if conditions:
                    vehicleClasses = conditions.parseFilters()[self._VEHICLE_CLASS_INDEX]
                    vehicleLevels = conditions.parseFilters()[self._VEHICLE_LVL_INDEX]
                    vehicleType = vehicleClasses[0] if vehicleClasses else ''
        minLvl = min(vehicleLevels) if vehicleLevels else MIN_VEHICLE_LEVEL
        maxLvl = max(vehicleLevels) if vehicleLevels else MAX_VEHICLE_LEVEL
        return (vehicleType, minLvl, maxLvl)

    def getSeasonInterval(self):
        season = self.getCurrentSeason()
        return (season.getStartDate(), season.getEndDate()) if season else (None, None)

    def getCurrentSeasonID(self):
        currentSeason = self.getCurrentSeason()
        return currentSeason.getSeasonID() if currentSeason else 0

    def isSeasonChanged(self):
        return AccountSettings.getEarlyAccess(EarlyAccess.EARLY_ACCESS_CURRENT_SEASON) != self.getCurrentSeasonID()

    def setEarlyAccessSetting(self, key):
        if self.getCurrentSeason() and self.isSeasonChanged():
            AccountSettings.clearEarlyAccess()
            AccountSettings.setEarlyAccess(EarlyAccess.EARLY_ACCESS_CURRENT_SEASON, self.getCurrentSeasonID())
        if not AccountSettings.getEarlyAccess(key):
            AccountSettings.setEarlyAccess(key, True)

    def getReceivedTokensForQuests(self):
        return sum((self.getTokensForQuest(quest.getID()) for _, quest in self.iterProgressionQuests() if quest and quest.isCompleted()))

    def isGroupQuestsCompleted(self, groupName):
        questIDs = self.__eventsCache.getGroups().get(getGroupName(groupName), Group(0, {})).getGroupEvents()
        if not questIDs:
            return True
        lastQuest = self.__eventsCache.getQuestByID(questIDs[-1])
        return lastQuest.isCompleted() if lastQuest else True

    def hasPostprogressionVehicle(self):
        return any((self.__itemsCache.items.getItemByCD(vehicleCD).isInInventory for vehicleCD in self.getPostProgressionVehicles()))

    def isPostProgressionQueueSelected(self):
        return any((self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) for queueType in self._POST_PROGRESSION_QUEUES)) if self.prbDispatcher is not None else False

    def isFilterDisabledInQueue(self):
        return any((self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) for queueType in self._EXCLUDE_FILTER_QUEUES)) if self.prbDispatcher is not None else False

    def getVehicleTypeAndLevelsByVehicleCD(self, vehCD):
        vehItem = self.__itemsCache.items.getItemByCD(vehCD)
        return (vehItem.type, vehItem.level) if vehItem is not None else ('', MIN_VEHICLE_LEVEL)

    @server_settings.serverSettingsChangeListener(Configs.EARLY_ACCESS_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        self.__firstVehicleCD = self.__findVehicleWithMinLevel()
        self.sysMessageController.checkSeasonChanged()
        self.sysMessageController.checkNotify()
        self.sysMessageController.startNotify()
        self.checkFeatureStateChanged()
        self.onUpdated()

    def __onTokensUpdate(self, diff):
        if self.getEAToken() in diff:
            self.onBalanceUpdated()

    def __onQuestsUpdated(self, diff):
        if any((questId.startswith(EARLY_ACCESS_PREFIX) for questId in set(diff))):
            self.__updatePostProgressionVehicles()
            self.onQuestsUpdated()

    def __isCompletedState(self):
        if not self.isGroupQuestsCompleted(EARLY_ACCESS_POSTPR_KEY):
            return False
        for cycleID, _ in self.iterAllCycles():
            if not self.isGroupQuestsCompleted(cycleID):
                return False

        return True

    def __findVehicleWithMinLevel(self):
        affectedVehicles = self.getAffectedVehicles()
        return min(affectedVehicles.keys(), key=lambda cd: self.__itemsCache.items.getItemByCD(cd).level) if affectedVehicles else None

    def __findPostrpVehicleWithMaxLevel(self):
        postprVehicles = self.getPostProgressionVehicles()
        return max(postprVehicles, key=lambda cd: self.__itemsCache.items.getItemByCD(cd).level) if postprVehicles else None

    def __isAnyPostprogressionVehicleUnlocked(self):
        vehicles = self.getPostProgressionVehicles()
        return any((self.__itemsCache.items.getItemByCD(vehicleCD).isUnlocked for vehicleCD in vehicles))

    def checkFeatureStateChanged(self):
        if self.isEnabled():
            isPausedPrevState = AccountSettings.getEarlyAccess(EarlyAccess.EVENT_PAUSED)
            isPaused = self.isPaused()
            if isPausedPrevState != isPaused:
                newEndDate = self.getCurrentSeason().getEndDate()
                if self.__currentEndSeasonDate is not None and newEndDate > self.__currentEndSeasonDate:
                    self.onFeatureStateChanged(isPaused, newEndDate)
                else:
                    self.onFeatureStateChanged(isPaused)
                self.__currentEndSeasonDate = newEndDate
                AccountSettings.setEarlyAccess(EarlyAccess.EVENT_PAUSED, isPaused)
        return


class _EarlyAccessSystemMessagesController(object):
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    __HOURS_COUNTDOWN = time_utils.ONE_DAY

    def __init__(self):
        self.__notificationManager = Notifiable()
        self.__nextCycleStartNotifier = SimpleNotifier(self.__getStartCycleTimer, self.__onNotifyCycleStart)
        self.__nextCycleFinishNotifier = SimpleNotifier(self.__getFinishCycleTimer, self.__onNotifyCyclesFinish)
        self.__nextSeasonStartNotifier = SimpleNotifier(self.__getStartSeasonTimer, self.__onNotifySeasonStart)

    def init(self):
        self.__notificationManager.addNotificator(self.__nextCycleStartNotifier)
        self.__notificationManager.addNotificator(self.__nextCycleFinishNotifier)
        self.__notificationManager.addNotificator(self.__nextSeasonStartNotifier)

    def startNotify(self):
        self.__notificationManager.startNotification()

    def stopNotify(self):
        self.__notificationManager.stopNotification()

    def fini(self):
        self.__notificationManager.clearNotification()

    def checkNotify(self):
        if self.__earlyAccessController.isPaused():
            return
        self.checkStartEvent()
        self.checkFinishEvent()
        self.checkStartCycles()
        self.checkFinishCycles()

    def checkStartEvent(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            ctrl.onStartEvent()

    def checkFinishEvent(self):
        ctrl = self.__earlyAccessController
        prevSeasonID = AccountSettings.getEarlyAccess(EarlyAccess.EARLY_ACCESS_CURRENT_SEASON)
        if not ctrl.isEnabled() and prevSeasonID is not None:
            ctrl.onFinishEvent()
        return

    def checkStartCycles(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            nowTime = time_utils.getServerUTCTime()
            _, finishProgressionTime = ctrl.getProgressionTimes()
            lastAnnounceChapter = None
            for cycleID, cycle in ctrl.iterAllCycles():
                if cycle.startDate < nowTime < finishProgressionTime:
                    lastAnnounceChapter = (cycleID, cycle.ordinalNumber)

            if lastAnnounceChapter is not None:
                ctrl.onStartAnnouncement(lastAnnounceChapter[0], lastAnnounceChapter[1])
            if ctrl.hasPostprogressionVehicle():
                ctrl.onStartAnnouncement(EARLY_ACCESS_POSTPR_KEY)
        return

    def checkFinishCycles(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            nowTime = time_utils.getServerUTCTime()
            _, finishProgressionTime = ctrl.getProgressionTimes()
            _, finishSeasonTime = ctrl.getSeasonInterval()
            if finishProgressionTime - self.__HOURS_COUNTDOWN < nowTime < finishProgressionTime:
                ctrl.onFinishAnnouncement(finishProgressionTime, isProgression=True)
            if finishSeasonTime - self.__HOURS_COUNTDOWN < nowTime < finishSeasonTime:
                ctrl.onFinishAnnouncement(finishSeasonTime, isProgression=False)

    def checkSeasonChanged(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            seasonID = ctrl.getCurrentSeason().getSeasonID()
            if AccountSettings.getEarlyAccess(EarlyAccess.EARLY_ACCESS_CURRENT_SEASON) != seasonID:
                AccountSettings.clearEarlyAccess()
                AccountSettings.setEarlyAccess(EarlyAccess.EARLY_ACCESS_CURRENT_SEASON, seasonID)

    def __getStartCycleTimer(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            nowTime = time_utils.getServerUTCTime()
            currentSeason = ctrl.getCurrentSeason()
            if currentSeason:
                cycleData = currentSeason.getNextByTimeCycle(nowTime)
                if cycleData is not None:
                    if cycleData.startDate > nowTime:
                        return cycleData.startDate - nowTime + 1
        return 0

    def __getFinishCycleTimer(self):
        ctrl = self.__earlyAccessController
        if ctrl.isEnabled():
            nowTime = time_utils.getServerUTCTime()
            _, finishProgressionTime = ctrl.getProgressionTimes()
            _, finishSeasonTime = ctrl.getSeasonInterval()
            showMessageTime = finishProgressionTime - self.__HOURS_COUNTDOWN if nowTime < finishProgressionTime - self.__HOURS_COUNTDOWN else finishSeasonTime - self.__HOURS_COUNTDOWN
            if showMessageTime > nowTime:
                return showMessageTime - nowTime + 1
            seasonEndTime = finishSeasonTime - nowTime
            if seasonEndTime > 0:
                return seasonEndTime

    def __getStartSeasonTimer(self):
        ctrl = self.__earlyAccessController
        nowTime = time_utils.getServerUTCTime()
        settings = ctrl.getModeSettings()
        for _, season in settings.seasons.iteritems():
            startSeason = season['startSeason'] if season else 0
            if nowTime < startSeason:
                return startSeason - nowTime + 1

    def __onNotifyCycleStart(self):
        self.checkStartCycles()
        self.__earlyAccessController.onUpdated()
        self.startNotify()

    def __onNotifyCyclesFinish(self):
        self.checkFinishCycles()
        self.checkFinishEvent()
        self.__earlyAccessController.onUpdated()
        self.startNotify()

    def __onNotifySeasonStart(self):
        self.checkSeasonChanged()
        self.checkNotify()
        self.__earlyAccessController.onUpdated()
        self.startNotify()
