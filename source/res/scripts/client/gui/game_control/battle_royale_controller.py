# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/battle_royale_controller.py
import logging
import typing
import json
import BigWorld
import Event
from shared_utils import nextTick
import season_common
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ROYALE_VEHICLE, CURRENT_VEHICLE
from account_helpers.settings_core.settings_constants import GRAPHICS
from adisp import process
from constants import QUEUE_TYPE, Configs, PREBATTLE_TYPE, ARENA_BONUS_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.battle_royale.constants import AmmoTypes, BattleRoyalePerfProblems
from gui.battle_royale.royale_models import BattleRoyaleSeason
from gui.game_control.br_vo_controller import BRVoiceOverController
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import event_dispatcher, events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from helpers.statistics import HARDWARE_SCORE_PARAMS
from season_provider import SeasonProvider
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IBattleRoyaleController, IEventProgressionController
from skeletons.gui.game_control import IEventsNotificationsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.shared.utils import IHangarSpaceReloader
from skeletons.gui.shared.hangar_spaces_switcher import IHangarSpacesSwitcher
from gui.ClientHangarSpace import SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.customization import ICustomizationService
_logger = logging.getLogger(__name__)

class BATTLE_ROYALE_GAME_LIMIT_TYPE(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


PERFORMANCE_GROUP_LIMITS = {BattleRoyalePerfProblems.HIGH_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'osBit': 1,
                                                                                   'graphicsEngine': 0}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'graphicsEngine': 0},
                                       BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 BattleRoyalePerfProblems.MEDIUM_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

