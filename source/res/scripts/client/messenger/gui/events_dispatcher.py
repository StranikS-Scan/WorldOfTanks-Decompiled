# Embedded file name: scripts/client/messenger/gui/events_dispatcher.py
from debug_utils import LOG_ERROR
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from messenger.ext import channel_num_gen
from gui.shared.utils.functions import getViewName
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS

def showLobbyChannelWindow(clientID):
    g_eventBus.handleEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, ctx={'clientID': clientID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showLazyChannelWindow(clientID):
    g_eventBus.handleEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, ctx={'clientID': clientID}), scope=EVENT_BUS_SCOPE.LOBBY)


def notifyCarousel(clientID, notify = True):
    g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': 'isNotified',
     'value': notify}), scope=EVENT_BUS_SCOPE.LOBBY)


def showConnectToSecureChannelWindow(channel):
    g_eventBus.handleEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, getViewName(MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, channel.getClientID()), {'channel': channel}), scope=EVENT_BUS_SCOPE.LOBBY)


def rqActivateChannel(clientID, component):
    g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_ACTIVATE, {'component': component}), scope=EVENT_BUS_SCOPE.LOBBY)


def rqActivateLazyChannel(name, component):
    clientID = channel_num_gen.getClientID4LazyChannel(name)
    if not clientID:
        LOG_ERROR('Client ID is not found', name)
    else:
        rqActivateChannel(clientID, component)


def rqDeactivateChannel(clientID):
    g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_DEACTIVATE), scope=EVENT_BUS_SCOPE.LOBBY)


def rqDeactivateLazyChannel(name):
    clientID = channel_num_gen.getClientID4LazyChannel(name)
    if not clientID:
        LOG_ERROR('Client ID is not found', name)
    else:
        rqDeactivateChannel(clientID)


def rqExitFromChannel(clientID):
    g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_EXIT), scope=EVENT_BUS_SCOPE.LOBBY)


def rqExitFromLazyChannel(name):
    clientID = channel_num_gen.getClientID4LazyChannel(name)
    if not clientID:
        LOG_ERROR('Client ID is not found', name)
    else:
        rqExitFromChannel(clientID)
