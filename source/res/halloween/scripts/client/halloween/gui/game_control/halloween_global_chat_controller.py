# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_global_chat_controller.py
from __future__ import absolute_import
import gui.shared
from constants import Configs
from gui.app_loader import sf_lobby
from gui.shared.utils.functions import getViewName
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.prb_control.entities.listener import IGlobalListener
from halloween.gui import halloween_account_settings
from halloween.gui.halloween_account_settings import AccountSettingsKeys
from halloween.gui.halloween_gui_constants import LAZY_CHANNEL
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.skeletons.halloween_global_chat_controller import IHalloweenGlobalChatController
from halloween_common.halloween_constants import HALLOWEEN_CHAT_CHANNEL
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

class HalloweenGlobalChatController(IHalloweenGlobalChatController, IGlobalListener):
    halloweenCtrl = dependency.descriptor(IHalloweenController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    SYS_CHANNELS_PARAM_KEY = Configs.SYSTEM_CHANNELS.value

    def __init__(self):
        self.__clientID = channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.HALLOWEEN_GLOBAL_CHANNEL)
        if not self.__clientID:
            SoftException('Client ID not found. Halloween channel does not work')
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
        super(HalloweenGlobalChatController, self).fini()

    def onDisconnected(self):
        super(HalloweenGlobalChatController, self).onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(HalloweenGlobalChatController, self).onAvatarBecomePlayer()
        self.__clear()

    def onLobbyInited(self, event):
        super(HalloweenGlobalChatController, self).onLobbyInited(event)
        self.startGlobalListening()
        self.halloweenCtrl.onSettingsUpdate += self._update
        self.lobbyContext.getServerSettings().onServerSettingsChange += self._onServerSettingChanged
        g_eventBus.addListener(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        self._update()

    def onPrbEntitySwitched(self):
        self._update()

    def isEnabled(self):
        return self.halloweenCtrl.isAvailable() and self.isChatEnabled() and not self.isAllChatsDisabled()

    def isAllChatsDisabled(self):
        return self.lobbyContext.getServerSettings().getSettings()[self.SYS_CHANNELS_PARAM_KEY]['disableAllChats']

    def isChatEnabled(self):
        sysChannelConfig = self.lobbyContext.getServerSettings().getSettings()[self.SYS_CHANNELS_PARAM_KEY]
        return sysChannelConfig.get('sysChannelsConfig', {}).get(HALLOWEEN_CHAT_CHANNEL, False)

    def removeChannel(self):
        if self.__isShown:
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_REMOVE), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = False

    def addChannel(self):
        if not self.__isShown and self.channelsCtrl.getController(self.__clientID):
            currCarouselItemCtx = _defCarouselItemCtx._replace(label=LAZY_CHANNEL.HALLOWEEN_GLOBAL_CHANNEL, order=channel_num_gen.getOrder4LazyChannel(LAZY_CHANNEL.HALLOWEEN_GLOBAL_CHANNEL), isNotified=not halloween_account_settings.getSettings(AccountSettingsKeys.CHAT_FIRST_SEEN), criteria={VIEW_SEARCH_CRITERIA.VIEW_UNIQUE_NAME: getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, self.__clientID)}, openHandler=lambda : showLazyChannelWindow(self.__clientID))
            gui.shared.g_eventBus.handleEvent(gui.shared.events.ChannelManagementEvent(self.__clientID, gui.shared.events.PreBattleChannelEvent.REQUEST_TO_ADD, currCarouselItemCtx._asdict()), gui.shared.EVENT_BUS_SCOPE.LOBBY)
            self.__isShown = True
            halloween_account_settings.setSettings(AccountSettingsKeys.CHAT_FIRST_SEEN, True)

    def _onServerSettingChanged(self, diff):
        if self.SYS_CHANNELS_PARAM_KEY in diff:
            self._update()

    def _update(self):
        if self.isEnabled() and self.halloweenCtrl.isEventPrb():
            self.addChannel()
        else:
            self.removeChannel()

    def __clear(self):
        g_eventBus.removeListener(ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, self.__handlerMinimizeAll, scope=EVENT_BUS_SCOPE.LOBBY)
        self.halloweenCtrl.onSettingsUpdate -= self._update
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
