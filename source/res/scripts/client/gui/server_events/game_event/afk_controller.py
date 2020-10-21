# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/afk_controller.py
import logging
from collections import namedtuple
import adisp
import gui.shared
from Event import Event, EventManager
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from constants import HE19_AFK_PERSONAL_QUEST_ID
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.base.ctx import PrbAction, LeavePrbAction
from gui.prb_control.entities.base.listener import IPrbListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.server_events.game_event import ifGameEventDisabled
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.afk_controller import IAFKController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class AFKController(CallbackDelayer, IAFKController, IPrbListener):
    eventsCache = dependency.descriptor(IEventsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    __AFKToken = namedtuple('AFKToken', ('tokenID', 'count', 'expiryTime'))
    __SHOW_WINDOW_DELAY = 2

    def __init__(self):
        self.__lobbyInited = False
        self.__eventsManager = EventManager()
        self.onBanUpdated = Event(self.__eventsManager)
        super(AFKController, self).__init__()

    def init(self):
        gui.shared.g_eventBus.addListener(gui.shared.events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)

    def fini(self):
        self.__lobbyInited = False
        g_clientUpdateManager.removeObjectCallbacks(self)
        gui.shared.g_eventBus.removeListener(gui.shared.events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__onLobbyInited)
        self.destroy()

    @property
    def isBanned(self):
        return bool(self.__banToken.count)

    @property
    def banExpiryTime(self):
        return self.__banToken.expiryTime

    @adisp.process
    def showWarningWindow(self):
        from gui.Scaleform.daapi.view.dialogs.event_afk_dialog import EventAFKDialogMetaData
        yield DialogsInterface.showDialog(EventAFKDialogMetaData(EventAFKDialogMetaData.AFTER_BATTLE_WARNING))

    @adisp.process
    def showBanWindow(self):
        from gui.Scaleform.daapi.view.dialogs.event_afk_dialog import EventAFKDialogMetaData
        shouldShowQuest = yield DialogsInterface.showDialog(EventAFKDialogMetaData(EventAFKDialogMetaData.BAN_MESSAGE))
        if not shouldShowQuest:
            return
        shouldLeavePrb = yield self.prbDispatcher.doLeaveAction(LeavePrbAction())
        if shouldLeavePrb:
            self.showQuest()

    def questFilter(self, quest):
        return quest is not self.__AFKPersonalQuest or self.isBanned

    def showQuest(self):
        if self.isBanned and not self.__isInQueue:
            quest = self.__AFKPersonalQuest
            if quest:
                from gui.server_events.events_dispatcher import showMissions
                self.__doSelectAction(PREBATTLE_ACTION_NAME.RANDOM)
                return showMissions(tab=QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, missionID=quest.getID(), groupID=quest.getGroupID())
        SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKError)

    @property
    def __AFKPersonalQuest(self):
        return first(self.eventsCache.getQuests(lambda x: x.getID() == HE19_AFK_PERSONAL_QUEST_ID).itervalues(), None)

    AFKPersonalQuest = __AFKPersonalQuest

    def __onLobbyInited(self, _):
        self.__lobbyInited = True
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        self.delayCallback(self.__SHOW_WINDOW_DELAY, self.__showBan)
        self.delayCallback(self.__SHOW_WINDOW_DELAY, self.__showWarning)

    @adisp.process
    def __doSelectAction(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))

    @prbEntityProperty
    def __prbEntity(self):
        return None

    @property
    def __isInQueue(self):
        return self.__prbEntity and self.__prbEntity.isInQueue()

    @property
    def __hasWarning(self):
        return not self.isBanned and self.__violationToken.count >= self.__violationsTillWarning

    @ifGameEventDisabled()
    def __onTokensUpdate(self, diff):
        if diff.get(self.__banToken.tokenID):
            self.__showBan()
            self.onBanUpdated()
        elif self.__banToken.tokenID in diff:
            self.__banIsShown = False
            self.onBanUpdated()
        if diff.get(self.__violationToken.tokenID):
            self.__showWarning()
        elif self.__violationToken.tokenID in diff:
            self.__warningIsShown = False

    @ifGameEventDisabled()
    def __showBan(self):
        if self.isBanned:
            if not self.__banIsShown:
                if self.__lobbyInited and not self.__isInQueue:
                    self.stopCallback(self.__showBan)
                    self.showBanWindow()
                    from gui.Scaleform.daapi.view.lobby.event_boards.formaters import formatTimeAndDate
                    SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKBan, messageData={'pardonDate': formatTimeAndDate(self.banExpiryTime)})
                    self.__banIsShown = True
                    self.__warningIsShown = False
                    questName = self.__AFKPersonalQuest.getUserName()
                    SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKQuest, messageData={'questName': text_styles.hightlight(backport.text(R.strings.system_messages.event.afk.quest.questName(), questName=questName))})
                else:
                    self.delayCallback(self.__SHOW_WINDOW_DELAY, self.__showBan)
        else:
            self.__banIsShown = False

    @ifGameEventDisabled()
    def __showWarning(self):
        if self.__hasWarning:
            if not self.__warningIsShown:
                if self.__lobbyInited and not self.__isInQueue:
                    self.stopCallback(self.__showWarning)
                    self.showWarningWindow()
                    SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKWarning)
                    self.__banIsShown = False
                    self.__warningIsShown = True
                else:
                    self.delayCallback(self.__SHOW_WINDOW_DELAY, self.__showWarning)
        else:
            self.__warningIsShown = False

    @property
    def __afkConfig(self):
        return self.eventsCache.getGameEventData().get('afkConfig', {})

    @property
    def __violationsTillWarning(self):
        return self.__afkConfig.get('violationsTillWarning', 1)

    def __getAfkToken(self, tokenType):
        config = self.__afkConfig.get('tokens', {}).get(tokenType)
        if config:
            return self.__AFKToken(config['id'], self.eventsCache.questsProgress.getTokenCount(config['id']), self.eventsCache.questsProgress.getTokenExpiryTime(config['id']))
        else:
            _logger.error('Wrong token type %s', tokenType)
            return self.__AFKToken(None, 0, 0)

    @property
    def __banToken(self):
        return self.__getAfkToken('ban')

    @property
    def __violationToken(self):
        return self.__getAfkToken('violation')

    @property
    def __pardonOrderToken(self):
        return self.__getAfkToken('pardonOrder')

    pardonOrderToken = __pardonOrderToken

    def __setBanIsShown(self, value):
        if bool(value) != self.__banIsShown:
            self.__setGameEventServerSetting(UIGameEventKeys.AFK_BAN_SHOWN, int(value))
            if not value:
                if self.__pardonOrderToken.count:
                    SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKUnbanByQuest)
                else:
                    SystemMessages.pushMessage('', type=SystemMessages.SM_TYPE.EventAFKUnban)

    def __getBanIsShown(self):
        return bool(self.__getGameEventServerSetting(UIGameEventKeys.AFK_BAN_SHOWN, 0))

    __banIsShown = property(__getBanIsShown, __setBanIsShown)

    def __setWarningIsShown(self, value):
        if bool(value) != self.__warningIsShown:
            self.__setGameEventServerSetting(UIGameEventKeys.AFK_WARNING_SHOWN, int(value))

    def __getWarningIsShown(self):
        return bool(self.__getGameEventServerSetting(UIGameEventKeys.AFK_WARNING_SHOWN, 0))

    __warningIsShown = property(__getWarningIsShown, __setWarningIsShown)

    def __getGameEventServerSetting(self, key, default=None):
        value = self.settingsCore.serverSettings.getGameEventStorage().get(key)
        return value or default

    def __setGameEventServerSetting(self, key, value):
        self.settingsCore.serverSettings.saveInGameEventStorage({key: value})
