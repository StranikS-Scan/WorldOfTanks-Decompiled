# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/game_control/battle_royale_controller.py
import json
import logging
from collections import namedtuple
from functools import partial
from itertools import groupby
import BigWorld
import typing
import Event
import season_common
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ROYALE_VEHICLE, CURRENT_VEHICLE, ROYALE_INTRO_VIDEO_SHOWN_FOR_SEASON
from adisp import adisp_process
from battle_royale.gui.constants import AmmoTypes, BattleRoyalePerfProblems, BattleRoyaleSubMode, BattleRoyaleModeState
from battle_royale.gui.game_control.br_vo_controller import BRVoiceOverController
from battle_royale.gui.royale_models import BattleRoyaleSeason
from battle_royale.gui.shared.event_dispatcher import showInfoPage
from battle_royale_progression.skeletons.game_controller import IBRProgressionOnTokensController
from constants import QUEUE_TYPE, Configs, PREBATTLE_TYPE, ARENA_BONUS_TYPE, BATTLE_ROYALE_SCENE
from gui import GUI_NATIONS_ORDER_INDEX
from gui import GUI_SETTINGS
from gui.ClientHangarSpace import SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen import R
from gui.periodic_battles.models import PeriodType
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.server_events.events_constants import BATTLE_ROYALE_GROUPS_ID
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import getParentWindow, showBrowserOverlayView
from gui.shared.events import ProfilePageEvent, ProfileStatisticEvent, ProfileTechniqueEvent
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.items_parameters.params import ShellParams
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.graphics import getGraphicsEngineValue
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier, TimerNotifier
from helpers import dependency, time_utils
from helpers.statistics import HARDWARE_SCORE_PARAMS
from items import vehicles
from items.battle_royale import isBattleRoyale
from battle_royale.gui.constants import SUB_MODE_ID_KEY
from shared_utils import first
from shared_utils import nextTick
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEventsNotificationsController, IHangarSpaceSwitchController, IBattleRoyaleController, IBattleRoyaleTournamentController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from stats_params import BATTLE_ROYALE_STATS_ENABLED
from gui.shared.money import DynamicMoney
from battle_royale.gui.constants import BR_COIN
if typing.TYPE_CHECKING:
    from helpers.server_settings import BattleRoyaleConfig
    from gui.shared.gui_items.tankman_skill import TankmanSkill
_logger = logging.getLogger(__name__)
BattleRoyaleProgressionPoints = namedtuple('BattleRoyaleProgressionPoints', ['lastInRange', 'points'])

