# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/rts_battles_controller.py
import typing
import logging
import BigWorld
from adisp import process
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IS_RTS_COMMANDER, RTS_INTRO_PAGE_VISITED
from account_helpers.client_ai_rosters import getUnsuitableVehiclesCriteria
from constants import Configs, ARENA_BONUS_TYPE
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.rts_battles.rts_helpers import markRTSBootcampComplete, isRTSBootcampComplete
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.rts_battles.rts_constants import COMMANDER_INVITATION_MARGIN
from gui.rts_battles.rts_models import RTSAlertData, RTSRoster
from gui.rts_battles.sound_manager import RTSSoundManager
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.shared.events import ViewEventType
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.shared import event_dispatcher, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.Scaleform.genConsts.RTSBATTLES_ALIASES import RTSBATTLES_ALIASES
from helpers import dependency, time_utils
from PlayerEvents import g_playerEvents
from RTSShared import RTSBootcampMatchmakerState
from season_provider import SeasonProvider
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils import IHangarSpace
from web.web_client_api.rts_battles import createRTSBattlesWebHanlders
if typing.TYPE_CHECKING:
    from helpers.server_settings import RTSBattlesConfig
    from gui.shared.utils.requesters import RequestCriteria
_logger = logging.getLogger(__name__)

def _showSeparateWebView(url, alias):
    event_dispatcher.showBrowserOverlayView(url, alias=alias, webHandlers=createRTSBattlesWebHanlders())


