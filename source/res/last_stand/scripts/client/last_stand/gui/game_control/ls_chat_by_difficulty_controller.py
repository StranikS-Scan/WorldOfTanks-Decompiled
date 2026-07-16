# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_chat_by_difficulty_controller.py
from __future__ import absolute_import
from future.utils import viewitems, viewvalues
import gui.shared
from constants import Configs
from debug_utils import LOG_ERROR
from gui.app_loader import sf_lobby
from gui.shared.utils.functions import getViewName
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent, GUICommonEvent
from gui.prb_control.entities.listener import IGlobalListener
from last_stand.gui import ls_account_settings
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.ls_gui_constants import DifficultyLevel, LAZY_CHANNEL
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_global_chat_controller import ILSDifficultyChatController
from helpers import dependency
from messenger.ext.channel_num_gen import getClientID4LazyChannel, getOrder4LazyChannel
from gui.prb_control.events_dispatcher import _defCarouselItemCtx
from gui.Scaleform.framework.managers.containers import VIEW_SEARCH_CRITERIA
from messenger.gui.Scaleform.data.ChannelsCarouselHandler import ChannelFindCriteria
from messenger.gui.events_dispatcher import showLazyChannelWindow
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.inject import channelsCtrlProperty
from frameworks.wulf import WindowLayer
from skeletons.gui.lobby_context import ILobbyContext

class LSDifficultyChatController(ILSDifficultyChatController, IGlobalListener):
    lsCtrl = dependency.descriptor(ILSController)
    lsDifficultyCtrl = dependency.descriptor(IDifficultyLevelController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    SYS_CHANNELS_PARAM_KEY = Configs.SYSTEM_CHANNELS.value

    def __init__(self):
        self.__clientIDs = {DifficultyLevel.EASY: (LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_EASY, getClientID4LazyChannel(LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_EASY)),
         DifficultyLevel.MEDIUM: (LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_MEDIUM, getClientID4LazyChannel(LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_MEDIUM)),
         DifficultyLevel.HARD: (LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_HARD, getClientID4LazyChannel(LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL_HARD))}
        for lazyChannel, clientID in viewvalues(self.__clientIDs):
            if not clientID:
                LOG_ERROR('Channel didn/t find. Channel={channel}'.format(channel=lazyChannel))

        self.__handlers = [ (ChannelFindCriteria(clientID), WindowLayer.WINDOW) for _, clientID in viewvalues(self.__clientIDs) ]
        self.__isShown = {DifficultyLevel.EASY: False,
         DifficultyLevel.MEDIUM: False,
         DifficultyLevel.HARD: False}

    @sf_lobby
    def app(self):
        return None

    @channelsCtrlProperty
    def channelsCtrl(self):
        return None

    def fini(self):
        self.__clear()
        super(LSDifficultyChatController, self).fini()

    def onDisconnected(self):
        super(LSDifficultyChatController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(LSDifficultyChatController, self).onAvatarBecomePlayer()
        self.__clear()

    def onLobbyInited(self, event):
        super(LSDifficultyChatController, self).onLobbyInited(event)
        self.startGlobalListening()
        self.lsCtrl.onSettingsUpdate += self._update
        self.lsDifficultyCtrl.onChangeDifficultyLevel += self._update
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        g_eventBus.addListener(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        self._update()

    def onPrbEntitySwitched(self):
        self._update()

    def isEnabled(self):
        return self.lsCtrl.isAvailable() and self.isChatEnabled() and not self.isAllChatsDisabled()

    def isAllChatsDisabled(self):
        return self.lobbyContext.getServerSettings().getSettings()[self.SYS_CHANNELS_PARAM_KEY]['disableAllChats']

    def isChatEnabled(self):
        sysChannelConfig = self.lobbyContext.getServerSettings().getSettings()[self.SYS_CHANNELS_PARAM_KEY]
        difficulty = self.lsDifficultyCtrl.getSelectedLevel()
        lazyChannel, _ = self.__clientIDs.get(difficulty, (None, None))
        return False if not lazyChannel else sysChannelConfig.get('sysChannelsConfig', {}).get(lazyChannel, False)

    def removeChannels(self):
        for difficulty, isShown in viewitems(self.__isShown):
            if isShown:
                self.removeChannel(difficulty)

    def removeChannel(self, difficulty):
        _, clientID = self.__clientIDs[difficulty]
        gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_REMOVE), gui.shared.EVENT_BUS_SCOPE.LOBBY)
        self.__isShown[difficulty] = False

    def addChannel(self, difficulty):
        lazyChannel, clientID = self.__clientIDs.get(difficulty, (None, None))
        if not clientID or not lazyChannel:
            return None
        else:
            if self.channelsCtrl.getController(clientID):
                currCarouselItemCtx = _defCarouselItemCtx._replace(label=lazyChannel, order=getOrder4LazyChannel(lazyChannel), isNotified=not ls_account_settings.getSettings(AccountSettingsKeys.CHAT_FIRST_SEEN).get(difficulty.value), criteria={VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, clientID)}, openHandler=lambda : showLazyChannelWindow(clientID))
                gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_ADD, currCarouselItemCtx._asdict()), gui.shared.EVENT_BUS_SCOPE.LOBBY)
                self.__isShown[difficulty] = True
                ls_account_settings.setChatFirstSeen(difficulty, True)
            return None

    def _update(self, *args, **kwargs):
        if self.lsCtrl.isEventPrb():
            difficulty = self.lsDifficultyCtrl.getSelectedLevel()
            if difficulty not in self.__isShown:
                return
            if self.__isShown[difficulty]:
                if not self.isEnabled():
                    self.removeChannel(difficulty)
                return
            self.removeChannels()
            levelInfo = self.lsDifficultyCtrl.getLevelInfo(difficulty.value)
            if not self.isEnabled() or levelInfo is None or not levelInfo.isUnlock:
                return
            self.addChannel(difficulty)
        else:
            self.removeChannels()
        return

    def _onServerSettingChanged(self, diff):
        if self.SYS_CHANNELS_PARAM_KEY in diff:
            self._update()

    def __clear(self):
        g_eventBus.removeListener(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        self.lsCtrl.onSettingsUpdate -= self._update
        self.lsDifficultyCtrl.onChangeDifficultyLevel -= self._update
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.stopGlobalListening()
        self.removeChannels()
        self.__isShown.update({difficulty:False for difficulty in self.__isShown})

    def __handlerMinimizeAll(self, _):
        viewContainer = self.app.containerManager
        for criteria, layer in self.__handlers:
            window = viewContainer.getView(layer, criteria)
            if window is not None:
                window.onWindowMinimize()

        return
