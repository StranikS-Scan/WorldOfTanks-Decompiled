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
from account_helpers.AccountSettings import ROYALE_VEHICLE, CURRENT_VEHICLE, ROYALE_INTRO_VIDEO_SHOWN
from account_helpers.settings_core.settings_constants import GRAPHICS
from adisp import adisp_process
from battle_royale.gui.constants import AmmoTypes, BattleRoyalePerfProblems
from battle_royale.gui.game_control.br_vo_controller import BRVoiceOverController
from battle_royale.gui.royale_models import BattleRoyaleSeason
from constants import QUEUE_TYPE, Configs, PREBATTLE_TYPE, ARENA_BONUS_TYPE, BATTLE_ROYALE_SCENE
from gui import GUI_NATIONS_ORDER_INDEX
from gui import GUI_SETTINGS
from gui.ClientHangarSpace import SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from gui.Scaleform.genConsts.PROFILE_DROPDOWN_KEYS import PROFILE_DROPDOWN_KEYS
from gui.game_control.links import URLMacros
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.server_events.events_constants import BATTLE_ROYALE_GROUPS_ID
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import getParentWindow, showBrowserOverlayView
from gui.shared.events import ProfilePageEvent, ProfileStatisticEvent, ProfileTechniqueEvent
from gui.shared.gui_items.Tankman import TankmanSkill
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, VEHICLE_TYPES_ORDER_INDICES
from gui.shared.utils import SelectorBattleTypesUtils
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from helpers import dependency, time_utils
from helpers.statistics import HARDWARE_SCORE_PARAMS
from items.battle_royale import isBattleRoyale
from shared_utils import first
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IEventsNotificationsController, IBootcampController, IHangarSpaceSwitchController, IBattleRoyaleController, IBattleRoyaleTournamentController, IBRProgressionOnTokensController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from stats_params import BATTLE_ROYALE_STATS_ENABLED
if typing.TYPE_CHECKING:
    from helpers.server_settings import BattleRoyaleConfig