class RTSBattlesController(IRTSBattlesController, Notifiable, SeasonProvider, IGlobalListener):
    _ALERT_DATA_CLASS = RTSAlertData
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(RTSBattlesController, self).__init__()
        self.__isRTSSoundMode = False
        self.__isCommander = False
        self.__roster = []
        self.__evtMgr = em = Event.EventManager()
        self.onUpdated = Event.Event(em)
        self.onRosterUpdated = Event.Event(em)
        self.onCommanderInvitation = Event.Event(em)
        self.onControlModeChanged = Event.Event(em)
        self.onGameModeChanged = Event.Event(em)
        self.onGameModeStatusTick = Event.Event(em)
        self.onGameModeStatusUpdated = Event.Event(em)
        self.onIsPrbActive = Event.Event(em)
        self.onRtsTutorialBannerUpdate = Event.Event(em)
        self.__serverSettings = None
        self.__rtsSettings = None
        self.__soundManager = RTSSoundManager()
        self.__tutorialBannerWindow = None
        self.__isBootcampResultDeserted = False
        self.__battleModeBeforeBootcamp = ARENA_BONUS_TYPE.UNKNOWN
        return

    def init(self):
        super(RTSBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(PeriodicNotifier(self.getTimer, self.__timerTick))
        g_playerEvents.onArenaCreated += self.__onArenaCreated

    def fini(self):
        self.__evtMgr.clear()
        self.clearNotification()
        g_playerEvents.onArenaCreated -= self.__onArenaCreated
        super(RTSBattlesController, self).fini()

    def getModeSettings(self):
        return self.getSettings()

    def onAvatarBecomePlayer(self):
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self._removeLobbyListeners()

    def onAccountBecomePlayer(self):
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateRtsSettings
            self.__serverSettings = None
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__soundManager.setIsFirstEntrance(True)
        return

    def onDisconnected(self):
        self.__clear()

    def onLobbyInited(self, *_):
        self.__isRTSSoundMode = False
        self.__roster = self.getRoster(self.getBattleMode())
        self.__updateSounds(self.isPrbActive())
        g_clientUpdateManager.addCallbacks({'aiRosters': self.__onUpdateRosters,
         'tokens': self.__onTokensUpdate})
        self.startNotification()
        self.startGlobalListening()
        self._addLobbyListeners()

    def onLobbyStarted(self, ctx):
        if self.isTankistEnabled():
            isCommander = AccountSettings.getSettings(IS_RTS_COMMANDER)
            self.changeControlMode(isCommander=isCommander)
        self.__hangarSpace.onSpaceCreate += self.updateRTSTutorialBanner

    def onPrbEntitySwitching(self):
        pass

    def onPrbEntitySwitched(self):
        isActive = self.isPrbActive()
        if isActive:
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.RTS)
            introPageSeen = AccountSettings.getNotifications(RTS_INTRO_PAGE_VISITED)
            if not introPageSeen:
                event_dispatcher.showRtsIntroPage()
            self.onUpdated()
            self.onGameModeChanged()
        else:
            default = AccountSettings.getSettingsDefault(IS_RTS_COMMANDER)
            AccountSettings.setSettings(IS_RTS_COMMANDER, default)
            self.__isCommander = default
        self.__updateSounds(isActive)
        self.onIsPrbActive(isActive)
        self.updateRTSTutorialBanner()

    @process
    def doSelectPrb(self, callback=None):
        if self.isPrbActive():
            if callback:
                callback()
            return
        else:
            navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
            if not navigationPossible:
                return
            rts1x7Enabled = self.isSubmodeEnabled(ARENA_BONUS_TYPE.RTS) and not self.isWarmup()
            actionName = PREBATTLE_ACTION_NAME.RTS if rts1x7Enabled else PREBATTLE_ACTION_NAME.RTS_1x1
            result = yield self.prbDispatcher.doSelectAction(PrbAction(actionName))
            if result and callback is not None:
                callback()
            return

    def onEnqueued(self, queueType, *args):
        self.updateRTSTutorialBanner()

    def onDequeued(self, queueType, *args):
        self.updateRTSTutorialBanner()

    def onEnqueueError(self, queueType, *args):
        self.updateRTSTutorialBanner()

    def onKickedFromQueue(self, queueType, *args):
        self.updateRTSTutorialBanner()

    def onArenaJoinFailure(self, queueType, *args):
        self.updateRTSTutorialBanner()

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isBattlesPossible(self):
        currentSeason = self.getCurrentSeason()
        return self.isEnabled() and self.isAnySubmodeAvailable() and currentSeason is not None and currentSeason.getCycleInfo() is not None

    def isAnySubmodeAvailable(self):
        rts1x7Enabled = self.isSubmodeEnabled(ARENA_BONUS_TYPE.RTS) and not self.isWarmup()
        rts1x1Enabled = self.isSubmodeEnabled(ARENA_BONUS_TYPE.RTS_1x1)
        return rts1x1Enabled or rts1x7Enabled

    def isCommander(self):
        return not self.isTankistEnabled() or self.__isCommander

    def isEnabled(self):
        return self.__rtsSettings.isEnabled

    def isSubmodeEnabled(self, bonusType):
        return self.__rtsSettings.isSubmodeEnabled(bonusType)

    def isTankistEnabled(self):
        return self.getBattleMode() == ARENA_BONUS_TYPE.RTS and not self.isWarmup()

    def isPrbActive(self):
        if self.prbEntity is None:
            return False
        else:
            modeFlags = self.prbEntity.getModeFlags()
            return bool(modeFlags & FUNCTIONAL_FLAG.RTS | modeFlags & FUNCTIONAL_FLAG.RTS_1x1 | modeFlags & FUNCTIONAL_FLAG.RTS_BOOTCAMP)

    def isWarmup(self):
        return self.__rtsSettings.isWarmupEnabled()

    def isVisible(self):
        return self.isEnabled() and self.getCurrentSeason() is not None

    def getBattleMode(self):
        if self.prbEntity is not None:
            modeFlags = self.prbEntity.getModeFlags()
            if bool(modeFlags & FUNCTIONAL_FLAG.RTS_BOOTCAMP):
                return ARENA_BONUS_TYPE.RTS_BOOTCAMP
            if bool(modeFlags & FUNCTIONAL_FLAG.RTS):
                return ARENA_BONUS_TYPE.RTS
            if bool(modeFlags & FUNCTIONAL_FLAG.RTS_1x1):
                return ARENA_BONUS_TYPE.RTS_1x1
        return ARENA_BONUS_TYPE.UNKNOWN

    def getCommanderInvitation(self, bonusType, includeMargin=True):
        expireAt, amount = self.__itemsCache.items.tokens.getTokenInfo(self.__rtsSettings.getInvitationTokenName(bonusType))
        margin = COMMANDER_INVITATION_MARGIN if includeMargin else 0
        now = time_utils.getCurrentLocalServerTimestamp()
        return (amount, now + margin < expireAt)

    def hasEnoughCurrency(self, bonusType):
        return self.getCurrency(bonusType) >= self.__rtsSettings.currencyAmountToBattle(bonusType)

    def getAlertBlock(self):
        alertData = self._getAlertBlockData()
        buttonCallback = event_dispatcher.showRtsPrimeTimeWindow
        return (buttonCallback, alertData or self._ALERT_DATA_CLASS(), alertData is not None)

    def getCurrency(self, bonusType):
        return self.__itemsCache.items.tokens.getTokenCount(self.__rtsSettings.getCurrencyTokenName(bonusType))

    def getRoster(self, bonusType):
        rawRoster = self.__itemsCache.items.aiRosters.getRosters().get(bonusType, {})
        return RTSRoster(rawRoster.get('vehicles', []), rawRoster.get('supplies', []), rawRoster.get('rtsManners', []))

    def getRosterConfig(self, bonusType):
        return self.__lobbyContext.getServerSettings().getAIRostersConfig().get(bonusType, {})

    def getSettings(self):
        return self.__rtsSettings

    def getSoundManager(self):
        return self.__soundManager

    def getUnsuitableRosterCriteria(self, bonusType):
        return getUnsuitableVehiclesCriteria(self.getRosterConfig(bonusType).get('vehicles', {}).get('bots', []))

    def getUnsuitableVehicleCriteria(self, bonusType):
        return getUnsuitableVehiclesCriteria([self.getSettings().getVehicleRestrictions(bonusType)])

    def getLockedEndDate(self):
        date = self.__rtsSettings.getWarmupPhaseEnd()
        return date if self.isWarmup() and date else 0

    def getBattleEconomics(self):
        bonusType = self.getBattleMode()
        if bonusType == ARENA_BONUS_TYPE.UNKNOWN:
            bonusType = ARENA_BONUS_TYPE.RTS
        return self.getSettings().getBattleEconomicsByBonusType(bonusType)

    def changeControlMode(self, isCommander):
        if self.__isCommander == isCommander:
            return
        if not self.isTankistEnabled():
            _logger.warning('RTSBattlesController: cannot switch control mode while submode is not 1x7')
            return
        self.__isCommander = isCommander
        AccountSettings.setSettings(IS_RTS_COMMANDER, self.__isCommander)
        self.onControlModeChanged(self.__isCommander)
        self.onRosterUpdated(self.__roster)
        self.onUpdated()
        self.updateRTSTutorialBanner()

    def runRTSQueue(self):
        self.prbDispatcher.doAction(PrbAction(actionName='', mmData=0))

    def enterRTSPrebattle(self):
        self.doSelectPrb()

    def hasSuitableVehicle(self):
        vehicleConfig = self.getSettings().getVehicleRestrictions(ARENA_BONUS_TYPE.RTS)
        allowedLevels = vehicleConfig.get('levels', frozenset())
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.LEVELS(allowedLevels)
        invVehicles = self.__itemsCache.items.getVehicles(criteria)
        return True if invVehicles else False

    @process
    def runRTSBootcamp(self):
        self.__battleModeBeforeBootcamp = self.getBattleMode()
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RTS_BOOTCAMP))

    @process
    def returnFromRTSBootcamp(self):
        if self.__isBootcampResultDeserted:
            self.__isBootcampResultDeserted = False
            event_dispatcher.showRTSBootcampResultDeserted()
        if self.__battleModeBeforeBootcamp == ARENA_BONUS_TYPE.RTS:
            actionName = PREBATTLE_ACTION_NAME.RTS
        else:
            actionName = PREBATTLE_ACTION_NAME.RTS_1x1
        if self.isTankistEnabled():
            self.changeControlMode(isCommander=True)
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))

    def showRTSInfoPage(self, alias=RTSBATTLES_ALIASES.RTS_BATTLES_INFO_PAGE):
        _showSeparateWebView(GUI_SETTINGS.rtsInfoPageURL, alias)

    def canShowRTSBootcampBanner(self):
        if self.getSettings().getRTSBootcampMatchmakerState() == RTSBootcampMatchmakerState.DISABLED:
            return False
        prbEntity = self.prbEntity
        if prbEntity is None or prbEntity.isInQueue():
            return False
        elif bool(prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RTS_BOOTCAMP):
            return False
        else:
            return False if isRTSBootcampComplete() else self.isPrbActive()

    def updateRTSTutorialBanner(self):
        self.onRtsTutorialBannerUpdate()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateRtsSettings
        self.__serverSettings = serverSettings
        self.__rtsSettings = self.__serverSettings.getRTSBattlesConfig()
        self.__serverSettings.onServerSettingsChange += self.__onUpdateRtsSettings
        return

    @property
    def bonusTypesWithCurrency(self):
        return (ARENA_BONUS_TYPE.RTS, ARENA_BONUS_TYPE.RTS_1x1)

    def setShowBootcampDeserted(self):
        self.__isBootcampResultDeserted = True

    def getAvailableCurrencies(self):
        return (self.__rtsSettings.getCurrencyTokenName(bonusType) for bonusType in self.bonusTypesWithCurrency) if self.__rtsSettings else (_ for _ in ())

    def __onTokensUpdate(self, diff):
        for name in self.getAvailableCurrencies():
            if name in diff:
                self.onUpdated()
                break

        if self.__rtsSettings.getInvitationTokenName(ARENA_BONUS_TYPE.RTS) in diff:
            self.onCommanderInvitation()

    def __onUpdateRosters(self, diff):
        for bonusType in ARENA_BONUS_TYPE.RTS_RANGE:
            if bonusType not in diff:
                continue
            newRoster = self.getRoster(bonusType)
            self.__roster = newRoster
            self.onRosterUpdated(newRoster)
            self.onUpdated()

    def __onUpdateRtsSettings(self, diff):
        if Configs.RTS_CONFIG.value in diff:
            self.__rtsSettings = self.__lobbyContext.getServerSettings().getRTSBattlesConfig()
            self.onUpdated()
            self.__resetTimers()
            self.updateRTSTutorialBanner()

    def __clear(self):
        if self.__tutorialBannerWindow is not None:
            self.__tutorialBannerWindow.destroy()
            self.__tutorialBannerWindow = None
        self.stopNotification()
        self.stopGlobalListening()
        self.__hangarSpace.onSpaceCreate -= self.updateRTSTutorialBanner
        self.__soundManager.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._removeLobbyListeners()
        return

    def __resetTimers(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onGameModeStatusUpdated(status)

    def __timerTick(self):
        self.onGameModeStatusTick()

    def __onArenaCreated(self):
        self.__updateSounds(False)

    def __updateSounds(self, isRTSSoundMode):
        if isRTSSoundMode != self.__isRTSSoundMode:
            self.__soundManager.onSoundModeChanged(isRTSSoundMode)
            self.__isRTSSoundMode = isRTSSoundMode

    def __onRoundFinished(self, winnerTeam, reason):
        playerAvatar = BigWorld.player()
        isRTSBootcamp = playerAvatar.arena.bonusType == ARENA_BONUS_TYPE.RTS_BOOTCAMP
        isWin = winnerTeam == playerAvatar.team
        if isRTSBootcamp and isWin:
            markRTSBootcampComplete(isComplete=True)

    def _addLobbyListeners(self):
        g_eventBus.addListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    def _removeLobbyListeners(self):
        g_eventBus.removeListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def __loadViewHandler(self, event):
        if not self.isPrbActive():
            return
        if event.alias != VIEW_ALIAS.LOBBY_HANGAR or not event.ctx.get('needToShowVehicle', False):
            return
        if self.isWarmup() and not self.isSubmodeEnabled(ARENA_BONUS_TYPE.RTS):
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
        else:
            if self.getBattleMode() != ARENA_BONUS_TYPE.RTS:
                yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RTS))
            self.changeControlMode(isCommander=False)

    def getEventEndTimestamp(self):
        if self.hasPrimeTimesLeftForCurrentCycle() or self.isInPrimeTime():
            currServerTime = time_utils.getCurrentLocalServerTimestamp()
            actualSeason = self.getCurrentSeason() or self.getNextSeason()
            actualCycle = actualSeason.getCycleInfo() or actualSeason.getNextCycleInfo(currServerTime)
            lastPrimeTimeEnd = max([ period[1] for primeTime in self.getPrimeTimes().values() for period in primeTime.getPeriodsBetween(int(currServerTime), actualCycle.endDate, True) ])
            return lastPrimeTimeEnd
        else:
            return None
