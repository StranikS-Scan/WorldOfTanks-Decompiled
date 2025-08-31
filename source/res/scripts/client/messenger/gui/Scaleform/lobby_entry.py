# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/lobby_entry.py
import weakref
from collections import defaultdict
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view import dialogs
from gui.Scaleform.managers.windows_stored_data import g_windowsStoredData, TARGET_ID
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import MessengerEvent, ChannelManagementEvent
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from messenger.formatters.users_messages import getUserActionReceivedMessage
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform import channels
from messenger.gui.Scaleform.data.ChannelsCarouselHandler import ChannelsCarouselHandler
from messenger.gui.Scaleform.view.lobby import antispam_message
from messenger.gui.interfaces import IGUIEntry
from messenger.m_constants import MESSENGER_SCOPE, LAZY_CHANNEL
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
from shared_utils import findFirst
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.shared import IItemsCache

class LobbyEntry(IGUIEntry):
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(LobbyEntry, self).__init__()
        self.__channelsCtrl = None
        self.__carouselHandler = None
        self.__components = defaultdict(list)
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @property
    def channelsCtrl(self):
        return self.__channelsCtrl

    def init(self):
        self.__channelsCtrl = channels.LobbyControllers()
        self.__channelsCtrl.init()
        self.__carouselHandler = ChannelsCarouselHandler(self)
        self.__carouselHandler.init()
        events = g_messengerEvents.channels
        events.onMessageReceived += self.__me_onMessageReceived
        events.onHistoryReceived += self.__me_onHistoryReceived
        add = g_eventBus.addListener
        add(MessengerEvent.LAZY_CHANNEL_CTRL_INITED, self.__handleLazyChannelCtlInited, scope=EVENT_BUS_SCOPE.LOBBY)
        add(MessengerEvent.LAZY_CHANNEL_CTRL_DESTROYED, self.__handleLazyChannelCtlDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        add(MessengerEvent.LOBBY_CHANNEL_CTRL_INITED, self.__handleLobbyChannelCtlInited, scope=EVENT_BUS_SCOPE.LOBBY)
        add(MessengerEvent.LOBBY_CHANNEL_CTRL_DESTROYED, self.__handleLobbyChannelCtlDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        add(MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__handlePrbChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_ACTIVATE, self.__handleRqActivateChannel, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_DEACTIVATE, self.__handleRqDeactivateChannel, scope=EVENT_BUS_SCOPE.LOBBY)
        add(ChannelManagementEvent.REQUEST_TO_EXIT, self.__handleRqExitFromChannel, scope=EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        self.__components.clear()
        if self.__channelsCtrl is not None:
            self.__channelsCtrl.clear()
            self.__channelsCtrl = None
        if self.__carouselHandler is not None:
            self.__carouselHandler.clear()
            self.__carouselHandler = None
        events = g_messengerEvents.channels
        events.onMessageReceived -= self.__me_onMessageReceived
        events.onHistoryReceived -= self.__me_onHistoryReceived
        remove = g_eventBus.removeListener
        remove(MessengerEvent.LAZY_CHANNEL_CTRL_INITED, self.__handleLazyChannelCtlInited, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(MessengerEvent.LAZY_CHANNEL_CTRL_DESTROYED, self.__handleLazyChannelCtlDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(MessengerEvent.LOBBY_CHANNEL_CTRL_INITED, self.__handleLobbyChannelCtlInited, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(MessengerEvent.LOBBY_CHANNEL_CTRL_DESTROYED, self.__handleLobbyChannelCtlDestroyed, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(MessengerEvent.PRB_CHANNEL_CTRL_INITED, self.__handlePrbChannelControllerInited, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_ACTIVATE, self.__handleRqActivateChannel, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_DEACTIVATE, self.__handleRqDeactivateChannel, scope=EVENT_BUS_SCOPE.LOBBY)
        remove(ChannelManagementEvent.REQUEST_TO_EXIT, self.__handleRqExitFromChannel, scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def show(self):
        self.__carouselHandler.start()
        cEvents = g_messengerEvents.channels
        cEvents.onPlayerEnterChannelByAction += self.__me_onPlayerEnterChannelByAction
        cEvents.onConnectingToSecureChannel += self.__me_onConnectingToSecureChannel
        cEvents.onChannelInfoUpdated += self.__me_onChannelInfoUpdated
        cEvents.onCommandReceived += self.__me_onCommandReceived
        g_messengerEvents.users.onUserActionReceived += self.__me_onUserActionReceived
        g_messengerEvents.onErrorReceived += self.__me_onErrorReceived
        self.__limitedUIController.startObserve(LuiRules.COMMON_CHAT, self.__updateCommonChatVisibility)
        self.__itemsCache.onSyncCompleted += self.__onSyncCompleted

    def close(self, nextScope):
        self.__components.clear()
        setTrustedCriteria = g_windowsStoredData.setTrustedCriteria
        for controller in self.__channelsCtrl.getControllersIterator():
            channel = controller.getChannel()
            setTrustedCriteria(TARGET_ID.CHANNEL_CAROUSEL, (channel.getProtoType(), channel.getID()))
            controller.deactivate(entryClosing=True)

        self.__carouselHandler.stop()
        if nextScope is MESSENGER_SCOPE.LOGIN:
            antispam_message.reset()
            self.__channelsCtrl.removeControllers()
            self.__carouselHandler.removeChannels()
        cEvents = g_messengerEvents.channels
        cEvents.onPlayerEnterChannelByAction -= self.__me_onPlayerEnterChannelByAction
        cEvents.onConnectingToSecureChannel -= self.__me_onConnectingToSecureChannel
        cEvents.onChannelInfoUpdated -= self.__me_onChannelInfoUpdated
        cEvents.onCommandReceived -= self.__me_onCommandReceived
        g_messengerEvents.users.onUserActionReceived -= self.__me_onUserActionReceived
        g_messengerEvents.onErrorReceived -= self.__me_onErrorReceived
        self.__limitedUIController.stopObserve(LuiRules.COMMON_CHAT, self.__updateCommonChatVisibility)
        self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted

    def addClientMessage(self, message, isCurrentPlayer=False):
        pass

    def __setView4Ctrl(self, controller):
        clientID = controller.getChannel().getClientID()
        if clientID in self.__components:
            components = self.__components.pop(clientID)
            for component in components:
                controller.setView(component())

    def __me_onMessageReceived(self, message, channel):
        if channel:
            clientID = channel.getClientID()
            controller = self.__channelsCtrl.getController(clientID)
            if controller:
                isNotShown = not channel.isMessageShown(message)
                if not controller.addMessage(message):
                    if isNotShown:
                        self.__carouselHandler.notifyChannel(channel, message)
                elif isNotShown:
                    channel.setMessageShown(message)

    def __me_onHistoryReceived(self, history, channel):
        if channel:
            clientID = channel.getClientID()
            controller = self.__channelsCtrl.getController(clientID)
            if controller:
                controller.setHistory(history)

    def __me_onCommandReceived(self, command):
        controller = self.__channelsCtrl.getController(command.getClientID())
        if controller:
            controller.addCommand(command)
        else:
            LOG_ERROR('Controller not found', command)

    def __me_onPlayerEnterChannelByAction(self, channel):
        controller = self.channelsCtrl.getController(channel.getClientID())
        if controller is None:
            LOG_ERROR('Controller not found', channel)
        else:
            events_dispatcher.showLobbyChannelWindow(channel.getClientID())
        return

    def __me_onConnectingToSecureChannel(self, channel):
        events_dispatcher.showConnectToSecureChannelWindow(channel)

    def __me_onChannelInfoUpdated(self, channel):
        self.__carouselHandler.updateChannel(channel)

    def __me_onUserActionReceived(self, action, user, shadowMode):
        message = getUserActionReceivedMessage(action, user)
        if message and not shadowMode:
            SystemMessages.pushMessage(message)

    def __me_onErrorReceived(self, error):
        if error.isModal():
            DialogsInterface.showDialog(dialogs.SimpleDialogMeta(error.getTitle(), error.getMessage(), dialogs.I18nInfoDialogButtons('common/error')), lambda *args: None)
        else:
            SystemMessages.pushMessage(error.getMessage(), type=SystemMessages.SM_TYPE.Error)

    def __handleLazyChannelCtlInited(self, event):
        ctx = event.ctx
        controller = ctx.get('controller')
        if controller is None:
            LOG_ERROR('Controller is not defined', ctx)
            return
        else:
            ctx.clear()
            channel = controller.getChannel()
            if channel.isAlwaysShow():
                if channel.getName() == LAZY_CHANNEL.COMMON:
                    if self.__limitedUIController.isRuleCompleted(LuiRules.COMMON_CHAT):
                        self.__carouselHandler.addChannel(channel, lazy=True)
                else:
                    self.__carouselHandler.addChannel(channel, lazy=True)
            self.__setView4Ctrl(controller)
            return

    def __handleLazyChannelCtlDestroyed(self, event):
        ctx = event.ctx
        controller = ctx.get('controller')
        if controller is None:
            LOG_ERROR('Controller is not defined', ctx)
            return
        else:
            self.__carouselHandler.removeChannel(controller.getChannel())
            return

    def __handleLobbyChannelCtlInited(self, event):
        ctx = event.ctx
        controller = ctx.get('controller')
        if controller is None:
            LOG_ERROR('Controller is not defined', ctx)
            return
        else:
            channel = controller.getChannel()
            self.__carouselHandler.addChannel(channel, isNotified=controller.hasUnreadMessages())
            return

    def __handleLobbyChannelCtlDestroyed(self, event):
        ctx = event.ctx
        controller = ctx.get('controller')
        if controller is None:
            LOG_ERROR('Controller is not defined', ctx)
            return
        else:
            self.__carouselHandler.removeChannel(controller.getChannel())
            return

    def __handlePrbChannelControllerInited(self, event):
        ctx = event.ctx
        prbType = ctx.get('prbType', 0)
        if not prbType:
            LOG_DEBUG('Prebattle type is not defined', ctx)
            return
        else:
            controller = ctx.get('controller')
            if controller is None:
                LOG_ERROR('Channel controller is not defined', ctx)
                return
            ctx.clear()
            self.__setView4Ctrl(controller)
            return

    def __handleRqActivateChannel(self, event):
        clientID = event.clientID
        if clientID is None:
            LOG_ERROR('clientID is not defined')
            return
        else:
            ctx = event.ctx
            component = ctx.get('component')
            if component is None:
                LOG_ERROR('UI component is not defined', ctx)
                return
            ctx.clear()
            controller = self.__channelsCtrl.getController(clientID)
            if controller:
                controller.setView(component)
            else:
                self.__components[clientID].append(weakref.ref(component))
            return

    def __handleRqDeactivateChannel(self, event):
        clientID = event.clientID
        if clientID is None:
            LOG_ERROR('clientID is not defined')
            return
        else:
            controller = self.__channelsCtrl.getController(clientID)
            if controller:
                controller.deactivate()
            return

    def __handleRqExitFromChannel(self, event):
        clientID = event.clientID
        if clientID is None:
            LOG_ERROR('clientID is not defined')
            return
        else:
            controller = self.__channelsCtrl.getController(clientID)
            if controller:
                controller.exit()
            return

    def __onSyncCompleted(self, reason, _):
        if reason in (CACHE_SYNC_REASON.SHOW_GUI, CACHE_SYNC_REASON.CLIENT_UPDATE, CACHE_SYNC_REASON.DOSSIER_RESYNC):
            self.__updateCommonChatVisibility()
            self.__itemsCache.onSyncCompleted -= self.__onSyncCompleted

    def __updateCommonChatVisibility(self, *_):
        channel = findFirst(lambda ch: ch.getName() == LAZY_CHANNEL.COMMON, self.channelsStorage.all())
        if channel is None:
            return
        else:
            isChannelExists = self.__carouselHandler.isChannelExists(channel)
            if self.__limitedUIController.isRuleCompleted(LuiRules.COMMON_CHAT):
                if not isChannelExists:
                    self.__carouselHandler.addChannel(channel, lazy=True)
            elif isChannelExists:
                self.__carouselHandler.removeChannel(channel)
            return
