# Embedded file name: scripts/client/messenger/gui/events_dispatcher.py
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE

def showLobbyChannelWindow(clientID):
    g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_LOBBY_CHANNEL_WINDOW, {'clientID': clientID}), scope=EVENT_BUS_SCOPE.LOBBY)


def showLazyChannelWindow(clientID):
    g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_LAZY_CHANNEL_WINDOW, {'clientID': clientID}), scope=EVENT_BUS_SCOPE.LOBBY)


def notifyCarousel(clientID, notify = True):
    g_eventBus.handleEvent(events.ChannelManagementEvent(clientID, events.ChannelManagementEvent.REQUEST_TO_CHANGE, {'key': 'isNotified',
     'value': notify}), scope=EVENT_BUS_SCOPE.LOBBY)


def showConnectToSecureChannelWindow(channel):
    g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_CONNECT_TO_SECURE_CHANNEL_WINDOW, {'channel': channel}), scope=EVENT_BUS_SCOPE.LOBBY)
