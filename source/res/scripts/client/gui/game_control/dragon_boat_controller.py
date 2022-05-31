# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/dragon_boat_controller.py
import logging
import typing
import BigWorld
from Event import EventManager, Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DBOAT_WIDGET_SHOW, DBOAT_INTRO_SCREEN_SHOWN
from account_helpers.settings_core.settings_constants import DragonBoatStorageKeys
from adisp import async, process
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS, SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader.decorators import sf_lobby
from gui.game_control.links import URLMacros
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, isPlayerAccount
from shared_utils import CONST_CONTAINER, safeCancelCallback
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.game_control import IDragonBoatController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from helpers.server_settings import _DragonBoatConfig
_logger = logging.getLogger(__name__)
DBOAT_PREFIX = 'dboat:'
DBOAT_DAILY_QUEST = 'dboat:daily'
DBOAT_WEEKLY_QUEST = 'dboat:weekly'
DBOAT_FINAL_REWARD = 'dboat:final_reward'
DBOAT_GET_FINAL_REWARD = 'dboat:final_reward:get'
DBOAT_REGISTRATION = 'registration'
DBOAT_REWARDS = 'rewards'
DBOAT_POINTS = 'dboat:points'
DBOAT_QUEST_SELECTED = 'dboat:quest:selected'
_ADDITIONAL_LOAD_WAIT = 0.1

class DragonBoatState(CONST_CONTAINER):
    NOT_STARTED = 0
    STARTED = 1
    FINISHED = 2
    ENDED = 3


