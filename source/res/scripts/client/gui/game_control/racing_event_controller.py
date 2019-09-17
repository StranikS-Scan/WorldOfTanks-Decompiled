# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/racing_event_controller.py
import logging
import Event
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from account_helpers.AccountSettings import RACING_EVENT_SM_SHOWED, RACING_REGISTRATION_SM_SHOWED, RACING_TEAM_CHANGED_SM_SHOWED
from binary_collection import BinarySetCollection
from gui import SystemMessages
from gui.Scaleform.locale.FESTIVAL import FESTIVAL
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.notifications import NotificationPriorityLevel
from gui.game_control.racing_event_lobby_sounds import RacingEventLobbySounds
from helpers import dependency, time_utils
from items.components.festival_constants import FEST_CONFIG
from messenger.m_constants import SCH_CLIENT_MSG_TYPE, PROTO_TYPE
from messenger.proto import proto_getter
from racing_event_config import RacingTeams, RACING_TEAM_BY_TOKEN_NAME, RaceTokens
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.utils.scheduled_notifications import Notifiable
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IRacingEventController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_REGISTRATION_STEP_NAME = 'RaceRegistration'
_RACE_REASON_STEP_NAME = 'RaceReason'

class RacingEventController(IRacingEventController, Notifiable):
    _battleResultsService = dependency.descriptor(IBattleResultsService)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RacingEventController, self).__init__()
        self.__isVehSwitching = False
        self.__serverSettings = None
        self.__raceEventSettings = None
        self.__isRacingEventEnabled = None
        self.__isRegistrationEnabled = None
        self.__isEventModeOn = None
        self.__racingTeam = RacingTeams.OUT_OF_TEAM
        self.__numRacingAttempts = None
        self.__maxNumRaceAttempts = -1
        self.onSettingsChanged = Event.Event()
        self.onEventModeChanged = Event.Event()
        self.onRacingTeamChanged = Event.Event()
        self.onNumRacingAttemptsChanged = Event.Event()
        self.onCooldownStateChanged = Event.Event()
        self.onMaxNumRacingAttemptsChanged = Event.Event()
        self.onRacingEventTriggerChanged = Event.Event()
        return

    def fini(self):
        self.onEventModeChanged.clear()
        self.onSettingsChanged.clear()
        self.onRacingTeamChanged.clear()
        self.onNumRacingAttemptsChanged.clear()
        self.onCooldownStateChanged.clear()
        self.onMaxNumRacingAttemptsChanged.clear()
        self.onRacingEventTriggerChanged.clear()
        super(RacingEventController, self).fini()

    def onDisconnected(self):
        self.__clear(True)
        super(RacingEventController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self.__clear(False)
        super(RacingEventController, self).onAvatarBecomePlayer()

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self._lobbyContext.getServerSettings())
        super(RacingEventController, self).onAccountBecomePlayer()

    def onLobbyInited(self, ctx):
        super(RacingEventController, self).onLobbyInited(ctx)
        self.__initData()
        self._eventsCache.onSyncCompleted += self.__onEventsCacheSyncCompleted
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_currentVehicle.onChangeStarted += self.__onCurrentVehicleChangeStarted
        self.startNotification()

    def onFightButtonClicked(self):
        if self.isEventModeOn():
            RacingEventLobbySounds.playRaceButtonClicked()

    def isEnabled(self):
        return bool(self._eventsCache.getEventBattles().enabled)

    def isRegistrationEnabled(self):
        return self.__getRegistrationEnabling()

    def getRaceCollectionInfo(self):
        raceCollections = self._itemsCache.items.festivity.getRaceCollections()
        hasItems = sum((BinarySetCollection(collection).itemsNum() for collection in raceCollections))
        raceInfo = self._lobbyContext.getServerSettings().getFestivalConfig()[FEST_CONFIG.RACE_COLLECTION_INFO]
        return (hasItems, raceInfo[0] * raceInfo[1])

    def isEventModeOn(self):
        return self.isEnabled() and self.__getEventModeOn()

    def isReadyForEventBattle(self):
        return not self.isCooldown()

    def getRacingTeam(self):
        return self.__racingTeam

    def getMaxNumRacingAttempts(self):
        if self.__maxNumRaceAttempts == -1:
            self.__maxNumRaceAttempts = self.__getMaxNumRacingAttempts()
        return self.__maxNumRaceAttempts

    def getNumRacingAttempts(self):
        return self.__getNumRacingAttempts()

    def isCooldown(self):
        return self.getNumRacingAttempts() == 0

    def getCooldownCountdown(self):
        cooldownTime = self._itemsCache.items.festivity.getRaceCooldown()
        cooldownCountdown = cooldownTime - time_utils.getServerUTCTime()
        cooldownCountdown = max(cooldownCountdown, 0)
        return cooldownCountdown

    @proto_getter(PROTO_TYPE.BW)
    def proto(self):
        return None

    def playRacingEventLobbySound(self):
        if self.isEventModeOn():
            RacingEventLobbySounds.playEventModeOn()
        else:
            RacingEventLobbySounds.playEventModeOff()

    def __getNumRacingAttempts(self):
        progress = self._eventsCache.questsProgress
        tokenNums = progress.getTokenCount(RaceTokens.RACE_ATTEMPT_TOKEN)
        return tokenNums

    def __getRacingTeam(self):
        progress = self._eventsCache.questsProgress
        for teamToken in RaceTokens.RACE_TEAM_TOKENS:
            if progress.getTokenCount(teamToken):
                return RACING_TEAM_BY_TOKEN_NAME[teamToken]

        return RacingTeams.OUT_OF_TEAM

    def __getRacingEventSettings(self):
        settings = self.__serverSettings.getRaceEventConfig()
        return settings

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRacingEventSettings
        self.__serverSettings = serverSettings
        self.__raceEventSettings = self.__getRacingEventSettings()
        self.__serverSettings.onServerSettingsChange += self.__updateRacingEventSettings
        return

    def __updateRacingEventSettings(self, diff):
        if 'festival_config' in diff:
            festConfig = diff['festival_config']
            if 'festival_race' in festConfig:
                self.__raceEventSettings = self.__getRacingEventSettings()
                self.onSettingsChanged()

    def __clear(self, clearData):
        self.__isVehSwitching = False
        if clearData:
            self.__isEventModeOn = None
            self.__racingTeam = RacingTeams.OUT_OF_TEAM
            self.__isRacingEventEnabled = None
            self.__isRegistrationEnabled = None
            self.__numRacingAttempts = None
            self.__maxNumRaceAttempts = -1
        self.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._eventsCache.onSyncCompleted -= self.__onEventsCacheSyncCompleted
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_currentVehicle.onChangeStarted -= self.__onCurrentVehicleChangeStarted
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateRacingEventSettings
        self.__serverSettings = None
        return

    def __initData(self):
        self.__onEventsCacheSyncCompleted()

    def __onCurrentVehicleChangeStarted(self):
        self.__isVehSwitching = True

    def __onCurrentVehicleChanged(self):
        if self.__isVehSwitching:
            self.__updateEventModeState()
        self.__isVehSwitching = False

    def __updateEventModeState(self):
        if g_currentVehicle.isPresent():
            isEventModeOn = self.isEventModeOn()
            if isEventModeOn != self.__isEventModeOn:
                self.__isEventModeOn = isEventModeOn
                self.onEventModeChanged(self.__isEventModeOn)

    def __getEventModeOn(self):
        return g_currentVehicle.item.isOnlyForEventBattles if g_currentVehicle.isPresent() else False

    def __onEventsCacheSyncCompleted(self, *_):
        currentRacingTeam = self.__getRacingTeam()
        if currentRacingTeam != self.__racingTeam:
            self.__racingTeam = currentRacingTeam
            self.onRacingTeamChanged(self.__racingTeam)
            self.__handleRacingTeamChangedNotification()
        currentNumRacingAttempts = self.__getNumRacingAttempts()
        if currentNumRacingAttempts != self.__numRacingAttempts:
            initFlag = self.__numRacingAttempts
            self.__numRacingAttempts = currentNumRacingAttempts
            self.onNumRacingAttemptsChanged(currentNumRacingAttempts)
            if self.__numRacingAttempts == self.__getMaxNumRacingAttempts() and initFlag is not None:
                self.onCooldownStateChanged(False)
                RacingEventLobbySounds.playCooldownOff()
                self.__handleRacingCooldownNotification(False)
            elif self.__numRacingAttempts == 0 and initFlag is not None:
                self.onCooldownStateChanged(True)
                self.__handleRacingCooldownNotification(True)
        maxNumRaceAttempts = self.__getMaxNumRacingAttempts()
        if maxNumRaceAttempts != self.__maxNumRaceAttempts:
            self.__maxNumRaceAttempts = maxNumRaceAttempts
            self.onMaxNumRacingAttemptsChanged(maxNumRaceAttempts)
        isRacingEventEnabled = self.isEnabled()
        if isRacingEventEnabled != self.__isRacingEventEnabled:
            self.__isRacingEventEnabled = isRacingEventEnabled
            self.onRacingEventTriggerChanged(isRacingEventEnabled)
            self.__updateEventModeState()
        isRegistrationEnabled = self.__getRegistrationEnabling()
        if isRegistrationEnabled != self.__isRegistrationEnabled:
            self.__isRegistrationEnabled = isRegistrationEnabled
        self.__handleTriggerNotifications()
        return

    def __getMaxNumRacingAttempts(self):
        quest = self._eventsCache.getHiddenQuests().get(RaceTokens.RACE_RESTORE_ATTEMPTS_TOKEN)
        if quest is not None:
            bonuses = quest.getBonuses('tokens')
            for bonus in bonuses:
                token = bonus.getTokens().get(RaceTokens.RACE_ATTEMPT_TOKEN)
                if token is not None:
                    return token.limit

        _logger.warning('Can not get max number of racing attempts')
        return -1

    def __getRegistrationEnabling(self):
        actions = self._eventsCache.getActions()
        for action in actions.itervalues():
            steps = action.getData()['steps']
            if steps is None:
                continue
            for step in steps:
                if step.get('name') != _REGISTRATION_STEP_NAME:
                    continue
                return bool(int(step.get('params', {}).get('enabled', '0')))

        return False

    def __getTriggerReason(self, stepName):
        actions = self._eventsCache.getActions()
        for action in actions.itervalues():
            steps = action.getData()['steps']
            if steps is None:
                continue
            for step in steps:
                if step.get('name') != stepName:
                    continue
                return int(step.get('params', {}).get('reason', '0'))

        return 0

    def __handleTriggerNotifications(self):
        triggerConfigs = {'registration': (_REGISTRATION_STEP_NAME, RACING_REGISTRATION_SM_SHOWED),
         'event': (_RACE_REASON_STEP_NAME, RACING_EVENT_SM_SHOWED)}
        for triggerName, config in triggerConfigs.iteritems():
            stepName, accSetting = config
            shownFlags = list(AccountSettings.getSettings(accSetting))
            reason = self.__getTriggerReason(stepName)
            if not shownFlags[reason - 1] and reason != 0:
                self.__updateRacingToogleAccSettings(reason, accSetting)
                self.proto.serviceChannel.pushClientMessage({'stateName': triggerName,
                 'state': reason}, SCH_CLIENT_MSG_TYPE.RACING_EVENT_STATE)

    def __handleRacingCooldownNotification(self, isCooldownStart):
        if isCooldownStart:
            header = backport.text(R.strings.festival.race.cooldown_start_notification.header())
            countdown = self.getCooldownCountdown()
            countdownStr = time_utils.getTillTimeString(countdown, FESTIVAL.RACE_HANGAR_STATUS_TIMELEFTEXT, removeLeadingZeros=True, removeLeadingZerosSeconds=True)
            message = backport.text(R.strings.festival.race.cooldown_start_notification.message(), time=text_styles.credits(countdownStr))
        else:
            header = backport.text(R.strings.festival.race.cooldown_stop_notification.header())
            message = backport.text(R.strings.festival.race.cooldown_stop_notification.message(), races=text_styles.credits(self.getNumRacingAttempts()))
        SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.RacingNotification, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': header,
         'text': message})

    @staticmethod
    def __updateRacingToogleAccSettings(reason, settingsKey):
        shownFlags = [False] * 4
        shownFlags[reason - 1] = True
        AccountSettings.setSettings(settingsKey, tuple(shownFlags))

    def __handleRacingTeamChangedNotification(self):
        team = self.__racingTeam
        if not AccountSettings.getSettings(RACING_TEAM_CHANGED_SM_SHOWED) and team != RacingTeams.OUT_OF_TEAM:
            teamStr = backport.text(R.strings.festival.race.racingTeam.num(team)())
            commanderInfo = R.strings.festival.race.hangar.commanderSlot.pilot.num(team)
            commander = (backport.text(commanderInfo.firstName()), backport.text(commanderInfo.secondName()))
            commander = ' '.join(commander)
            header = backport.text(R.strings.festival.serviceChannelMessages.racingEvent.registrationSuccess.title())
            message = backport.text(R.strings.festival.serviceChannelMessages.racingEvent.registrationSuccess.message(), team=text_styles.credits(teamStr), commander=text_styles.credits(commander))
            SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.RacingNotification, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': header,
             'text': message})
            AccountSettings.setSettings(RACING_TEAM_CHANGED_SM_SHOWED, True)
