# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/chats_presenter.py
from __future__ import absolute_import
import logging
from constants import Configs
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen.view_models.views.lobby.page.footer.chat_model import ChatModel
from gui.impl.gen.view_models.views.lobby.page.footer.message_model import MessageModel
from gui.impl.gui_decorators import args2params
from gui.impl.pub.view_component import ViewComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import ChannelCarouselEvent, ChannelManagementEvent
from helpers import dependency, i18n
from helpers.server_settings import serverSettingsChangeListener
from messenger import MessengerEntry
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.m_constants import MESSENGER_SCOPE, LAZY_CHANNEL
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

def _convertDPItemToModel(item):
    message = MessageModel()
    message.setId(item['clientID'])
    message.setName(i18n.makeString(item['label']))
    message.setSystem(not item['canClose'])
    message.setSelected(item['isWindowOpened'])
    message.setViewed(not item['isNotified'])
    message.setTooltipId(item['tooltipData']['tooltipId'])
    return message


class ChatsPresenter(ViewComponent[ChatModel]):
    __appLoader = dependency.descriptor(IAppLoader)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ChatsPresenter, self).__init__(model=ChatModel)
        self.__carouselHandler = MessengerEntry.g_instance.gui.getEntry(MESSENGER_SCOPE.LOBBY).carouselHandler

    @property
    def viewModel(self):
        return super(ChatsPresenter, self).getViewModel()

    def _finalize(self):
        super(ChatsPresenter, self)._finalize()
        self.__carouselHandler.setNextWindowGeometry(None)
        if self.__carouselHandler.channelsDP is not None:
            self.__carouselHandler.channelsDP.onDataUpdated -= self.__updateModel
        if self.__carouselHandler.preBattleChannelsDP is not None:
            self.__carouselHandler.preBattleChannelsDP.onDataUpdated -= self.__updateModel
        return

    def _onLoading(self, *args, **kwargs):
        super(ChatsPresenter, self)._onLoading()
        self.__carouselHandler.channelsDP.onDataUpdated += self.__updateModel
        self.__carouselHandler.preBattleChannelsDP.onDataUpdated += self.__updateModel
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.onViewMessageAction, self.__onViewMessageAction),
         (self.viewModel.onDeleteMessageAction, self.__onDeleteMessageAction),
         (self.viewModel.onWindowAnchorPositionUpdated, self.__onWindowAnchorPositionUpdated),
         (self.viewModel.onChatsAction, self.__onChatsAction),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged))

    def _getListeners(self):
        return ((events.ChannelWindowEvent.ON_WINDOW_POPULATE, self.__onWindowPopulate, EVENT_BUS_SCOPE.LOBBY), (events.ChannelWindowEvent.ON_WINDOW_MINIMIZE, self.__onWindowMinimize, EVENT_BUS_SCOPE.LOBBY))

    @serverSettingsChangeListener(Configs.SYSTEM_CHANNELS.value)
    def __onServerSettingChanged(self, diff):
        self.__updateModel()

    @args2params(int, int, int, int)
    def __onWindowAnchorPositionUpdated(self, x, y, width, height):
        self.__carouselHandler.setNextWindowGeometry((x,
         y,
         width,
         height))

    def __onWindowPopulate(self, event):
        self.__requestChange(event.ctx['clientID'], 'isWindowOpened', True)

    def __onWindowMinimize(self, event):
        self.__requestChange(event.ctx['clientID'], 'isWindowOpened', False)

    def __requestChange(self, clientID, key, value):
        g_eventBus.handleEvent(ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': key,
         'value': value}), scope=EVENT_BUS_SCOPE.LOBBY)

    @args2params(int, int, int, int, int)
    def __onViewMessageAction(self, sessionID, x, y, width, height):
        self.__carouselHandler.setWindowGeometry(sessionID, (x,
         y,
         width,
         height))
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.OPEN_BUTTON_CLICK, sessionID), scope=EVENT_BUS_SCOPE.LOBBY)

    @args2params(int)
    def __onDeleteMessageAction(self, sessionID):
        g_eventBus.handleEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.CLOSE_BUTTON_CLICK, sessionID), scope=EVENT_BUS_SCOPE.LOBBY)

    @args2params(int, int, int, int)
    def __onChatsAction(self, x, y, width, height):
        manager = self.__appLoader.getApp().containerManager
        window = manager.getView(WindowLayer.WINDOW, {POP_UP_CRITERIA.VIEW_ALIAS: g_entitiesFactories.getAliasByEvent(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW)})
        if not window:
            self.__carouselHandler.setManagerWindowGeometry((x,
             y,
             width,
             height))
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW)), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            name = window.uniqueName
            isOnTop = manager.as_isOnTopS(WindowLayer.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(WindowLayer.WINDOW, name)
            else:
                window.onWindowClose()

    def __updateModel(self, *_):
        if not self.isBound():
            return
        channels, preBattleChannels = self.__getChannelsList()
        messages = self.viewModel.getMessages()
        messages.clear()
        if not self.__lobbyContext.getServerSettings().isChatEnabled():
            return
        for idx, channel in enumerate(channels):
            if channel['label'] == LAZY_CHANNEL.COMMON and not self.__lobbyContext.getServerSettings().isHangarGeneralChatEnabled():
                continue
            message = _convertDPItemToModel(channel)
            message.setOrder(idx)
            messages[str(channel['clientID'])] = message

        for idx, prbChannel in enumerate(preBattleChannels):
            message = _convertDPItemToModel(prbChannel)
            message.setOrder(idx)
            message.setPrebattle(True)
            messages[str(prbChannel['clientID'])] = message

    def __getChannelsList(self):
        return (self.__carouselHandler.channelsDP.collection, self.__carouselHandler.preBattleChannelsDP.collection)
