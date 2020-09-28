# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/game_event_controller.py
import logging
import typing
from collections import defaultdict, namedtuple
from operator import itemgetter
import BigWorld
import Event
from adisp import process, async
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.lobby.wt_event import wt_event_sound
from gui.game_control.season_provider import SeasonProvider
from gui.periodic_battles.models import PrimeTime
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.event_dispatcher import showHangar, showWtEventCollectionWindow, showWTWelcomeScreen
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from items import makeIntCompactDescrByID as makeCD
from items.components.c11n_constants import CustomizationType
from items.components.crew_skins_constants import CrewSkinType
from items.vehicles import makeVehicleTypeCompDescrByName
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY
from shared_utils import collapseIntervals, makeTupleByDict, findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.server_events.bonuses import mergeBonuses, splitBonuses
from gui.wt_event.wt_event_notification_helpers import pushOpenedLootBoxNotification
from gui.shared.gui_items.processors.loot_boxes import LootBoxReRollRecordsProcessor
if typing.TYPE_CHECKING:
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)

class _GameEventConfig(namedtuple('_GameEventConfig', ('isEnabled', 'peripheryIDs', 'cycleTimes', 'seasons', 'primeTimes', 'eventBattles'))):
    __slots__ = ()

    def __new__(cls, **kwargs):
        defaults = dict(isEnabled=False, peripheryIDs={}, cycleTimes={}, seasons={}, primeTimes={}, eventBattles={})
        defaults.update(kwargs)
        return super(_GameEventConfig, cls).__new__(cls, **defaults)

    def asDict(self):
        return self._asdict()

    def replace(self, data):
        allowedFields = self._fields
        dataToUpdate = dict(((k, v) for k, v in data.iteritems() if k in allowedFields))
        return self._replace(**dataToUpdate)

    @classmethod
    def defaults(cls):
        return cls()


def _makeIntCDByBonusItem(bonusItem):
    if 'customizations' in bonusItem:
        itemValue = bonusItem['customizations'][0]
        custType = itemValue['custType']
        custTypeId = getattr(CustomizationType, str(custType).upper(), None)
        itemId = itemValue['id']
        if not custTypeId:
            return
        return makeCD('customizationItem', custTypeId, itemId)
    elif 'crewSkins' in bonusItem:
        itemValue = bonusItem['crewSkins'][0]
        skinID = itemValue['id']
        return makeCD('crewSkin', CrewSkinType.CREW_SKIN, skinID)
    else:
        return


