# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.messengerBar.VehicleCompareCartButton import VehicleCompareCartButton
from gui.Scaleform.daapi.view.lobby.messengerBar.session_stats_button import SessionStatsButton
from gui.Scaleform.daapi.view.lobby.profile.earning_pop_up_view import EarningPopUpView
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.SESSION_STATS_CONSTANTS import SESSION_STATS_CONSTANTS

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.messengerBar.ChannelListContextMenuHandler import ChannelListContextMenuHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.CHANNEL_LIST, ChannelListContextMenuHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.messengerBar.ChannelCarousel import ChannelCarousel
    from gui.Scaleform.daapi.view.lobby.messengerBar.ContactsListButton import ContactsListButton
    from gui.Scaleform.daapi.view.lobby.messengerBar.messenger_bar import MessengerBar
    from gui.Scaleform.daapi.view.lobby.messengerBar.NotificationListButton import NotificationListButton
    from notification.NotificationListView import NotificationListView
    from notification.NotificationPopUpViewer import NotificationPopUpViewer
    return (GroupedViewSettings(VIEW_ALIAS.NOTIFICATIONS_LIST, NotificationListView, 'notificationsList.swf', WindowLayer.WINDOW, 'notificationsList', VIEW_ALIAS.NOTIFICATIONS_LIST, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     ComponentSettings(VIEW_ALIAS.CHANNEL_CAROUSEL, ChannelCarousel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.CONTACTS_LIST_BUTTON, ContactsListButton, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.VEHICLE_COMPARE_CART_BUTTON, VehicleCompareCartButton, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.MESSENGER_BAR, MessengerBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.NOTIFICATION_LIST_BUTTON, NotificationListButton, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(SESSION_STATS_CONSTANTS.SESSION_STATS_BUTTON_ALIAS, SessionStatsButton, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.SYSTEM_MESSAGES, NotificationPopUpViewer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(VIEW_ALIAS.ADVANCED_ACHIEVEMENTS_EARNING_VIEW, EarningPopUpView, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (MessengerBarBusinessHandler(),)


class MessengerBarBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.NOTIFICATIONS_LIST, self.loadViewByCtxEvent),)
        super(MessengerBarBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
