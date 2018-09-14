# Embedded file name: scripts/client/messenger/gui/Scaleform/sf_settings.py
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings, ScopeTemplates
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName

class MESSENGER_VIEW_ALIAS(object):
    FAQ_WINDOW = 'messenger/faqWindow'
    CHANNEL_MANAGEMENT_WINDOW = 'messenger/channelsManagementWindow'
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
    return [GroupedViewSettings(MESSENGER_VIEW_ALIAS.FAQ_WINDOW, FAQWindow, 'FAQWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, ChannelsManagementWindow, 'channelsManagementWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, LazyChannelWindow, 'lazyChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, LobbyChannelWindow, 'lobbyChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, ConnectToSecureChannelWindow, 'connectToSecureChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True),
     ViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT, ChannelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [MessengerPackageBusinessHandler()]


class MessengerPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(MESSENGER_VIEW_ALIAS.FAQ_WINDOW, self.__showSimpleWindow),
         (MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, self.__showSimpleWindow),
         (MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, self.__showLazyChannelWindow),
         (MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, self.__showLobbyChannelWindow),
         (MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, self.__showSimpleWindow)]
        super(MessengerPackageBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showSimpleWindow(self, event):
        self.app.loadView(event.eventType, event.name, event.ctx)

    def __showLazyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW
        self.app.loadView(alias, getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, event.ctx.get('clientID')), event.ctx)

    def __showLobbyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW
        self.app.loadView(alias, getViewName(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, event.ctx['clientID']), event.ctx)
