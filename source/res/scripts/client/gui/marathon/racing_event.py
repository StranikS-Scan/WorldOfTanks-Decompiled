# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/racing_event.py
from functools import partial
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import MARATHON_REWARD_WAS_SHOWN_PREFIX
from adisp import async, process
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.framework.managers.view_lifecycle_watcher import ViewLifecycleWatcher, IViewLifecycleHandler
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.game_control.links import URLMacros
from gui.game_control.racing_event_lobby_sounds import RacingEventLobbySounds
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_constants import MARATHON_STATE
from gui.marathon.marathon_event_dp import MarathonEvent
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from items.components.festival_constants import FEST_CONFIG
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IRacingEventController
from skeletons.gui.lobby_context import ILobbyContext
RACING_BASE_TOKEN = 'fest19:race:'
PERSONAL_PROGRESS_AWARD_TOKEN = RACING_BASE_TOKEN + 'personalProgressReward:5'
COLLECTION_AWARD_BASE_TOKEN = RACING_BASE_TOKEN + 'collection_reward:'
COLLECTION_AWARD_COUNT = 3
TOURNAMENT_STAGE_COUNT = 5
COLLECTION_AWARD_TOKENS = [ COLLECTION_AWARD_BASE_TOKEN + str(num) for num in range(1, COLLECTION_AWARD_COUNT + 1) ]
TOURNAMENT_END_FAKE_TOKEN = RACING_BASE_TOKEN + 'tournament:end'
TOURNAMENT_STAGE_END_FAKE_BASE_TOKEN = 'tournament:stage:end:'
TOURNAMENT_STAGE_END_FAKE_TOKEN = RACING_BASE_TOKEN + TOURNAMENT_STAGE_END_FAKE_BASE_TOKEN
TOURNAMENT_STAGE_END_FAKE_TOKENS = [ TOURNAMENT_STAGE_END_FAKE_TOKEN + str(num) for num in range(1, TOURNAMENT_STAGE_COUNT + 1) ]
AWARD_TOKENS = COLLECTION_AWARD_TOKENS + TOURNAMENT_STAGE_END_FAKE_TOKENS + [TOURNAMENT_END_FAKE_TOKEN, PERSONAL_PROGRESS_AWARD_TOKEN]

class RacingEventAddPath(object):
    EMPTY_PATH = ''
    PROGRESS = 'progress'
    INFO = 'info'
    COLLECTION = 'collection'
    PERSONAL_AWARD = 'personalAward'
    TOURNAMENT_FINISHED = 'tournamentFinished'
    TOURNAMENT_STAGE_FINISHED = 'tournamentStageFinished'


RACING_EVENT_TOKEN_TO_AWARD_URL_MAP = {PERSONAL_PROGRESS_AWARD_TOKEN: RacingEventAddPath.PERSONAL_AWARD,
 TOURNAMENT_END_FAKE_TOKEN: RacingEventAddPath.TOURNAMENT_FINISHED}
RACING_EVENT_TOKEN_TO_AWARD_URL_MAP.update({token:RacingEventAddPath.COLLECTION for token in COLLECTION_AWARD_TOKENS})
RACING_EVENT_TOKEN_TO_AWARD_URL_MAP.update({token:RacingEventAddPath.TOURNAMENT_STAGE_FINISHED for token in TOURNAMENT_STAGE_END_FAKE_TOKENS})

class _RacingAwardScreenHandler(IViewLifecycleHandler):
    __VIEWS = (VIEW_ALIAS.RACING_AWARD_VIEW,)

    def __init__(self, onAwardScreenDestroyedCallback):
        super(_RacingAwardScreenHandler, self).__init__([ ViewKey(alias) for alias in self.__VIEWS ])
        self.__onAwardScreenDestroyedCallback = onAwardScreenDestroyedCallback

    def onViewDestroyed(self, view):
        if view.destroyedByWeb:
            self.__onAwardScreenDestroyedCallback()