class GameEventController(IGameEventController, IGlobalListener, SeasonProvider):
    _eventsCache = dependency.descriptor(IEventsCache)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _bootcampCtrl = dependency.descriptor(IBootcampController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _itemsCache = dependency.descriptor(IItemsCache)
    _lootBoxController = dependency.descriptor(IEventLootBoxesController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __appLoader = dependency.descriptor(IAppLoader)
    __guiLoader = dependency.descriptor(IGuiLoader)
    __WT_EVENT_STORAGE_NAME = 'wt'
    __WT_EVENT_TOKEN_STORAGE = 'bossTicketToken'
    __WT_EVENT_QUICK_TOKEN_STORAGE = 'bossQuickTicketToken'
    __WT_EVENT_TOKENS_DRAW_STORAGE = 'numberOfTokensToDraw'
    __WT_EVENT_QUEST_PREFIX_NAME = 'questPrefix'
    __WT_EVENT_HUNTER_COLLECTION_NAME = 'hunterCollection'
    __WT_EVENT_BOSS_COLLECTION_NAME = 'bossCollection'
    __WT_EVENT_PROGRESSION_CONFIG = 'itemsProgression'
    __WT_EVENT_HUNTER_PROGRESS_TOKEN_STORAGE = 'hunterProgressToken'
    __WT_EVENT_BOSS_PROGRESS_TOKEN_STORAGE = 'bossProgressToken'

    def __init__(self):
        super(GameEventController, self).__init__()
        self.onUpdated = Event.Event()
        self.onProgressUpdated = Event.Event()
        self.onEventPrbChanged = Event.Event()
        self.onEventUpdated = Event.Event()
        self._setSeasonSettingsProvider(self.__getGameEventConfig)
        self.wtHunterCD = makeVehicleTypeCompDescrByName('germany:G105_T-55_NVA_DDR_EL')
        self.wtBossCD = makeVehicleTypeCompDescrByName('germany:G98_Waffentrager_E100_TL')
        self.wtSpecialBossCD = makeVehicleTypeCompDescrByName('germany:G98_Waffentrager_E100_TL_S')
        self.__enterSound = wt_event_sound.WTEventHangarEnterSound()
        self.__lootBoxData = None
        self.__lootBoxReRollRecords = {}
        self.__notificator = Notifiable()
        self.__isEventEnabled = False
        self.__readyToGoPortal = {'camera': False,
         'boss': False,
         'hunter': False}
        self.__wtEventSelected = False
        self.eventHeroTankIsInFocus = False
        return

    def onLobbyInited(self, event):
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.updateLootBoxReRollRecords()
        self.__packLootBoxData(self._lobbyContext.getServerSettings().getLootBoxConfig())
        if self.__lootBoxData is None:
            _logger.error('[LootBox] Could not fetch lootBox bonus data for some reason')
        self.startGlobalListening()
        self.__enterSound.clear()
        self.__enterSound.update(self.isEventPrbActive())
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_VEHICLED_CLICKED, self.onHeroTankMouseClicked, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_PORTAL_CLICKED, self.onPortalClicked, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_SELECTED, self.wtEventSelected, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(CameraRelatedEvents.WT_EVENT_CAMERA_READY_TO_GO_PORTAL, self.__cameraReadyToGoPortal, EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.addListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_NON_EVENT_VEHICLE_CHOSEN, self.__onNonEventVehicleChosen, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_COLLECTION_VIEW_LOADED, self.__collectionViewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.WT_EVENT_HERO_TANK_LEAVE_WORLD, self.__onHeroTankLeaveWorld, EVENT_BUS_SCOPE.LOBBY)
        self._eventsCache.onSyncCompleted += self.__updateEvent
        self.__updateEvent()
        return

    def vehiclePreviewOpenRandom(self):
        if self.__wtEventSelected:
            self.__doSelectAction(PREBATTLE_ACTION_NAME.RANDOM)

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def init(self):
        super(GameEventController, self).init()
        self.__notificator.addNotificator(SimpleNotifier(self.getTimer, self.__updateEvent))
        self.__notificator.addNotificator(SimpleNotifier(self.__getTimeForTurnOffEntryPoint, self.onEventUpdated))

    def fini(self):
        self.onEventPrbChanged.clear()
        self.onUpdated.clear()
        self.onProgressUpdated.clear()
        self.onEventUpdated.clear()
        self.__stop()
        self.__notificator.clearNotification()
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_VEHICLED_CLICKED, self.onHeroTankMouseClicked, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_PORTAL_CLICKED, self.onPortalClicked, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, self.wtEventSelectedOff, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(CameraRelatedEvents.WT_EVENT_CAMERA_READY_TO_GO_PORTAL, self.__cameraReadyToGoPortal, EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.removeListener(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, self.__onHeroTankLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_NON_EVENT_VEHICLE_CHOSEN, self.__onNonEventVehicleChosen, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_COLLECTION_VIEW_LOADED, self.__collectionViewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.WT_EVENT_HERO_TANK_LEAVE_WORLD, self.__onHeroTankLeaveWorld, EVENT_BUS_SCOPE.LOBBY)
        self._eventsCache.onSyncCompleted -= self.__updateEvent
        super(GameEventController, self).fini()

    def wtEventSelected(self, _):
        self.__wtEventSelected = True
        wt_event_sound.playHangarCameraFly(forward=True)

    def wtEventSelectedOff(self, _):
        self.__wtEventSelected = False
        self.eventHeroTankIsInFocus = False
        wt_event_sound.playHangarCameraFly(forward=False)

    def onEventWelcomeCollectionScreensClosed(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_SELECTED, ctx={'data': {}}), EVENT_BUS_SCOPE.LOBBY)

    def onPrbEntitySwitched(self):
        if not self.isEnabled():
            return
        else:
            if self.isEventPrbActive():
                isCustomizationOpen = False
                app = self.__appLoader.getApp()
                view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
                if view is not None:
                    isCustomizationOpen = True
                    view.onCloseWindow(force=True)
                else:
                    view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_HANGAR))
                    if view is None:
                        showHangar()
                if not self.__isWelcomeScreenShown():
                    if self._settingsCore.isReady:
                        self._settingsCore.serverSettings.saveInEventStorage({'wtIntroShown': True})
                    else:
                        _logger.error('Can not apply WT intro settings. Settings are not ready')
                    showWTWelcomeScreen()
                elif not isCustomizationOpen:
                    _logger.debug('WT Event: welcome screen was already shown')
                    g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_SELECTED, ctx={'data': {}}), EVENT_BUS_SCOPE.LOBBY)
            else:
                g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_SELECTED_OFF, ctx={'data': {}}), EVENT_BUS_SCOPE.LOBBY)
            self.onEventPrbChanged(self.isEventPrbActive())
            self.__enterSound.update(self.isEventPrbActive())
            return

    def isEnabled(self):
        return self._eventsCache.isEventEnabled() and self.getCurrentSeason() is not None

    def isAvailable(self):
        return self.isInPrimeTime() and self.isActive()

    def runEventQueue(self):
        g_prbLoader.getDispatcher().doAction(PrbAction('', 0))

    def getLootBoxReRollRecords(self, lootBoxType=None):
        return self.__lootBoxReRollRecords.get(lootBoxType, 0) if lootBoxType is not None else self.__lootBoxReRollRecords

    @process
    def updateLootBoxReRollRecords(self):
        result = yield LootBoxReRollRecordsProcessor().request()
        if result and result.success:
            self.__lootBoxReRollRecords = result.auxData
            if any([ bool(value.get('count')) for value in self.__lootBoxReRollRecords.values() ]):
                if self.isActive() and self._lobbyContext.getServerSettings().isLootBoxesEnabled():
                    pushOpenedLootBoxNotification()

    def getHunter(self):
        return self._itemsCache.items.getItemByCD(self.wtHunterCD)

    def getHunterCD(self):
        return self.wtHunterCD

    def getBoss(self):
        return self._itemsCache.items.getItemByCD(self.wtBossCD)

    @process
    def runStandardHangarMode(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        return

    @process
    def selectBoss(self):
        isPrbActive = self.isEventPrbActive()
        if not isPrbActive:
            isPrbActive = yield self.__doSelectEventPrb()
        if isPrbActive:
            bossVehicle = self.getBoss()
            g_currentVehicle.selectVehicle(bossVehicle.invID)

    def getSpecialBoss(self):
        return self._itemsCache.items.getItemByCD(self.wtSpecialBossCD)

    def isSpecialBoss(self):
        return g_currentVehicle.item.intCD == self.getSpecialBoss().intCD

    def isActive(self):
        return self.isEnabled() and not self._bootcampCtrl.isInBootcamp() and self.hasWeekdays() and self.__getCurrentCycleInfo()[1]

    def isInPrimeTime(self):
        return self.getPrimeTimeStatus()[2]

    def isEventPrbActive(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInPreQueue(queueType=QUEUE_TYPE.EVENT_BATTLES) or state.isInUnit(PREBATTLE_TYPE.EVENT)
        else:
            return False

    def getEventFinishTime(self):
        pass

    def hasWeekdays(self):
        eventConfig = self.__getGameEventConfig()
        result = findFirst(lambda primeTime: bool(primeTime['weekdays']), eventConfig.primeTimes.values(), None)
        return result is not None

    def getPrimeTimes(self):
        eventConfig = self.__getGameEventConfig()
        primeTimes = eventConfig.primeTimes
        peripheryIDs = eventConfig.peripheryIDs
        primeTimesPeriods = defaultdict(lambda : defaultdict(list))
        for _, primeTime in primeTimes.items():
            period = (primeTime['start'], primeTime['end'])
            weekdays = primeTime['weekdays']
            for pID in primeTime['peripheryIDs']:
                if pID not in peripheryIDs:
                    continue
                periphery = primeTimesPeriods[pID]
                for wDay in weekdays:
                    periphery[wDay].append(period)

        return {pID:PrimeTime(pID, {wDay:collapseIntervals(periods) for wDay, periods in pPeriods.iteritems()}) for pID, pPeriods in primeTimesPeriods.iteritems()}

    def getPrimeTimeStatus(self, peripheryID=None):
        if peripheryID is None:
            peripheryID = self._connectionMgr.peripheryID
        primeTime = self.getPrimeTimes().get(peripheryID)
        if primeTime is None:
            return (PrimeTimeStatus.NOT_SET, 0, False)
        elif not primeTime.hasAnyPeriods():
            return (PrimeTimeStatus.FROZEN, 0, False)
        else:
            season = self.getCurrentSeason() or self.getNextSeason()
            currTime = time_utils.getCurrentLocalServerTimestamp()
            if season and season.hasActiveCycle(currTime) and primeTime.getPeriodsBetween(currTime, season.getCycleEndDate()):
                self.__isNow, timeTillUpdate = primeTime.getAvailability(currTime, season.getCycleEndDate())
            else:
                timeTillUpdate = 0
                if season:
                    nextCycle = season.getNextByTimeCycle(currTime)
                    if nextCycle:
                        primeTimeStart = primeTime.getNextPeriodStart(nextCycle.startDate, season.getEndDate(), includeBeginning=True)
                        if primeTimeStart:
                            timeTillUpdate = max(primeTimeStart, nextCycle.startDate) - currTime
                self.__isNow = False
            return (PrimeTimeStatus.AVAILABLE, timeTillUpdate, self.__isNow) if self.__isNow else (PrimeTimeStatus.NOT_AVAILABLE, timeTillUpdate, False)

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        primeTimes = self.getPrimeTimes()
        dayStart, dayEnd = time_utils.getDayTimeBoundsForLocal(selectedTime)
        dayEnd += 1
        serversPeriodsMapping = {}
        hostsList = self.__getHostList()
        for _, _, serverShortName, _, peripheryID in hostsList:
            if peripheryID not in primeTimes:
                continue
            dayPeriods = primeTimes[peripheryID].getPeriodsBetween(dayStart, dayEnd)
            if groupIdentical and dayPeriods in serversPeriodsMapping.values():
                for name, period in serversPeriodsMapping.iteritems():
                    serverInMapping = name if period == dayPeriods else None
                    if serverInMapping:
                        newName = '{0}, {1}'.format(serverInMapping, serverShortName)
                        serversPeriodsMapping[newName] = serversPeriodsMapping.pop(serverInMapping)
                        break

            serversPeriodsMapping[serverShortName] = dayPeriods

        return serversPeriodsMapping

    def getTimer(self):
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus()
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE and not self._connectionMgr.isStandalone():
            allPeripheryIDs = set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])
            for peripheryID in allPeripheryIDs:
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(peripheryID)
                if peripheryStatus == PrimeTimeStatus.NOT_AVAILABLE and peripheryTime < timeLeft:
                    timeLeft = peripheryTime

        seasonsChangeTime = self.getClosestStateChangeTime()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if seasonsChangeTime and (currTime + timeLeft > seasonsChangeTime or timeLeft == 0):
            timeLeft = seasonsChangeTime - currTime
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def hasAvailablePrimeTimeServers(self):
        return self.__hasPrimeTimeServers(statuses=(PrimeTimeStatus.AVAILABLE,))

    def hasConfiguredPrimeTimeServers(self):
        return self.__hasPrimeTimeServers(statuses=(PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE))

    def hasPrimeTimesLeft(self):
        season = self.getCurrentSeason()
        currTime = time_utils.getCurrentLocalServerTimestamp()
        if season is not None and season.hasActiveCycle(currTime):
            seasonEnd = season.getEndDate()
            peripheryIDs = self.__getPeripheryIDs()
            for peripheryID, primeTime in self.getPrimeTimes().items():
                if peripheryID in peripheryIDs and primeTime.getPeriodsBetween(currTime, seasonEnd):
                    return True

        return False

    def hasEnoughTickets(self):
        countNormal = self.getWtEventTokensCount()
        countQuick = self.getWtEventQuickTokensCount()
        drawCount = self.getTokensToDraw()
        return countNormal + countQuick >= drawCount

    def hasSpecialBoss(self):
        specialVehicle = self.getSpecialBoss()
        return specialVehicle.invID != -1 if specialVehicle is not None else False

    def getWtEventTokensCount(self):
        return self._eventsCache.questsProgress.getTokenCount(self.getWtEventTokenName())

    def getWtEventQuickTokensCount(self):
        return self._eventsCache.questsProgress.getTokenCount(self.getWtEventQuickTokenName())

    def getWtEventTokenName(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_TOKEN_STORAGE, '')

    def getWtEventQuickTokenName(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_QUICK_TOKEN_STORAGE, '')

    def getWtEventHunterProgressTokenName(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_HUNTER_PROGRESS_TOKEN_STORAGE, '')

    def getWtEventBossProgressTokenName(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_BOSS_PROGRESS_TOKEN_STORAGE, '')

    def getTokensToDraw(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_TOKENS_DRAW_STORAGE, 1)

    def getWtEventQuestPrefix(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_QUEST_PREFIX_NAME, '')

    def getHunterCollectionSize(self):
        collection = self.getHunterCollection()
        return len(collection)

    def getBossCollectionSize(self):
        collection = self.getBossCollection()
        return len(collection)

    def getTotalCollectionSize(self):
        return self.getHunterCollectionSize() + self.getBossCollectionSize()

    def getHunterCollection(self):
        return self.__getCollection(self.__WT_EVENT_HUNTER_COLLECTION_NAME)

    def getBossCollection(self):
        return self.__getCollection(self.__WT_EVENT_BOSS_COLLECTION_NAME)

    def getHunterCollectedCount(self):
        tokensCount = self._eventsCache.questsProgress.getTokenCount(self.getWtEventHunterProgressTokenName())
        collectionSize = self.getHunterCollectionSize()
        return min(tokensCount, collectionSize)

    def getBossCollectedCount(self):
        tokensCount = self._eventsCache.questsProgress.getTokenCount(self.getWtEventBossProgressTokenName())
        collectionSize = self.getBossCollectionSize()
        return min(tokensCount, collectionSize)

    def getTotalCollectedCount(self):
        return self.getHunterCollectedCount() + self.getBossCollectedCount()

    def getNextRewardItemsLeft(self):
        progression = self.__getItemsProgression()
        currentProgress = self.getTotalCollectedCount()
        nextValue = findFirst(lambda value: value > currentProgress, progression, currentProgress)
        return nextValue - currentProgress

    def getXpConfig(self):
        wtEventData = self.__getWtEventData()
        xp = wtEventData.get('xp', {'hunter': {'win': (),
                    'lose': ()},
         'boss': {'win': (),
                  'lose': ()}})
        return xp

    def getItemProgression(self):
        wtEventData = self.__getWtEventData()
        itemsProgression = wtEventData.get(self.__WT_EVENT_PROGRESSION_CONFIG, {})
        result = []
        for _, data in sorted(itemsProgression.iteritems(), key=itemgetter(0)):
            rewards = self.__getQuestRewards(data.get('questName', ''))
            result.append((data.get('itemsCount', 0), rewards))

        return result

    def getProgressionConfig(self):
        wtEventData = self.__getWtEventData()
        return wtEventData.get(self.__WT_EVENT_PROGRESSION_CONFIG, {})

    def getDataByQuestName(self, questId):
        wtEventData = self.__getWtEventData()
        itemsProgression = wtEventData.get(self.__WT_EVENT_PROGRESSION_CONFIG, {})
        itemsCount = 0
        rewards = []
        questOrder = 0
        for order, data in itemsProgression.iteritems():
            if data.get('questName', '') == questId:
                questOrder = order
                itemsCount = data.get('itemsCount', 0)
                rewards = self.__getQuestRewards(questId)
                break

        return (itemsCount, rewards, questOrder == len(itemsProgression))

    def getLootBoxRewards(self, boxType):
        if self.__lootBoxData is None or boxType not in self.__lootBoxData:
            return []
        else:
            result = []
            for section, bonuses in self.__lootBoxData[boxType].iteritems():
                if section == 'gold':
                    result.append('gold_{}'.format(bonuses[0].getValue()))
                result.append(section)

            return result

    def getLootBoxDetailedRewards(self, boxType):
        return {} if self.__lootBoxData is None or boxType not in self.__lootBoxData else self.__lootBoxData[boxType]

    def getIdAndCollectionByIntCD(self, intCD):
        for bonusId, bonusItem in self.getHunterCollection().iteritems():
            if intCD == _makeIntCDByBonusItem(bonusItem):
                return (bonusId, self.__WT_EVENT_HUNTER_COLLECTION_NAME)

        for bonusId, bonusItem in self.getBossCollection().iteritems():
            if intCD == _makeIntCDByBonusItem(bonusItem):
                return (bonusId, self.__WT_EVENT_BOSS_COLLECTION_NAME)

        return (None, None)

    def hasItem(self, bonusItem):
        if 'customizations' in bonusItem:
            item = self._itemsCache.items.getItemByCD(_makeIntCDByBonusItem(bonusItem))
            return item is not None and bool(item.fullCount())
        elif 'crewSkins' in bonusItem:
            item = self._itemsCache.items.getItemByCD(_makeIntCDByBonusItem(bonusItem))
            return item is not None and bool(item.inAccount())
        else:
            return False

    def onHeroTankMouseClicked(self, event):
        isEvent = event.ctx['data']['isEvent']
        if isEvent:
            if not self.isEventPrbActive():
                self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)
        isHangarRandomVehicle = event.ctx['data'].get('hangarRandomVehicle')
        if isHangarRandomVehicle and self.isEventPrbActive():
            self.__doSelectAction(PREBATTLE_ACTION_NAME.RANDOM)

    def onPortalClicked(self, event):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE)

    def isLastSeasonDay(self):
        season = self.getCurrentSeason()
        if season is None:
            return False
        else:
            currentCycleEnd = season.getCycleEndDate()
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleEnd))
            return 0 < timeLeft < time_utils.ONE_DAY

    @process
    def __doSelectAction(self, actionName):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            yield dispatcher.doSelectAction(PrbAction(actionName))
        return

    @process
    def showEventMetaPage(self):
        if self.isActive():
            isPrbActive = self.isEventPrbActive()
            if not isPrbActive:
                isPrbActive = yield self.__doSelectEventPrb()
            if isPrbActive:
                showWtEventCollectionWindow()

    @process
    def showEventHangar(self):
        if self.isActive():
            if not self.isEventPrbActive():
                yield self.__doSelectEventPrb()
            showHangar()

    def getVehicleEquipmentIDs(self, vehDescr):
        config = self.__getGameEventConfig()
        equipments = config.eventBattles.get('equipments')
        if equipments is not None:
            tags = vehDescr.type.tags
            if 'event_boss' in tags:
                return equipments.get('boss', [])
            if 'event_hunter' in tags:
                return equipments.get('hunters', [])
        return list()

    @async
    @process
    def __doSelectEventPrb(self, callback):
        if self.isActive():
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is not None:
                result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE))
                callback(result)
            else:
                callback(False)
        else:
            callback(False)
        return

    def __isWelcomeScreenShown(self):
        eventStorage = self._settingsCore.serverSettings.getEventStorage()
        return eventStorage.get('wtIntroShown', False)

    def __getCollection(self, collectionName):
        wtEventData = self.__getWtEventData()
        collection = wtEventData.get(collectionName, {})
        return collection

    def __getItemsProgression(self):
        wtEventData = self.__getWtEventData()
        itemsProgression = wtEventData.get(self.__WT_EVENT_PROGRESSION_CONFIG, {})
        return [ data.get('itemsCount', 0) for _, data in sorted(itemsProgression.iteritems(), key=itemgetter(0)) ]

    def __getQuestRewards(self, questID):
        quests = self._eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        return quests[questID].getBonuses()

    def __onTokensUpdate(self, diff):
        if self.getWtEventHunterProgressTokenName() in diff or self.getWtEventBossProgressTokenName() in diff:
            self.onProgressUpdated()

    def __stop(self):
        self.stopGlobalListening()
        self.__notificator.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__readyToGoPortal = {'camera': False,
         'boss': False,
         'hunter': False}
        self.__wtEventSelected = False

    def __getEventData(self):
        return self._eventsCache.getIngameEventsData()

    def __getWtEventData(self):
        return self.__getEventData().get(self.__WT_EVENT_STORAGE_NAME, {})

    def __getGameEventConfig(self):
        return makeTupleByDict(_GameEventConfig, self.__getEventData())

    def __getCurrentCycleInfo(self):
        season = self.getCurrentSeason()
        if season is not None:
            if season.hasActiveCycle(time_utils.getCurrentLocalServerTimestamp()):
                return (season.getCycleEndDate(), True)
            return (season.getCycleStartDate(), False)
        else:
            return (None, False)

    def __hasPrimeTimesLeft(self, currTime):
        season = self.getCurrentSeason()
        if season is not None and season.hasActiveCycle(currTime):
            seasonEnd = season.getEndDate()
            peripheryIDs = self.__getPeripheryIDs()
            for peripheryID, primeTime in self.getPrimeTimes().iteritems():
                if peripheryID in peripheryIDs and primeTime.getPeriodsBetween(currTime, seasonEnd):
                    return True

        return False

    def __getPeripheryIDs(self):
        if self._connectionMgr.isStandalone():
            return {self._connectionMgr.peripheryID}
        return set([ host.peripheryID for host in g_preDefinedHosts.hostsWithRoaming() ])

    def __getHostList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self._connectionMgr.isStandalone():
            hostsList.insert(0, (self._connectionMgr.url,
             self._connectionMgr.serverUserName,
             self._connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        return hostsList

    def __hasPrimeTimeServers(self, statuses):
        peripheryIDs = self.__getPeripheryIDs()
        return any((self.getPrimeTimeStatus(peripheryID)[0] in statuses for peripheryID in peripheryIDs))

    def __packLootBoxData(self, ctx):
        self.__lootBoxData = {}
        for box in ctx.itervalues():
            rollInfo = box.get('reRoll')
            rewards = {}
            rewards.update(rollInfo.get('bonus', {}))
            rewards.update(rollInfo.get('guaranteedBonus', {}))
            bonuses = self.__convertToBonuses(rewards)
            packedBonuses = {}
            boxType = box.get('type', '')
            if boxType in self.__lootBoxData:
                continue
            for bonus in bonuses:
                name = bonus.getName()
                if name in ('gold', 'vehicles'):
                    key = name
                elif name == 'customizations' or name == 'crewSkins':
                    key = 'collection'
                elif name == 'battleToken':
                    continue
                else:
                    key = 'random'
                if key not in packedBonuses:
                    packedBonuses[key] = []
                packedBonuses[key].append(bonus)

            self.__lootBoxData[boxType] = packedBonuses

    @staticmethod
    def __convertToBonuses(rewards):
        bonuses = BattlePassAwardsManager.composeBonuses([rewards])
        hasNewBonuses = True
        while hasNewBonuses:
            hasNewBonuses = False
            flatBonuses = []
            for bonus in bonuses:
                if bonus.getName() == 'groups':
                    flatBonuses.extend(BattlePassAwardsManager.composeBonuses(bonus.getValue()))
                    hasNewBonuses = True
                if bonus.getName() in ('oneof', 'allof'):
                    flatBonuses.extend(bonus.getOptionalBonuses())
                    hasNewBonuses = True
                flatBonuses.append(bonus)

            bonuses = flatBonuses

        bonuses = mergeBonuses(bonuses)
        bonuses = splitBonuses(bonuses)
        return bonuses

    def __updateEvent(self):
        isEventEnabled = self.isEnabled()
        if self.__isEventEnabled != isEventEnabled:
            self.__isEventEnabled = isEventEnabled
            self.onEventUpdated()
        self.__notificator.startNotification()

    def __cameraReadyToGoPortal(self, _):
        self.__readyToGoPortal['camera'] = True
        self.__checkReadyToGoPortal()

    def __onHeroTankLeaveWorld(self, event):
        isBoss = event.ctx.get('isBoss', False)
        if isBoss:
            self.__readyToGoPortal['boss'] = False
        else:
            self.__readyToGoPortal['hunter'] = False

    def __onHeroTankLoaded(self, event):
        entity = event.ctx.get('entity', None)
        if entity is not None and entity.isEvent:
            if entity.isBoss:
                self.__setBossHeroTankReady()
            else:
                self.__setHunterHeroTankReady()
        self.__checkReadyToGoPortal()
        return

    def __wtEventSelectedCamera(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_SELECTED, ctx={'data': {'setStoredVehicle': False}}), EVENT_BUS_SCOPE.LOBBY)

    def __checkReadyToGoPortal(self):
        if self.__wtEventSelected and all(self.__readyToGoPortal.itervalues()) and not self.eventHeroTankIsInFocus:
            BigWorld.callback(1.0, self.__wtEventSelectedCamera)
        if not self.__wtEventSelected and self.isEventPrbActive() and all(self.__readyToGoPortal.itervalues()):
            welcomeScreen = self.__guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.wt_event.WTEventWelcome())
            if welcomeScreen is None:
                g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.WT_EVENT_SELECTED, ctx={'data': {'setStoredVehicle': True}}), EVENT_BUS_SCOPE.LOBBY)
        return

    def __onNonEventVehicleChosen(self, _):
        if self.isEventPrbActive():
            self.runStandardHangarMode()

    @process
    def __collectionViewLoaded(self, _):
        if not self.isEventPrbActive():
            yield self.__doSelectEventPrb()

    def __setHunterHeroTankReady(self):
        self.__readyToGoPortal['hunter'] = True

    def __setBossHeroTankReady(self):
        self.__readyToGoPortal['boss'] = True

    def __getTimeForTurnOffEntryPoint(self):
        currentSeason = self.getCurrentSeason()
        if currentSeason is not None:
            currentTime = time_utils.getCurrentLocalServerTimestamp()
            return max(currentSeason.getStartDate() + time_utils.ONE_DAY * 3 - currentTime, 0)
        else:
            return 0

    def getEventVehiclesCarouselSorted(self):
        return [self.wtSpecialBossCD, self.wtBossCD, self.wtHunterCD]

    def isInWTEventSquad(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.EVENT)
        else:
            return False
