# Embedded file name: scripts/client/messenger/gui/Scaleform/sf_settings.py
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings, ScopeTemplates
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowWindowEvent

class MESSENGER_VIEW_ALIAS(object):
    FAQ_WINDOW = 'messenger/faqWindow'
    CHANNEL_MANAGEMENT_WINDOW = 'messenger/channelsManagementWindow'
    CONTACTS_WINDOW = 'messenger/contactsWindow'
    LAZY_CHANNEL_WINDOW = 'messenger/lazyChannelWindow'
    LOBBY_CHANNEL_WINDOW = 'messenger/lobbyChannelWindow'
    CONNECT_TO_SECURE_CHANNEL_WINDOW = 'messenger/connectToSecureChannelWindow'
    CHANNEL_COMPONENT = 'channelComponent'


def getViewSettings():
    from messenger.gui.Scaleform.view import ChannelComponent
    from messenger.gui.Scaleform.view import ChannelsManagementWindow
    from messenger.gui.Scaleform.view import ConnectToSecureChannelWindow
    from messenger.gui.Scaleform.view import FAQWindow
    from messenger.gui.Scaleform.view import LazyChannelWindow
    from messenger.gui.Scaleform.view import LobbyChannelWindow
    from messenger.gui.Scaleform.view import ContactsWindow
    return [GroupedViewSettings(MESSENGER_VIEW_ALIAS.FAQ_WINDOW, FAQWindow, 'FAQWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, ChannelsManagementWindow, 'channelsManagementWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_CHANNEL_MANAGEMENT_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CONTACTS_WINDOW, ContactsWindow, 'contactsWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_CONTACTS_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, LazyChannelWindow, 'lazyChannelWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_LAZY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, LobbyChannelWindow, 'lobbyChannelWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_LOBBY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, ConnectToSecureChannelWindow, 'connectToSecureChannelWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_CONNECT_TO_SECURE_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT, ChannelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [MessengerPackageBusinessHandler()]


class MessengerPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(ShowWindowEvent.SHOW_FAQ_WINDOW, self.__showFAQWindow),
         (ShowWindowEvent.SHOW_CHANNEL_MANAGEMENT_WINDOW, self.__showChannelsManagementWindow),
         (ShowWindowEvent.SHOW_CONTACTS_WINDOW, self.__showContactsWindow),
         (ShowWindowEvent.SHOW_LAZY_CHANNEL_WINDOW, self.__showLazyChannelWindow),
         (ShowWindowEvent.SHOW_LOBBY_CHANNEL_WINDOW, self.__showLobbyChannelWindow),
         (ShowWindowEvent.SHOW_CONNECT_TO_SECURE_CHANNEL_WINDOW, self.__showConnectToSecureChannelWindow)]
        super(MessengerPackageBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showFAQWindow(self, _):
        alias = name = MESSENGER_VIEW_ALIAS.FAQ_WINDOW
        self.app.loadView(alias, name)

    def __showChannelsManagementWindow(self, _):
        alias = name = MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW
        self.app.loadView(alias, name)

    def __showContactsWindow(self, _):
        alias = name = MESSENGER_VIEW_ALIAS.CONTACTS_WINDOW
        self.app.loadView(alias, name)

    def __showLazyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW
        clientID = event.ctx['clientID']
        self.app.loadView(alias, 'lobbyChannelWindow_{0:n}'.format(clientID), clientID)

    def __showLobbyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW
        clientID = event.ctx['clientID']
        self.app.loadView(alias, 'lobbyChannelWindow_{0:n}'.format(clientID), clientID)

    def __showConnectToSecureChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW
        channel = event.ctx['channel']
        self.app.loadView(alias, 'connectToSecureChannel_{0:n}'.format(channel.getClientID()), channel)