class RacingEvent(MarathonEvent):
    RACING_MARATHON_PREFIX = 'racing_event_'
    _RACING_EVENT_SECTION = 'racingEvent'
    __racingEventController = dependency.descriptor(IRacingEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _COOLDOWN_UPDATE_TIMEOUT = 1

    def __init__(self):
        super(RacingEvent, self).__init__()
        self.onDataChanged = Event.Event()
        self.__secondsNotifier = None
        self.__additionalPath = RacingEventAddPath.EMPTY_PATH
        self.__additionalParams = RacingEventAddPath.EMPTY_PATH
        self.__urlMacros = URLMacros()
        self.__urlDict = GUI_SETTINGS.lookup(self.urlDictName)
        self.__viewLifecycleWatcher = ViewLifecycleWatcher()
        return

    @property
    def prefix(self):
        return self.RACING_MARATHON_PREFIX

    @property
    def tokenPrefix(self):
        return RACING_BASE_TOKEN

    @property
    def urlDictName(self):
        return RacingEvent._RACING_EVENT_SECTION

    @property
    def label(self):
        return R.strings.quests.missions.tab.label.racingEvent()

    @property
    def tabTooltip(self):
        return QUESTS.MISSIONS_TAB_RACINGEVENT

    @property
    def tabTooltipDisabled(self):
        return QUESTS.MISSIONS_TAB_RACINGEVENT

    @property
    def flagTooltipAlias(self):
        return TOOLTIPS_CONSTANTS.RACE_WIDGET

    @property
    def flagEnabledTooltipType(self):
        return TOOLTIPS_CONSTANTS.WULF

    @property
    def awardTokens(self):
        return AWARD_TOKENS

    def playSoundsOnEnterTab(self):
        RacingEventLobbySounds.playRacingMetaGameOn()

    def playSoundsOnExitTab(self):
        RacingEventLobbySounds.playRacingMetaGameOff()
        RacingEventLobbySounds.playRacingCollectionOff()
        self.__racingEventController.playRacingEventLobbySound()

    def init(self):
        super(RacingEvent, self).init()
        self.__racingEventController.onNumRacingAttemptsChanged += self.onDataChanged
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app is not None and app.containerManager is not None:
            self.__viewLifecycleWatcher.start(app.containerManager, [_RacingAwardScreenHandler(self.showRewardScreen)])
        self.__secondsNotifier = PeriodicNotifier(self.__getNotificationDelta, self.onDataChanged, (self._COOLDOWN_UPDATE_TIMEOUT,))
        self.__secondsNotifier.startNotification()
        self.__additionalPath = RacingEventAddPath.EMPTY_PATH
        self.__additionalParams = RacingEventAddPath.EMPTY_PATH
        return

    def fini(self):
        super(RacingEvent, self).fini()
        if self.__secondsNotifier is not None:
            self.__secondsNotifier.stopNotification()
            self.__secondsNotifier.clear()
        self.__racingEventController.onNumRacingAttemptsChanged -= self.onDataChanged
        return

    def getHangarFlag(self, state=None):
        if state == MARATHON_STATE.NOT_STARTED:
            return backport.image(R.images.gui.maps.icons.library.hangarFlag.racing_flag_default())
        return backport.image(R.images.gui.maps.icons.library.hangarFlag.racing_flag_available()) if not self.__racingEventController.isCooldown() else backport.image(R.images.gui.maps.icons.library.hangarFlag.racing_flag_cooldown())

    def doesShowRewardVideo(self):
        return False

    def doesShowMissionsTab(self):
        return self.isAvailable()

    def getMarathonFlagState(self, vehicle):
        flagState = super(RacingEvent, self).getMarathonFlagState(vehicle)
        flagState.update({'flagStateText': self.__getHangarFlagStateText(self.getState())})
        return flagState

    def setAdditionalPath(self, additionalPath, params=''):
        self.__additionalPath = additionalPath
        if params:
            self.__additionalParams = params

    @async
    @process
    def getUrl(self, callback):
        url = None
        if self.__urlDict is None:
            LOG_ERROR('Requesting URL for marathon when URL dict is not specified')
            yield lambda clb: clb(None)
        url = yield self.__urlMacros.parse(self.__getUrl())
        callback(url)
        return

    def showRewardScreen(self):
        if not self.doesShowRewardScreen():
            return
        if not self._awardsReceived.empty():
            priority, tokenName = self._awardsReceived.get()
            if not AccountSettings.getUIFlag(self._getRewardShownMarkKey(MARATHON_REWARD_WAS_SHOWN_PREFIX, awardPostfix=tokenName)):
                self.__additionalPath = RACING_EVENT_TOKEN_TO_AWARD_URL_MAP.get(tokenName, RacingEventAddPath.EMPTY_PATH)
                self.__additionalParams = self.__getParams(tokenName)
                showBrowserOverlayView(self.__getUrl(), alias=VIEW_ALIAS.RACING_AWARD_VIEW, callbackOnLoad=partial(self._setScreenWasShown, key=MARATHON_REWARD_WAS_SHOWN_PREFIX, awardPostFix=tokenName))

    def createMarathonWebHandlers(self):
        from gui.marathon.web_handlers import createRacingEventWebHandlers
        return createRacingEventWebHandlers()

    def __getUrl(self):
        baseUrl = self.__lobbyContext.getServerSettings().getFestivalConfig().get(FEST_CONFIG.RACING_EVENT_URL, RacingEventAddPath.EMPTY_PATH)
        relativeUrl = RacingEventAddPath.EMPTY_PATH
        if self.__additionalPath:
            relativeUrl = self.__urlDict.get(self.__additionalPath) + self.__additionalParams
        self.__additionalPath = self.__additionalParams = RacingEventAddPath.EMPTY_PATH
        return baseUrl + relativeUrl

    def __getParams(self, tokenName):
        if COLLECTION_AWARD_BASE_TOKEN in tokenName or TOURNAMENT_STAGE_END_FAKE_BASE_TOKEN in tokenName:
            tokenParts = tokenName.split(':')
            lastPart = tokenParts[-1] if tokenParts else None
            collectionOrStageNumber = lastPart if lastPart is not None else ''
            return collectionOrStageNumber
        else:
            return RacingEventAddPath.EMPTY_PATH

    def __getFormattedFlagTooltipBody(self):
        vehicleText = text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.vehicle()))
        bodyText = backport.text(R.strings.tooltips.festivalMarathon.body(), levels=text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.levels())), vehicle=vehicleText, style=text_styles.stats(backport.text(R.strings.tooltips.festivalMarathon.body.style(), vehicle=vehicleText)))
        return bodyText

    def __getHangarFlagStateText(self, state):
        if state == MARATHON_STATE.SUSPENDED:
            return backport.text(R.strings.tooltips.marathon.flag.state.suspend())
        if state == MARATHON_STATE.NOT_STARTED:
            return ''
        racingCtrl = self.__racingEventController
        if racingCtrl.isCooldown():
            countdown = racingCtrl.getCooldownCountdown()
            stateText = time_utils.getTillTimeString(countdown, '#festival:race/hangar/status/timeLeft')
        else:
            stateText = ''.join((str(racingCtrl.getNumRacingAttempts()), '/', str(racingCtrl.getMaxNumRacingAttempts())))
        return stateText

    def __getNotificationDelta(self):
        return self._COOLDOWN_UPDATE_TIMEOUT
