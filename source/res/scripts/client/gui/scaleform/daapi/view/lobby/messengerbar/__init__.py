# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.managers.context_menu import ContextMenuManager
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CHANNEL_LIST, 'gui.Scaleform.daapi.view.lobby.messengerBar.ChannelListContextMenuHandler', 'ChannelListContextMenuHandler')

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.messengerBar.ChannelCarousel import ChannelCarousel
    from gui.Scaleform.daapi.view.lobby.messengerBar.ContactsListButton import ContactsListButton
    from gui.Scaleform.daapi.view.lobby.messengerBar.MessengerBar import MessengerBar
    from gui.Scaleform.daapi.view.lobby.messengerBar.NotificationListButton import NotificationListButton
    from notification.NotificationListView import NotificationListView
    from notification.NotificationPopUpViewer import NotificationPopUpViewer
    return (GroupedViewSettings(VIEW_ALIAS.NOTIFICATIONS_LIST, NotificationListView, 'notificationsList.swf', ViewTypes.WINDOW, 'notificationsList', VIEW_ALIAS.NOTIFICATIONS_LIST, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     ViewSettings(VIEW_ALIAS.CHANNEL_CAROUSEL, ChannelCarousel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.CONTACTS_LIST_BUTTON, ContactsListButton, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MESSENGER_BAR, MessengerBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.NOTIFICATION_LIST_BUTTON, NotificationListButton, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.SYSTEM_MESSAGES, NotificationPopUpViewer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (MessengerBarBusinessHandler(),)


class MessengerBarBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.NOTIFICATIONS_LIST, self.loadViewByCtxEvent),)
        super(MessengerBarBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