class BATTLE_ROYALE_GAME_LIMIT_TYPE(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


PERFORMANCE_GROUP_LIMITS = {BattleRoyalePerfProblems.HIGH_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'osBit': 1,
                                                                                   'graphicsEngine': 0}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.SYSTEM_DATA: {'graphicsEngine': 0},
                                       BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 BattleRoyalePerfProblems.MEDIUM_RISK: [{BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 300}}, {BATTLE_ROYALE_GAME_LIMIT_TYPE.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}
_PERIOD_INFO_TO_MOD_STATE = {PeriodType.UNDEFINED: BattleRoyaleModeState.Unavailable,
 PeriodType.BEFORE_SEASON: BattleRoyaleModeState.Unavailable,
 PeriodType.BETWEEN_SEASONS: BattleRoyaleModeState.Unavailable,
 PeriodType.AFTER_SEASON: BattleRoyaleModeState.Finished,
 PeriodType.BEFORE_CYCLE: BattleRoyaleModeState.Unavailable,
 PeriodType.BETWEEN_CYCLES: BattleRoyaleModeState.Unavailable,
 PeriodType.AFTER_CYCLE: BattleRoyaleModeState.Finished,
 PeriodType.AVAILABLE: BattleRoyaleModeState.Regular,
 PeriodType.FROZEN: BattleRoyaleModeState.Unavailable,
 PeriodType.NOT_AVAILABLE: BattleRoyaleModeState.CeasefireCurrentServer,
 PeriodType.ALL_NOT_AVAILABLE: BattleRoyaleModeState.CeasefireAllServers,
 PeriodType.STANDALONE_NOT_AVAILABLE: BattleRoyaleModeState.CeasefireAllServers,
 PeriodType.NOT_AVAILABLE_END: BattleRoyaleModeState.CeasefireCurrentServer,
 PeriodType.ALL_NOT_AVAILABLE_END: BattleRoyaleModeState.Finished,
 PeriodType.STANDALONE_NOT_AVAILABLE_END: BattleRoyaleModeState.Finished,
 PeriodType.NOT_SET: BattleRoyaleModeState.Unavailable,
 PeriodType.ALL_NOT_SET: BattleRoyaleModeState.Unavailable,
 PeriodType.STANDALONE_NOT_SET: BattleRoyaleModeState.Unavailable}

class BattleRoyaleController(Notifiable, SeasonProvider, IBattleRoyaleController, IPrbListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarsSpace = dependency.descriptor(IHangarSpace)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    TOKEN_QUEST_ID = 'token:br:title:'
    MAX_STORED_ARENAS_RESULTS = 20

    def __init__(self):
        super(BattleRoyaleController, self).__init__()
        self.__em = Event.EventManager()
        self.onUpdated = Event.Event(self.__em)
        self.onPrimeTimeStatusUpdated = Event.Event(self.__em)
        self.onWidgetUpdate = Event.Event(self.__em)
        self.onBalanceUpdated = Event.Event(self.__em)
        self.onSubModeUpdated = Event.Event(self.__em)
        self.onStatusTick = Event.Event(self.__em)
        self.onTournamentBannerStateChanged = Event.Event(self.__em)
        self.onEntryPointUpdated = Event.Event(self.__em)
        self.__balance = None
        self.__clientValuesInited = False
        self.__clientShields = {}
        self.__performanceGroup = None
        self.__serverSettings = None
        self.__battleRoyaleSettings = None
        self.__equipmentCount = {}
        self.__isBRLogicEnabled = False
        self.__voControl = None
        self.__defaultHangars = {}
        self.__isNeedToUpdateHeroTank = False
        self.__profStatSelectBattlesTypeInited = False
        self.__profTechSelectBattlesTypeInited = False
        self.__callbackID = None
        self.__isTournamentBannerEnabled = None
        self.__currentSubModeID = BattleRoyaleSubMode.SOLO_MODE_ID
        return

    def init(self):
        super(BattleRoyaleController, self).init()
        self.__balance = DynamicMoney()
        self.__voControl = BRVoiceOverController()
        self.__voControl.init()
        self.addNotificator(SimpleNotifier(self.__getTournamentBannerTimerDelta, self.__updateTournamentBannerState))
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))
        self.addNotificator(TimerNotifier(self.getTimer, self.__timerNotifier))
        self.__spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange

    def fini(self):
        self.__voControl.fini()
        self.__voControl = None
        self.__equipmentCount = None
        self.__defaultHangars = None
        self.__em.clear()
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.clearNotification()
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        super(BattleRoyaleController, self).fini()
        return

    def onLobbyInited(self, event):
        super(BattleRoyaleController, self).onLobbyInited(event)
        if not self.__clientValuesInited:
            self.__clientValuesInited = True
        g_clientUpdateManager.addCallbacks({'battleRoyale': self.__updateRoyale,
         'cache.dynamicCurrencies': self.__updateDynamicCurrencies})
        self.startNotification()
        self.__initBalanceCurrencies()
        self.__hangarsSpace.onVehicleChanged += self.__onVehicleChanged
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__onEventNotification(self.__notificationsCtrl.getEventsNotifications())
        self.__battleRoyaleTournamentController.onSelectBattleRoyaleTournament += self.__selectBattleRoyaleTournament
        g_eventBus.addListener(ProfilePageEvent.SELECT_PROFILE_ALIAS, self.__onChangeProfileAlias, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(ProfileStatisticEvent.SELECT_BATTLE_TYPE, self.__onProfileStatisticSelectBattlesType, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(ProfileStatisticEvent.DISPOSE, self.__onProfileStatisticDispose, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(ProfileTechniqueEvent.SELECT_BATTLE_TYPE, self.__onProfileTechniqueSelectBattlesType, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(ProfileTechniqueEvent.DISPOSE, self.__onProfileTechniqueDispose, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        nextTick(self.__eventAvailabilityUpdate)()

    def getBRCoinBalance(self, default=None):
        return self.__balance.get(BR_COIN, default) if self.__balance is not None else default

    def __initBalanceCurrencies(self):
        self.__updateBalanceCurrencies()
        self.onBalanceUpdated()

    def __updateBalanceCurrencies(self):
        self.__balance = self.__itemsCache.items.stats.getDynamicMoney()

    def __updateDynamicCurrencies(self, currencies):
        if BR_COIN not in currencies:
            return False
        brCoin = currencies.get(BR_COIN, 0)
        if self.getBRCoinBalance(0) != brCoin:
            self.__updateBalanceCurrencies()
        self.onBalanceUpdated()

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
        self.__clearClientValues()
        self.__clear()
        super(BattleRoyaleController, self).onDisconnected()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        super(BattleRoyaleController, self).onAccountBecomePlayer()

    def onAvatarBecomePlayer(self):
        self.__clear()
        if self.__sessionProvider.arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
            self.__voControl.activate()
        else:
            self.__voControl.deactivate()
        self.__voControl.onAvatarBecomePlayer()
        super(BattleRoyaleController, self).onAvatarBecomePlayer()

    def getCurrentSubModeID(self):
        return self.__currentSubModeID

    def setCurrentSubModeID(self, currentSubModeID, updateNeeded=True):
        if currentSubModeID not in BattleRoyaleSubMode.ALL_RANGE:
            currentSubModeID = BattleRoyaleSubMode.SOLO_MODE_ID
        self.__currentSubModeID = currentSubModeID
        if updateNeeded:
            self.onSubModeUpdated()

    def selectSubModeBattle(self, selectedSubModeID, **kwargs):
        extData = {SUB_MODE_ID_KEY: selectedSubModeID}
        self.__selectRoyaleBattle(extData=extData, **kwargs)

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().battleRoyale

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def getEndTime(self):
        return self.getCurrentSeason().getCycleEndDate()

    def getStartTime(self):
        return self.getCurrentSeason().getCycleStartDate()

    def getTimeLeftTillCycleEnd(self):
        timeLeft = 0
        currentCycleInfo = self.getCurrentCycleInfo()
        if currentCycleInfo[1]:
            timeLeft = time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(currentCycleInfo[0]))
        return timeLeft

    def getPerformanceGroup(self):
        if not self.__performanceGroup:
            self.__analyzeClientSystem()
            _logger.debug('Current performance group %s', self.__performanceGroup)
        return self.__performanceGroup

    def getVehicleShells(self, vehicleName):
        vehicleType = vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByName(vehicleName))
        vehicle = self.__itemsCache.items.getItemByCD(vehicleType.compactDescr)
        return [ (shell, vehicle.gun.maxAmmo * self.__equipmentCount.get(AmmoTypes.BASIC_SHELL if ShellParams(shell.descriptor, vehicle.descriptor).isBasic else AmmoTypes.PREMIUM_SHELL, 0)) for shell in vehicle.shells.installed ]

    def getVehicleEquipment(self, vehicleName):
        vehiclesSlotsConfig = self.getModeSettings().vehiclesSlotsConfig
        if vehicleName not in vehiclesSlotsConfig:
            _logger.error("Get equipment for vehicle '%r' failed. Vehicle not found in config. Slots config %s", vehicleName, vehiclesSlotsConfig)
            return []
        return [ (vehicles.g_cache.equipments()[eqId], self.__equipmentCount.get(chargeId, 0)) for chargeId, eqId in sorted(vehiclesSlotsConfig[vehicleName].items(), key=lambda s: s[0]) ]

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

    def isActive(self):
        _, isCycleActive = self.getCurrentCycleInfo()
        return self.isEnabled() and self.getCurrentSeason() is not None and isCycleActive

    def isBattleRoyaleMode(self):
        if self.prbDispatcher is None:
            return False
        else:
            state = self.prbDispatcher.getFunctionalState()
            return self.__isBattleRoyaleMode(state) or self.__isBattleRoyaleTournamentMode(state)

    def getModeState(self):
        return _PERIOD_INFO_TO_MOD_STATE[self.getPeriodInfo().periodType]

    def __isBattleRoyaleMode(self, state):
        return state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE) or state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)

    def __isBattleRoyaleTournamentMode(self, state):
        return state.isInPreQueue(queueType=QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT) or state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT)

    def isBattlePassAvailable(self, bonusType):
        battlePassConfig = self.__lobbyContext.getServerSettings().getBattlePassConfig()
        return battlePassConfig.isEnabled() and battlePassConfig.isGameModeEnabled(bonusType)

    def isInBattleRoyaleSquad(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.BATTLE_ROYALE)
        else:
            return False

    def isInRandomSquadSubMode(self):
        return self.getCurrentSubModeID() == BattleRoyaleSubMode.SOLO_DYNAMIC_MODE_ID

    def selectRoyaleBattle(self):
        if not self.isEnabled():
            return
        self.__selectRoyaleBattle()

    def openInfoPageWindow(self, isModeSelector=False):
        showInfoPage(isModeSelector)

    def setDefaultHangarEntryPoint(self):
        if self.__battleRoyaleTournamentController.isSelected():
            self.__battleRoyaleTournamentController.leaveBattleRoyaleTournament(isChangingToBattleRoyaleHangar=True)

    def isGeneralHangarEntryPoint(self):
        return not self.__battleRoyaleTournamentController.isSelected()

    def selectRandomBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__callbackID = BigWorld.callback(0, partial(self.__doSelectRandomPrb, dispatcher))
            return

    def getPlayerLevelInfo(self):
        return self.__itemsCache.items.battleRoyale.accTitle

    def getStats(self):
        return self.__itemsCache.items.battleRoyale

    @staticmethod
    @dependency.replace_none_kwargs(guiLoader=IGuiLoader)
    def showIntroWindow(ctx=None, parent=None, guiLoader=None):
        from battle_royale.gui.impl.lobby.views.intro_view import IntroWindow
        from gui.shared.utils.HangarSpace import g_execute_after_hangar_space_inited

        @g_execute_after_hangar_space_inited
        def load(guiLoader):
            view = guiLoader.windowsManager.getViewByLayoutID(R.views.battle_royale.lobby.views.IntroView())
            if view is None:
                window = IntroWindow(ctx or {}, parent or getParentWindow())
                window.load()
            return

        load(guiLoader)

    def getQuests(self):
        _, isCycleActive = self.getCurrentCycleInfo()
        return {k:v for k, v in self.__eventsCache.getQuests().items() if v.getGroupID() == BATTLE_ROYALE_GROUPS_ID and self.__tokenIsValid(v)} if self.isGeneralHangarEntryPoint() and isCycleActive else {}

    def isDailyQuestsRefreshAvailable(self):
        if self.hasPrimeTimesLeftForCurrentCycle():
            return True
        serversPeriodsMapping = self.getPrimeTimesForDay(time_utils.getCurrentLocalServerTimestamp())
        periods = []
        for _, dayPeriods in serversPeriodsMapping.items():
            periods.append(max([ periodEnd for _, periodEnd in dayPeriods ]))

        if periods:
            periodTimeLeft = max(periods) - time_utils.getCurrentLocalServerTimestamp()
            return periodTimeLeft > time_utils.getDayTimeLeft()
        return False

    def showIntroVideo(self, alias, force=False):
        introVideoUrl = self.__getIntroVideoURL()
        if not introVideoUrl:
            return
        else:
            season = self.getCurrentSeason()
            if season is None:
                return
            if not force:
                if not self.isBattleRoyaleMode():
                    return
                if self.getModeState() == BattleRoyaleModeState.Regular and not SelectorBattleTypesUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE):
                    SelectorBattleTypesUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE)
                storedSeasonID = AccountSettings.getSettings(ROYALE_INTRO_VIDEO_SHOWN_FOR_SEASON)
                if season.getSeasonID() == storedSeasonID:
                    return
            AccountSettings.setSettings(ROYALE_INTRO_VIDEO_SHOWN_FOR_SEASON, season.getSeasonID())
            showBrowserOverlayView(introVideoUrl, alias or VIEW_ALIAS.BROWSER_OVERLAY, forcedSkipEscape=True)
            return

    def getProgressionPointsTableData(self):
        gameModes = sorted(self.__progressionPointsConfig().keys())
        gameModeLists = []
        for gameMode in gameModes:
            gameModeLists.append(self.__getProgressionPointsPerPlace(gameMode))

        return (gameModes, gameModeLists)

    def getTournamentBannerData(self):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        for bannerData in self.getModeSettings().tournamentsWidget.get('widgets', []):
            if bannerData['startDate'] <= currentTime < bannerData['endDate']:
                return bannerData

        return None

    @property
    def isTournamentBannerEnabled(self):
        if self.__isTournamentBannerEnabled is None:
            self.__isTournamentBannerEnabled = self.__getTournamentBannerAvailability()
        return self.__isTournamentBannerEnabled

    def __getIntroVideoURL(self):
        if not hasattr(GUI_SETTINGS, 'battleRoyaleVideo'):
            return None
        else:
            introVideoUrl = GUI_SETTINGS.battleRoyaleVideo.get('introVideo')
            return GUI_SETTINGS.checkAndReplaceWebBridgeMacros(introVideoUrl) if introVideoUrl else introVideoUrl

    def __progressionPointsConfig(self):
        return self.__battleRoyaleSettings.progressionTokenAward

    def __getProgressionPointsPerPlace(self, gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO):
        pointsList = self.__progressionPointsConfig().get(gameMode, [])
        if not pointsList:
            return []
        pointList = [ (key, len(list(group))) for key, group in groupby(zip(*pointsList)[1]) ]
        result = []
        count = 0
        for points, pointsCount in pointList:
            count += pointsCount
            result.append(BattleRoyaleProgressionPoints(count, points))

        return result

    def __selectRoyaleBattle(self, extData=None, **kwargs):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            isSquad = extData and extData.get(SUB_MODE_ID_KEY, BattleRoyaleSubMode.SOLO_MODE_ID) == BattleRoyaleSubMode.SQUAD_MODE_ID
            self.__doSelectBattleRoyalePrb(dispatcher, isSquad=isSquad, extData=extData, **kwargs)
            return

    def __selectBattleRoyaleTournament(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectBattleRoyaleTournamentPrb(dispatcher)
            return

    def __serverSettingsChangeBrowserHandler(self, browser, diff):
        if not diff.get(Configs.BATTLE_ROYALE_CONFIG.value, {}).get('isEnabled'):
            browser.onCloseView()

    def _createSeason(self, cycleInfo, seasonData):
        return BattleRoyaleSeason(cycleInfo, seasonData)

    def __eventAvailabilityUpdate(self, *_):
        if g_prbLoader.getDispatcher() is None:
            return
        elif self.__battleRoyaleTournamentController.isSelected():
            return
        else:
            battleRoyaleEnabled = self.isEnabled() and self.getCurrentSeason() is not None
            isSelectRandom = not battleRoyaleEnabled and self.isBattleRoyaleMode()
            if battleRoyaleEnabled and not self.isActive():
                currTime = time_utils.getCurrentLocalServerTimestamp()
                cycle = self.getCurrentSeason().getNextByTimeCycle(currTime)
                isSelectRandom = cycle is None
            if isSelectRandom:
                self.selectRandomBattle()
            return

    def __onCheckSceneChange(self):
        if self.isBattleRoyaleMode():
            self.__enableRoyaleMode()
            self.__spaceSwitchController.hangarSpaceUpdate(BATTLE_ROYALE_SCENE)
        elif self.__isBRLogicEnabled:
            self.__disableRoyaleMode()

    def __enableRoyaleMode(self):
        self.__isBRLogicEnabled = True
        royaleVehicleID = AccountSettings.getFavorites(ROYALE_VEHICLE)
        vehicle = self.__itemsCache.items.getVehicle(royaleVehicleID)
        if not royaleVehicleID or vehicle is None or not vehicle.isOnlyForBattleRoyaleBattles:
            criteria = REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE]) | REQ_CRITERIA.INVENTORY
            values = self.__itemsCache.items.getVehicles(criteria=criteria).values()
            royaleVehicle = first(sorted(values, key=lambda item: (GUI_NATIONS_ORDER_INDEX[item.nationName], VEHICLE_TYPES_ORDER_INDICES[item.type], item.userName)))
            if royaleVehicle:
                royaleVehicleID = royaleVehicle.invID
        if royaleVehicleID:
            g_currentVehicle.selectVehicle(royaleVehicleID)
        else:
            g_currentVehicle.selectNoVehicle()
        self.__voControl.activate()
        return

    def __disableRoyaleMode(self):
        self.__isBRLogicEnabled = False
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
            criteria |= ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        if storedVehInvID:
            g_currentVehicle.selectVehicle(storedVehInvID)
        else:
            g_currentVehicle.selectNoVehicle()
        self.__voControl.deactivate()

    @adisp_process
    def __doSelectBattleRoyaleTournamentPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE_TOURNAMENT))

    @adisp_process
    def __doSelectBattleRoyalePrb(self, dispatcher, isSquad=False, extData=None, accountsToInvite=None, **kwargs):
        actionName = PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD if isSquad else PREBATTLE_ACTION_NAME.BATTLE_ROYALE
        result = yield dispatcher.doSelectAction(PrbAction(actionName, accountsToInvite=accountsToInvite, extData=extData))
        if not result:
            self.onSubModeUpdated()

    @adisp_process
    def __doSelectRandomPrb(self, dispatcher):
        self.__callbackID = None
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        return

    @adisp_process
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

    @adisp_process
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

    def __timerTick(self):
        self.onStatusTick()

    def __timerNotifier(self):
        self.onEntryPointUpdated()
        if self.isBattleRoyaleMode():
            self.onWidgetUpdate()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()
        self.__timerNotifier()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = serverSettings
        self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
        self.__brProgression.setSettings(self.getModeSettings().eventProgression)
        self.__updateEquipmentCount()
        self.__serverSettings.onServerSettingsChange += self.__updateRoyaleSettings
        return

    def __updateRoyaleSettings(self, diff):
        if Configs.BATTLE_ROYALE_CONFIG.value not in diff:
            return
        else:
            self.__eventAvailabilityUpdate()
            self.__battleRoyaleSettings = self.__getBattleRoyaleSettings()
            self.__brProgression.setSettings(self.getModeSettings().eventProgression)
            self.__updateEquipmentCount()
            self.__updateTournamentBannerState()
            self.__divisions = None
            self.onUpdated()
            self.__resetTimer()
            return

    def __onChangeProfileAlias(self, event):
        if self.isBattleRoyaleMode() and BATTLE_ROYALE_STATS_ENABLED:
            event.ctx = {'selectedAlias': VIEW_ALIAS.PROFILE_STATISTICS}

    def __onProfileStatisticSelectBattlesType(self, event):
        if not BATTLE_ROYALE_STATS_ENABLED:
            return
        eventOwner = event.ctx.get('eventOwner')
        if eventOwner == 'battleRoyale':
            event.ctx['battlesType'] = PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO
        elif eventOwner and self.isBattleRoyaleMode() and not self.__profStatSelectBattlesTypeInited:
            event.ctx['battlesType'] = PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO
            self.__profStatSelectBattlesTypeInited = True

    def __onProfileStatisticDispose(self, event):
        if not BATTLE_ROYALE_STATS_ENABLED:
            return
        self.__profStatSelectBattlesTypeInited = False

    def __onProfileTechniqueSelectBattlesType(self, event):
        if not BATTLE_ROYALE_STATS_ENABLED:
            return
        eventOwner = event.ctx.get('eventOwner')
        if event.ctx.get('eventOwner') == 'battleRoyale':
            event.ctx['battlesType'] = PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO
        elif eventOwner and self.isBattleRoyaleMode() and not self.__profTechSelectBattlesTypeInited:
            event.ctx['battlesType'] = PROFILE_DROPDOWN_KEYS.BATTLE_ROYALE_SOLO
            self.__profTechSelectBattlesTypeInited = True

    def __onProfileTechniqueDispose(self, event):
        if not BATTLE_ROYALE_STATS_ENABLED:
            return
        self.__profTechSelectBattlesTypeInited = False

    @adisp_process
    def __onSelectVehicleInHangar(self, event):
        if not self.isBattleRoyaleMode():
            return
        vehicleInvID = event.ctx['vehicleInvID']
        prevVehicleInvID = event.ctx['prevVehicleInvID']
        vehicle = self.__itemsCache.items.getVehicle(vehicleInvID)
        if vehicle and not isBattleRoyale(vehicle.tags):
            dispatcher = g_prbLoader.getDispatcher()
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result and self.isEnabled():
                g_currentVehicle.selectVehicle(prevVehicleInvID)

    def __clear(self):
        self.stopNotification()
        self.__hangarsSpace.onVehicleChanged -= self.__onVehicleChanged
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.__battleRoyaleTournamentController.onSelectBattleRoyaleTournament -= self.__selectBattleRoyaleTournament
        g_eventBus.removeListener(ProfilePageEvent.SELECT_PROFILE_ALIAS, self.__onChangeProfileAlias, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ProfileStatisticEvent.SELECT_BATTLE_TYPE, self.__onProfileStatisticSelectBattlesType, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ProfileTechniqueEvent.SELECT_BATTLE_TYPE, self.__onProfileTechniqueSelectBattlesType, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ProfileStatisticEvent.DISPOSE, self.__onProfileStatisticDispose, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(ProfileTechniqueEvent.DISPOSE, self.__onProfileTechniqueDispose, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__defaultHangars = {}
        self.__balance = None
        self.__isTournamentBannerEnabled = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        return

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
        stats['graphicsEngine'] = getGraphicsEngineValue()
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

    def __onVehicleChanged(self):
        if self.__isNeedToUpdateHeroTank:
            self.__hangarsSpace.onHeroTankReady()
            self.__isNeedToUpdateHeroTank = False

    def __tokenIsValid(self, quest):
        tokens = quest.accountReqs.getTokens()
        return False if tokens and not tokens[0].isAvailable() else True

    def __updateTournamentBannerState(self):
        self.__isTournamentBannerEnabled = self.__getTournamentBannerAvailability()
        self.onTournamentBannerStateChanged()

    def __getTournamentBannerAvailability(self):
        return self.getModeSettings().tournamentsWidget['isWidgetEnabled'] and self.getTournamentBannerData() is not None

    def __getTournamentBannerTimerDelta(self):
        if self.getModeSettings().tournamentsWidget['isWidgetEnabled']:
            currentTime = time_utils.getCurrentLocalServerTimestamp()
            prevBannerData = None
            for bannerData in self.getModeSettings().tournamentsWidget.get('widgets', []):
                if currentTime < bannerData['startDate'] and prevBannerData:
                    if currentTime < prevBannerData['endDate'] < bannerData['startDate']:
                        startDate = prevBannerData['endDate']
                    else:
                        startDate = bannerData['startDate']
                    return max(0, startDate - time_utils.getCurrentLocalServerTimestamp())
                prevBannerData = bannerData

            if prevBannerData:
                return max(0, prevBannerData['endDate'] - time_utils.getCurrentLocalServerTimestamp())
        return 0