_logger = logging.getLogger(__name__)
BattleRoyaleProgressionPoints = namedtuple('BattleRoyaleProgressionPoints', ['lastInRange', 'points'])

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
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)
    __bootcamp = dependency.descriptor(IBootcampController)
    __brProgression = dependency.descriptor(IBRProgressionOnTokensController)
    TOKEN_QUEST_ID = 'token:br:title:'
    MAX_STORED_ARENAS_RESULTS = 20

    def __init__(self):
        super(BattleRoyaleController, self).__init__()
        self.onUpdated = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onWidgetUpdate = Event.Event()
        self.__clientValuesInited = False
        self.__clientShields = {}
        self.__performanceGroup = None
        self.__serverSettings = None
        self.__battleRoyaleSettings = None
        self.__wasInLobby = False
        self.__equipmentCount = {}
        self.__equipmentSlots = tuple()
        self.__isBRLogicEnabled = False
        self.__voControl = None
        self.__defaultHangars = {}
        self.__urlMacros = None
        self.__isNeedToUpdateHeroTank = False
        self.__profileStatisticWasSelected = False
        self.__profStatSelectBattlesTypeInited = False
        self.__profTechSelectBattlesTypeInited = False
        self.__callbackID = None
        return

    def init(self):
        super(BattleRoyaleController, self).init()
        self.__voControl = BRVoiceOverController()
        self.__voControl.init()
        self.__urlMacros = URLMacros()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))
        self.__spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange

    def getTimer(self, now=None, peripheryID=None):
        now = now or self._getNow()
        primeTimeStatus, timeLeft, _ = self.getPrimeTimeStatus(now, peripheryID)
        if primeTimeStatus != PrimeTimeStatus.AVAILABLE:
            for pID in self._getAllPeripheryIDs():
                peripheryStatus, peripheryTime, _ = self.getPrimeTimeStatus(now, pID)
                if peripheryStatus in (PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE):
                    timeLeft = peripheryTime
                    break

        seasonsChangeTime = self.getClosestStateChangeTime(now)
        if seasonsChangeTime and (now + timeLeft > seasonsChangeTime or timeLeft == 0):
            timeLeft = seasonsChangeTime - now
        return timeLeft + 1 if timeLeft > 0 else 0

    def fini(self):
        self.__voControl.fini()
        self.__voControl = None
        self.__equipmentCount = None
        self.__defaultHangars = None
        self.__urlMacros = None
        self.onUpdated.clear()
        self.onPrimeTimeStatusUpdated.clear()
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.clearNotification()
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
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
        self.__wasInLobby = True
        nextTick(self.__eventAvailabilityUpdate)()

    def onPrbEntitySwitched(self):
        self.__modeEntered()

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
        super(BattleRoyaleController, self).onAccountBecomePlayer()

    def onAvatarBecomePlayer(self):
        self.__clear()
        if self.__sessionProvider.arenaVisitor.getArenaBonusType() in ARENA_BONUS_TYPE.BATTLE_ROYALE_RANGE:
            self.__voControl.activate()
        else:
            self.__voControl.deactivate()
        self.__voControl.onAvatarBecomePlayer()
        super(BattleRoyaleController, self).onAvatarBecomePlayer()

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().battleRoyale

    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def isShowTimeLeft(self):
        return self.getModeSettings().isShowTimeLeft

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
    def _getFullLearnedSkill(skillName):
        return TankmanSkill(skillName, skillLevel=100)

    def getBrCommanderSkills(self):
        ignoredSkillNames = ('commander_sixthSense',)
        result = [ self._getFullLearnedSkill(skillName) for skillName in ignoredSkillNames ]
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            for _, tankman in vehicle.crew:
                if tankman is not None:
                    skills = (skill for skill in tankman.skills if skill.name not in ignoredSkillNames)
                    for skill in skills:
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

    def selectRoyaleBattle(self):
        if not self.isEnabled():
            return
        self.__selectRoyaleBattle()

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

    @adisp_process
    def openURL(self, url=None):
        requestUrl = url or self.__battleRoyaleSettings.url
        if requestUrl:
            parsedUrl = yield self.__urlMacros.parse(requestUrl)
            if parsedUrl:
                self.__showBrowserView(parsedUrl)

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

    def getIntroVideoURL(self):
        if not hasattr(GUI_SETTINGS, 'battleRoyaleVideo'):
            return None
        else:
            introVideoUrl = GUI_SETTINGS.battleRoyaleVideo.get('introVideo')
            return GUI_SETTINGS.checkAndReplaceWebBridgeMacros(introVideoUrl) if introVideoUrl else introVideoUrl

    def getProgressionPointsTableData(self):
        gameModes = sorted(self.__progressionPointsConfig().keys())
        gameModeLists = []
        for gameMode in gameModes:
            gameModeLists.append(self.__getProgressionPointsPerPlace(gameMode))

        return (gameModes, gameModeLists)

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

    def __modeEntered(self):
        if not self.isBattleRoyaleMode():
            return
        if not SelectorBattleTypesUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE):
            SelectorBattleTypesUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.BATTLE_ROYALE)
        introVideoUrl = self.getIntroVideoURL()
        if AccountSettings.getSettings(ROYALE_INTRO_VIDEO_SHOWN) or not introVideoUrl:
            return
        AccountSettings.setSettings(ROYALE_INTRO_VIDEO_SHOWN, True)
        showBrowserOverlayView(introVideoUrl, VIEW_ALIAS.BROWSER_OVERLAY, forcedSkipEscape=True)

    def __selectRoyaleBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectBattleRoyalePrb(dispatcher)
            return

    def __selectBattleRoyaleTournament(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectBattleRoyaleTournamentPrb(dispatcher)
            return

    def __showBrowserView(self, url):
        showBrowserOverlayView(url, alias=BATTLEROYALE_ALIASES.BATTLE_ROYALE_BROWSER_VIEW)

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
        elif not self.__bootcamp.isInBootcamp() and self.__isBRLogicEnabled:
            self.__disableRoyaleMode()

    def __enableRoyaleMode(self):
        self.__isBRLogicEnabled = True
        royaleVehicleID = AccountSettings.getFavorites(ROYALE_VEHICLE)
        if not royaleVehicleID or self.__itemsCache.items.getVehicle(royaleVehicleID) is None:
            criteria = REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE]) | REQ_CRITERIA.INVENTORY
            vehicles = self.__itemsCache.items.getVehicles
            values = vehicles(criteria=criteria).values()
            royaleVehicle = first(sorted(values, key=lambda item: (item.isRented,
             GUI_NATIONS_ORDER_INDEX[item.nationName],
             VEHICLE_TYPES_ORDER_INDICES[item.type],
             item.userName)))
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
    def __doSelectBattleRoyalePrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.BATTLE_ROYALE))

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
        self.onWidgetUpdate()

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

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
        self.stopGlobalListening()
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
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __clearClientValues(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRoyaleSettings
        self.__serverSettings = None
        self.__clientValuesInited = False
        self.__profileStatisticWasSelected = False
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

    def __onVehicleChanged(self):
        if self.__isNeedToUpdateHeroTank:
            self.__hangarsSpace.onHeroTankReady()
            self.__isNeedToUpdateHeroTank = False

    def __tokenIsValid(self, quest):
        tokens = quest.accountReqs.getTokens()
        return False if tokens and not tokens[0].isAvailable() else True