class DragonBoatController(IDragonBoatController):
    eventsCache = dependency.descriptor(IEventsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        super(DragonBoatController, self).__init__()
        self.__isLobbyInited = False
        self.__isInHangar = False
        self.__processFinalReward = False
        self.__tokens = None
        self.__teamTokens = None
        self.__finalRewardAvailable = None
        self.__finalQuest = None
        self.__activePlayer = None
        self.__completedQuests = None
        self.__lastEventState = None
        self.__screenLoadCB = None
        self.__serverSettings = None
        self.__urlMacros = URLMacros()
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onStatusUpdated = Event(self.__em)
        self.onWidgetStateChanged = Event(self.__em)
        return

    @sf_lobby
    def app(self):
        pass

    def fini(self):
        self.__clear()
        self.__em.clear()
        super(DragonBoatController, self).fini()

    def onDisconnected(self):
        super(DragonBoatController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(DragonBoatController, self).onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(DragonBoatController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.lobbyContext.getServerSettings())

    def onLobbyInited(self, event):
        if not isPlayerAccount():
            return
        self.__isLobbyInited = True

    def onLobbyStarted(self, ctx):
        super(DragonBoatController, self).onLobbyStarted(ctx)
        self.__initConfig()
        self.eventsCache.onSyncCompleted += self.__onSyncCompleted
        self.eventsCache.onProgressUpdated += self.__onSyncCompleted
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.__onSyncCompleted()

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.isEnabled() and self.getConfig().isActive

    def getConfig(self):
        return self.lobbyContext.getServerSettings().dragonBoatConfig

    def getDragonBoatQuests(self):
        return self.eventsCache.getHiddenQuests(self.__filterFunc)

    def getState(self):
        if self.__finalRewardAvailable & self.__completedQuests and self.__activePlayer & self.__tokens:
            if not self.__finalQuest & self.__completedQuests:
                return DragonBoatState.ENDED
        teamNumber = self.getTeam()
        if self.__teamTokens & self.__tokens and not teamNumber and self.__needToShowFinishScreen():
            return DragonBoatState.FINISHED
        return DragonBoatState.STARTED if teamNumber else DragonBoatState.NOT_STARTED

    def getTeam(self):
        teamTokens = self.getConfig().dragonBoatTokens.get('activeParticipant')
        return self.itemsCache.items.tokens.getTokenCount(teamTokens[0]) if teamTokens else 0

    def getDailyQuestName(self):
        dqTokens = set(self.getConfig().dragonBoatTokens.get('dailyBattleMissions'))
        dqToken = dqTokens & self.__tokens
        if dqToken:
            dqToken = str(next(iter(dqToken))).split(':')[-1]
            if dqToken.isdigit():
                return 'dboat:daily:{}'.format(dqToken)
        return None

    @async
    @process
    def getUrl(self, urlName=None, callback=lambda *args: None):
        url = yield self.__urlMacros.parse(self._getUrl(urlName))
        callback(url)

    def createWebHandlers(self):
        from gui.impl.lobby.dragon_boat.dragon_boat_web_handlers import createDragonBoatWebHandlers
        return createDragonBoatWebHandlers()

    def isNeedHandlingEscape(self):
        return True

    def processFinalReward(self):
        dbStorage = dict()
        if self.settingsCore.isReady and self.settingsCache.isSynced():
            dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
        finalRewardObtained = dbStorage.get(DragonBoatStorageKeys.DBOAT_FINAL_REWARD_OBTAINED)
        if self.isEnabled() and isPlayerAccount() and self.getState() == DragonBoatState.ENDED and finalRewardObtained is not None and not finalRewardObtained:
            self.__processFinalReward = True
            BigWorld.player().requestSingleToken(DBOAT_GET_FINAL_REWARD)
        return

    def checkWidgetState(self):
        dbStorage = dict()
        if self.settingsCore.isReady and self.settingsCache.isSynced():
            dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
        finalRewardObtained = dbStorage.get(DragonBoatStorageKeys.DBOAT_FINAL_REWARD_OBTAINED)
        if finalRewardObtained is not None and finalRewardObtained:
            AccountSettings.setSettings(DBOAT_WIDGET_SHOW, False)
        if self.__finalRewardAvailable & self.__completedQuests and not self.__activePlayer & self.__tokens:
            AccountSettings.setSettings(DBOAT_WIDGET_SHOW, False)
        self.onWidgetStateChanged()
        return

    def checkFinishScreenToShow(self):
        if self.__finalRewardAvailable & self.__completedQuests:
            return 0
        else:
            completedQ = self.__getCompletedQuests()
            dbStorage = dict()
            if self.settingsCore.isReady and self.settingsCache.isSynced():
                dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
            teamPattern = 'team{}'
            lastTeamRewardQ = self.getConfig().dragonBoatQuests.get('lastTeamReward', [])
            for qName in lastTeamRewardQ:
                if qName in completedQ:
                    teamId = qName.split(':')[1]
                    if teamId and teamId.isdigit():
                        team = teamPattern.format(teamId)
                        screenShown = dbStorage.get(team)
                        if screenShown is not None and not screenShown:
                            return teamId

            return 0

    def showFinishScreen(self, team):
        from gui.shared.event_dispatcher import showDragonBoatFinishTeamdWindow
        if team:
            teamPattern = 'team{}'
            if self.settingsCore.isReady and self.settingsCache.isSynced():
                self.settingsCore.serverSettings.saveInDragonBoatStorage({teamPattern.format(team): True})
                showDragonBoatFinishTeamdWindow(team=team)

    def isDayQuestCompleted(self):
        return DBOAT_QUEST_SELECTED in self.__tokens and self.getDailyQuestName() is None

    def isFinalRewardInProcess(self):
        return self.__screenLoadCB is not None or self.__processFinalReward

    def getLastDayOfEvent(self):
        return self.getConfig().endTime

    def _getUrl(self, urlName=None):
        baseUrl = self.getConfig().dragonBoatUrl
        return baseUrl if urlName is None else baseUrl + GUI_SETTINGS.dragonBoat.get(urlName, '')

    def __initConfig(self):
        self.__tokens = set(self.itemsCache.items.tokens.getTokens().keys())
        self.__teamTokens = set(self.getConfig().dragonBoatTokens.get('registration'))
        self.__finalRewardAvailable = set(self.getConfig().dragonBoatQuests.get('finalRewardAvailable'))
        self.__finalQuest = set(self.getConfig().dragonBoatQuests.get('finalReward'))
        self.__activePlayer = set(self.getConfig().dragonBoatTokens.get('activePlayer'))
        self.__completedQuests = set(self.__getCompletedQuests())
        self.__updateLastEventState()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__initConfig()
        self.onSettingsChanged()
        return

    def __updateEventBattlesSettings(self, diff):
        if 'dragon_boat_config' in diff:
            self.__initConfig()
            self.onSettingsChanged()

    def __clear(self):
        self.__cancelCallback()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        return

    def __onSyncCompleted(self, *args):
        self.__initConfig()
        if not self.isAvailable():
            return
        else:
            if self.__finalRewardAvailable & self.__completedQuests:
                AccountSettings.setSettings(DBOAT_INTRO_SCREEN_SHOWN, True)
            dbStorage = dict()
            if self.settingsCore.isReady and self.settingsCache.isSynced():
                dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
            finalRewardObtained = dbStorage.get(DragonBoatStorageKeys.DBOAT_FINAL_REWARD_OBTAINED)
            if finalRewardObtained is not None and not finalRewardObtained and self.__finalRewardAvailable & self.__completedQuests and self.__activePlayer & self.__tokens and self.__finalQuest & self.__completedQuests:
                AccountSettings.setSettings(DBOAT_WIDGET_SHOW, False)
                self.__processFinalReward = True
                self.__tryShowScreen(self.__showRewardScreen)
            if self.__finalRewardAvailable & self.__completedQuests:
                self.checkWidgetState()
            return

    def __onViewLoaded(self, pyView, _):
        if self.__isLobbyInited:
            if pyView.alias == VIEW_ALIAS.LOBBY_HANGAR:
                self.__isInHangar = True
            elif pyView.layer == WindowLayer.SUB_VIEW:
                self.__isInHangar = False

    def __tryShowScreen(self, screenFunc):
        if self.__screenLoadCB is not None:
            return
        else:
            self.__screenLoadCB = BigWorld.callback(0.1, screenFunc)
            return

    def __showRewardScreen(self):
        self.__cancelCallback()
        if self.__isLobbyInited and self.__isInHangar:
            from gui.shared.event_dispatcher import showDragonBoatFinalRewardWindow
            showDragonBoatFinalRewardWindow()
            self.onWidgetStateChanged()
            self.__processFinalReward = False
            return
        self.__screenLoadCB = BigWorld.callback(_ADDITIONAL_LOAD_WAIT, self.__showRewardScreen)

    def __cancelCallback(self):
        if self.__screenLoadCB is not None:
            safeCancelCallback(self.__screenLoadCB)
            self.__screenLoadCB = None
        return

    def __updateLastEventState(self):
        if self.__lastEventState is not None:
            if self.getConfig().isActive != self.__lastEventState and self.isEnabled():
                self.__lastEventState = self.getConfig().isActive
                if self.__lastEventState:
                    SystemMessages.pushI18nMessage('#system_messages:dragonBoat/restored', type=SystemMessages.SM_TYPE.WarningHeader, messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.priorityMessageTitle())})
                else:
                    SystemMessages.pushI18nMessage('#system_messages:dragonBoat/paused', type=SystemMessages.SM_TYPE.WarningHeader, messageData={'header': backport.text(R.strings.messenger.serviceChannelMessages.priorityMessageTitle())})
        else:
            self.__lastEventState = self.getConfig().isActive
        return

    def __getCompletedQuests(self):
        return [ q.getID() for q in self.getDragonBoatQuests().itervalues() if q.isCompleted() ]

    def __needToShowFinishScreen(self):
        dbStorage = dict()
        if self.settingsCore.isReady and self.settingsCache.isSynced():
            dbStorage = self.settingsCore.serverSettings.getDragonBoatStorage()
        finishQuestPostfix = ':finish'
        finishedQuest = [ qName for qName in self.__completedQuests if qName.endswith(finishQuestPostfix) ]
        shownFinishedScreens = 0
        for k, v in dbStorage.iteritems():
            if k.startswith('team'):
                shownFinishedScreens += int(v)

        return shownFinishedScreens < len(finishedQuest)

    @classmethod
    def __filterFunc(cls, quest):
        return quest.getID().startswith(DBOAT_PREFIX)