class BattleRoyaleController(Notifiable, SeasonProvider, IBattleRoyaleController, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarsSpace = dependency.descriptor(IHangarSpace)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battleResultsService = dependency.descriptor(IBattleResultsService)
    __hangarSpacesSwitcher = dependency.descriptor(IHangarSpacesSwitcher)
    __hangarSpaceReloader = dependency.descriptor(IHangarSpaceReloader)
    __eventProgression = dependency.descriptor(IEventProgressionController)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __c11nService = dependency.descriptor(ICustomizationService)
    TOKEN_QUEST_ID = 'token:br:title:'
    DAILY_QUEST_ID = 'steel_hunter'
    MODE_ALIAS = 'battleRoyale'
    PROGRESSION_XP_TOKEN = 'token:br:point'
    MAX_STORED_ARENAS_RESULTS = 20

    def __init__(self):
        super(BattleRoyaleController, self).__init__()
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self._setSeasonSettingsProvider(self.getModeSettings)
        self._setPrimeTimesIteratorGetter(self.getPrimeTimesIter)
        self.__clientValuesInited = False
        self.__clientShields = {}
        self.__performanceGroup = None
        self.__serverSettings = None
        self.__battleRoyaleSettings = None
        self.__wasInLobby = False
        self.__equipmentCount = {}
        self.__equipmentSlots = tuple()
        self.__voControl = None
        self.__playerMaxLevel = 0
        self.__levelProgress = tuple()
        self.__shownBattleResultsForArena = []
        self.__defaultHangars = {}
        self.__c11nVisible = False
        return

    def init(self):
        super(BattleRoyaleController, self).init()
        self.__voControl = BRVoiceOverController()
        self.__voControl.init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))

    def fini(self):
        self.__voControl.fini()
        self.__voControl = None
        self.__equipmentCount = None
        self.__defaultHangars = None
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.clearNotification()
        super(BattleRoyaleController, self).fini()
        return

    def wasInLobby(self):
        return self.__wasInLobby

    def onLobbyInited(self, event):
        super(BattleRoyaleController, self).onLobbyInited(event)
        if not self.__clientValuesInited:
            self.__clientValuesInited = True
        g_clientUpdateManager.addCallbacks({'battleRoyale': self.__updateRoyale})
        self.startNotification()
        self.startGlobalListening()
        self.__hangarsSpace.onSpaceChangedByAction += self.__onSpaceChanged
        self.__hangarsSpace.onSpaceChanged += self.__onSpaceChanged
        self.__c11nService.onVisibilityChanged += self.__onC11nVisibilityChanged
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__onEventNotification(self.__notificationsCtrl.getEventsNotifications())
        self.__updateMode()
        self.__wasInLobby = True
        self.__updateMaxLevelAndProgress()
        if not self.__hangarsSpace.spaceInited or self.__hangarsSpace.spaceLoading():
            self.__hangarsSpace.onSpaceCreate += self.__onSpaceCreate
        else:
            self.__updateSpace()
        self.__eventProgression.onUpdated += self.__eventAvailabilityUpdate
        nextTick(self.__eventAvailabilityUpdate)()

    def __onEventNotification(self, added, removed=()):
        for evNotification in removed:
            if evNotification.eventType in (SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM):
                self.__defaultHangars[evNotification.eventType == SERVER_CMD_CHANGE_HANGAR_PREM] = None

        for evNotification in added:
            if evNotification.eventType in (SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM):
                try:
                    data = json.loads(evNotification.data)
                    path = data['hangar']
                except Exception:
                    path = evNotification.data

                self.__defaultHangars[evNotification.eventType == SERVER_CMD_CHANGE_HANGAR_PREM] = path

        return

    def onDisconnected(self):
        self.__wasInLobby = False
        self.__clearClientValues()
        self.__clear()
        super(BattleRoyaleController, self).onDisconnected()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__battleResultsService.onResultPosted += self.__showBattleResults
        super(BattleRoyaleController, self).onAccountBecomePlayer()

    def onAvatarBecomePlayer(self):
        self.__clear()
        self.__battleResultsService.onResultPosted -= self.__showBattleResults
        if self.__sessionProvider.arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
            self.__voControl.activate()
        else:
            self.__voControl.deactivate()
        self.__voControl.onAvatarBecomePlayer()
        super(BattleRoyaleController, self).onAvatarBecomePlayer()

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def getEndTime(self):
        return self.getCurrentSeason().getCycleEndDate()

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            _logger.debug('Current performance group %s', self.__performanceGroup)
        return self.__performanceGroup

    def getDefaultAmmoCount(self, itemKey, intCD=None, vehicleName=None):
        if itemKey in AmmoTypes.SHELLS or itemKey in AmmoTypes.CHARGES:
            return self.__equipmentCount.get(itemKey, 0)
        else:
            if itemKey == AmmoTypes.ITEM:
                if intCD is None:
                    _logger.error('Cannot get count of equipment. Equipment id not specified')
                    return 0
                if vehicleName is None:
                    _logger.error("Cannot get count of '%r' equipment. Vehicle not specified", intCD)
                    return 0
                vehiclesSlotsConfig = self.getModeSettings().vehiclesSlotsConfig
                if vehicleName not in vehiclesSlotsConfig:
                    _logger.error("Cannot get count of '%r' equipment. Vehicle '%r' not found", intCD, vehicleName)
                    return 0
                for chargeId, equipmentId in vehiclesSlotsConfig[vehicleName].iteritems():
                    if equipmentId == intCD:
                        return self.getDefaultAmmoCount(chargeId)

            else:
                _logger.warning("Can't get default ammo count. Unknown item key: '%r'.", itemKey)
            return 0

    def getVehicleSlots(self):
        return self.__equipmentSlots

    def getBrVehicleEquipmentIds(self, vehicleName):
        vehiclesSlotsConfig = self.getModeSettings().vehiclesSlotsConfig
        if vehicleName not in vehiclesSlotsConfig:
            _logger.error("Get equipment for vehicle '%r' failed. Vehicle not found. Slots config %s", vehicleName, vehiclesSlotsConfig)
            return None
        else:
            vehiclesSlots = vehiclesSlotsConfig[vehicleName]
            result = []
            for chargeName in sorted(vehiclesSlots.keys()):
                result.append(vehiclesSlots[chargeName])

            return result

    @staticmethod
    def getBrCommanderSkills():
        result = []
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            for _, tankman in vehicle.crew:
                if tankman is not None:
                    for skill in tankman.skills:
                        result.append(skill)

        return result

    def isBattleRoyaleMode(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE) or state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
        else:
            return False

    def isInBattleRoyaleSquad(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
        else:
            return False

    def onPrbEntitySwitched(self):
        self.__updateMode()
        self.__updateSpace()

    def selectRoyaleBattle(self):
        if self.isEnabled():
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher is None:
                _logger.error('Prebattle dispatcher is not defined')
                return
            self.__doSelectBattleRoyalePrb(dispatcher)
        return

    def selectRandomBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectRandomPrb(dispatcher)
            return

    def getPlayerLevelInfo(self):
        return self.__itemsCache.items.battleRoyale.accTitle

    def getMaxPlayerLevel(self):
        return self.__playerMaxLevel

    def getPointsProgressForLevel(self, level):
        if self.__playerMaxLevel == 0:
            self.__updateMaxLevelAndProgress()
        return self.__levelProgress[level]

    def getStats(self):
        return self.__itemsCache.items.battleRoyale

    def _createSeason(self, cycleInfo, seasonData):
        return BattleRoyaleSeason(cycleInfo, seasonData)

    def __updateMaxLevelAndProgress(self):
        eventProgression = self.getModeSettings().eventProgression
        if eventProgression:
            self.__levelProgress = eventProgression['brPointsByTitle'] + (0,)
            self.__playerMaxLevel = len(self.__levelProgress) - 1

    def __onSpaceChanged(self):
        switchItems = self.__hangarSpacesSwitcher.itemsToSwitch
        if self.isBattleRoyaleMode() and self.__hangarSpacesSwitcher.currentItem != switchItems.BATTLE_ROYALE:
            self.selectRandomBattle()

    def __eventAvailabilityUpdate(self, *_):
        season = self.__eventProgression.getCurrentSeason()
        isEnabled = self.__eventProgression.isSteelHunter and self.__eventProgression.modeIsEnabled()
        isEnabledSeason = season is not None
        battleRoyaleEnabled = isEnabled and isEnabledSeason
        if not battleRoyaleEnabled and self.isBattleRoyaleMode():
            self.selectRandomBattle()
        return

    def __onSpaceCreate(self):
        nextTick(self.__updateSpace)()

    def __updateSpace(self):
        if not self.__c11nVisible and self.__hangarsSpace.spaceInited and not self.__hangarsSpace.spaceLoading():
            switchItems = self.__hangarSpacesSwitcher.itemsToSwitch
            isBrSpace = self.__hangarSpacesSwitcher.currentItem == switchItems.BATTLE_ROYALE
            isBrMode = self.isBattleRoyaleMode()
            if isBrMode and not isBrSpace:
                g_eventBus.handleEvent(events.HangarSpacesSwitcherEvent(events.HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, ctx={'switchItemName': switchItems.BATTLE_ROYALE}), scope=EVENT_BUS_SCOPE.LOBBY)
            elif not isBrMode and isBrSpace:
                defaultHangarPath = self.__defaultHangars.get(self.__hangarsSpace.isPremium)
                if defaultHangarPath is not None:
                    self.__hangarSpaceReloader.changeHangarSpace(defaultHangarPath)
                else:
                    g_eventBus.handleEvent(events.HangarSpacesSwitcherEvent(events.HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE, ctx={'switchItemName': switchItems.DEFAULT}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __updateMode(self):
        if self.isBattleRoyaleMode():
            self.__enableRoyaleMode()
        else:
            self.__disableRoyaleMode()

    def __enableRoyaleMode(self):
        royaleVehicleID = AccountSettings.getFavorites(ROYALE_VEHICLE)
        if not royaleVehicleID or self.__itemsCache.items.getVehicle(royaleVehicleID) is None:
            criteria = REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE]) | REQ_CRITERIA.INVENTORY
            vehicles = self.__itemsCache.items.getVehicles
            royaleVehicle = first(sorted(vehicles(criteria=criteria).values(), key=lambda item: item.intCD))
            if royaleVehicle:
                royaleVehicleID = royaleVehicle.invID
        if royaleVehicleID:
            g_currentVehicle.selectVehicle(royaleVehicleID)
        else:
            g_currentVehicle.selectNoVehicle()
        self.__voControl.activate()
        return

    def __disableRoyaleMode(self):
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        if storedVehInvID:
            g_currentVehicle.selectVehicle(storedVehInvID)
        else:
            g_currentVehicle.selectNoVehicle()
        self.__voControl.deactivate()

    @process
    def __doSelectBattleRoyalePrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE))

    @process
    def __doSelectRandomPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    @process
    def fightClick(self):
        dispatcher = g_prbLoader.getDispatcher()
        if not dispatcher:
            return
        lobbyContext = dependency.instance(ILobbyContext)
        navigationPossible = yield lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if dispatcher:
                dispatcher.doAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE))
            else:
                _logger.error('Prebattle dispatcher is not defined')

    @process
    def _doLeaveBattleRoyalePrb(self, dispatcher):
        if dispatcher is None:
            return
        else:
            yield dispatcher.doLeaveAction(LeavePrbAction())
            return

    def __getBattleRoyaleSettings(self):
        generalSettings = self.__serverSettings.battleRoyale
        cycleID = None
        now = time_utils.getCurrentLocalServerTimestamp()
        _, cycleInfo = season_common.getSeason(generalSettings.asDict(), now)
        if cycleInfo:
            _, _, _, cycleID = cycleInfo
        for season in generalSettings.seasons.values():
            if cycleID in season.get('cycles', {}):
                return generalSettings.replace(season).replace(season['cycles'][cycleID])

        return generalSettings

    def __getCachedSettings(self):
        return self.__battleRoyaleSettings

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
        self.__eventAvailabilityUpdate()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = serverSettings
        self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
        self.__updateEquipmentCount()
        self.__serverSettings.onServerSettingsChange += self.__updateRoyaleSettings
        return

    def __updateRoyaleSettings(self, diff):
        if Configs.BATTLE_ROYALE_CONFIG.value not in diff:
            return
        else:
            self.__eventAvailabilityUpdate()
            self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
            self.__updateEquipmentCount()
            self.__divisions = None
            self.onUpdated()
            self.__resetTimer()
            return

    def __clear(self):
        self.stopNotification()
        self.stopGlobalListening()
        self.__hangarsSpace.onSpaceChangedByAction -= self.__onSpaceChanged
        self.__hangarsSpace.onSpaceChanged -= self.__onSpaceChanged
        self.__hangarsSpace.onSpaceCreate -= self.__onSpaceCreate
        self.__eventProgression.onUpdated -= self.__eventAvailabilityUpdate
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.__c11nService.onVisibilityChanged -= self.__onC11nVisibilityChanged
        self.__defaultHangars = {}
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearClientValues(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = None
        self.__clientValuesInited = False
        return

    def __updateRoyale(self, _):
        self.onUpdated()
        self.__resetTimer()

    def __analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        self.__performanceGroup = BattleRoyalePerfProblems.LOW_RISK
        for groupName, conditions in PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    self.__performanceGroup = groupName
                    return

        return

    def __updateEquipmentCount(self):
        if self.__equipmentCount:
            self.__equipmentCount = None
        self.__equipmentCount = {}
        items = self.__battleRoyaleSettings.defaultAmmo
        for itemGroup in items:
            groupKey, groupItems = itemGroup
            self.__equipmentCount[groupKey] = groupItems[0]

        return

    def __showBattleResults(self, reusableInfo, _, resultsWindow):
        battleRoyaleArenaTypes = (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)
        if reusableInfo.common.arenaBonusType in battleRoyaleArenaTypes:
            batleRoyaleInfo = reusableInfo.personal.getBattleRoyaleInfo()
            title, _ = batleRoyaleInfo.get('accBRTitle', (None, None))
            prevTitle, _ = batleRoyaleInfo.get('prevBRTitle', (None, None))
            if title == prevTitle:
                return None
            arenaUniqueID = reusableInfo.arenaUniqueID
            if arenaUniqueID not in self.__shownBattleResultsForArena:
                self.__shownBattleResultsForArena.append(arenaUniqueID)
                self.__shownBattleResultsForArena = self.__shownBattleResultsForArena[-self.MAX_STORED_ARENAS_RESULTS:]
                event_dispatcher.showBattleRoyaleLevelUpWindow(reusableInfo, resultsWindow)
        return None

    def __onC11nVisibilityChanged(self, isVisible):
        self.__c11nVisible = isVisible
        self.__updateSpace()

    def getPrimeTimesIter(self, primeTimes):
        for primeTime in primeTimes.itervalues():
            yield primeTime

    @staticmethod
    def getModeSettings():
        lobbyContext = dependency.instance(ILobbyContext)
        generalSettings = lobbyContext.getServerSettings().battleRoyale
        return generalSettings
