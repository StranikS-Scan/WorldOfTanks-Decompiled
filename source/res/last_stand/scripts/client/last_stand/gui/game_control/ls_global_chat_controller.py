# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_global_chat_controller.py
import gui.shared
from constants import Configs
from gui.app_loader import sf_lobby
from gui.shared.utils.functions import getViewName
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent, GUICommonEvent
from gui.prb_control.entities.listener import IGlobalListener
from last_stand.gui import ls_account_settings
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.ls_gui_constants import LAZY_CHANNEL
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_global_chat_controller import ILSGlobalChatController
from last_stand_common.last_stand_constants import LS_CHAT_CHANNEL
from helpers import dependency
from messenger.ext import channel_num_gen
from gui.prb_control.events_dispatcher import _defCarouselItemCtx
from gui.Scaleform.framework.managers.containers import VIEW_SEARCH_CRITERIA
from messenger.gui.Scaleform.data.ChannelsCarouselHandler import ChannelFindCriteria
from messenger.gui.events_dispatcher import showLazyChannelWindow
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.inject import channelsCtrlProperty
from soft_exception import SoftException
from frameworks.wulf import WindowLayer
from skeletons.gui.lobby_context import ILobbyContext

class LSGlobalChatController(ILSGlobalChatController, IGlobalListener):
    lsCtrl = dependency.descriptor(ILSController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    SYS_CHANNELS_PARAM_KEY = Configs.SYSTEM_CHANNELS.value

    def __init__(self):
        self.__clientID = channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL)
        if not self.__clientID:
            SoftException('Client ID not found. Last stand channel does not work')
        self.__handler = (ChannelFindCriteria(self.__clientID), WindowLayer.WINDOW)
        self.__isShown = False

    @sf_lobby
    def app(self):
        return None

    @channelsCtrlProperty
    def channelsCtrl(self):
        return None

    def fini(self):
        self.__clear()
        super(LSGlobalChatController, self).fini()

    def onDisconnected(self):
        super(LSGlobalChatController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(LSGlobalChatController, self).onAvatarBecomePlayer()
        self.__clear()

    def onLobbyInited(self, event):
        super(LSGlobalChatController, self).onLobbyInited(event)
        self.startGlobalListening()
        self.lsCtrl.onSettingsUpdate += self._update
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
        return sysChannelConfig.get('sysChannelsConfig', {}).get(LS_CHAT_CHANNEL, False)

    def removeChannel(self):
        if self.__isShown:
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_REMOVE), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = False

    def addChannel(self):
        if not self.__isShown and self.channelsCtrl.getController(self.__clientID):
            currCarouselItemCtx = _defCarouselItemCtx._replace(label=LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL, order=channel_num_gen.getOrder4LazyChannel(LAZY_CHANNEL.LAST_STAND_GLOBAL_CHANNEL), isNotified=not ls_account_settings.getSettings(AccountSettingsKeys.CHAT_FIRST_SEEN), criteria={VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, self.__clientID)}, openHandler=lambda : showLazyChannelWindow(self.__clientID))
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_ADD, currCarouselItemCtx._asdict()), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = True
            ls_account_settings.setSettings(AccountSettingsKeys.CHAT_FIRST_SEEN, True)

    def _update(self):
        if self.isEnabled() and self.lsCtrl.isEventPrb():
            self.addChannel()
        else:
            self.removeChannel()

    def _onServerSettingChanged(self, diff):
        if self.SYS_CHANNELS_PARAM_KEY in diff:
            self._update()

    def __clear(self):
        g_eventBus.removeListener(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        self.lsCtrl.onSettingsUpdate -= self._update
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self._onServerSettingChanged
        self.stopGlobalListening()
        self.__isShown = False

    def __handlerMinimizeAll(self, _):
        viewContainer = self.app.containerManager
        criteria, layer = self.__handler
        window = viewContainer.getView(layer, criteria)
        if window is not None:
            window.onWindowMinimize()
        return
