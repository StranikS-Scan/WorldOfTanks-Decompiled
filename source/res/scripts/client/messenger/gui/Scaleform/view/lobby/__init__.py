# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/__init__.py
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ViewSettings
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTACTS_ALIASES import CONTACTS_ALIASES
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName
ACCOUNT_NAME_MIN_CHARS_LENGTH = 2
ACCOUNT_NAME_MAX_CHARS_LENGTH = 24

class MESSENGER_VIEW_ALIAS(object):
    FAQ_WINDOW = 'messenger/faqWindow'
    CHANNEL_MANAGEMENT_WINDOW = 'messenger/channelsManagementWindow'
    LAZY_CHANNEL_WINDOW = 'messenger/lazyChannelWindow'
    LOBBY_CHANNEL_WINDOW = 'messenger/lobbyChannelWindow'
    CONNECT_TO_SECURE_CHANNEL_WINDOW = 'messenger/connectToSecureChannelWindow'
    CHANNEL_COMPONENT = 'channelComponent'


def getContextMenuHandlers():
    from messenger.gui.Scaleform.data import contacts_cm_handlers
    return ((CONTEXT_MENU_HANDLER_TYPE.CONTACTS_GROUP, contacts_cm_handlers.SimpleContactsCMHandler), (CONTEXT_MENU_HANDLER_TYPE.PLAYER_CONTACTS, contacts_cm_handlers.PlayerContactsCMHandler))


def getViewSettings():
    from messenger.gui.Scaleform.view.lobby.ChannelComponent import ChannelComponent
    from messenger.gui.Scaleform.view.lobby.ChannelsManagementWindow import ChannelsManagementWindow
    from messenger.gui.Scaleform.view.lobby.ConnectToSecureChannelWindow import ConnectToSecureChannelWindow
    from messenger.gui.Scaleform.view.lobby.FAQWindow import FAQWindow
    from messenger.gui.Scaleform.view.lobby.LazyChannelWindow import LazyChannelWindow
    from messenger.gui.Scaleform.view.lobby.LobbyChannelWindow import LobbyChannelWindow
    from messenger.gui.Scaleform.view.lobby.contact_manage_note_views import ContactEditNoteView, ContactCreateNoteView
    from messenger.gui.Scaleform.view.lobby.ContactsSettingsView import ContactsSettingsView
    from messenger.gui.Scaleform.view.lobby.ContactsTreeComponent import ContactsTreeComponent
    from messenger.gui.Scaleform.view.lobby.GroupDeleteView import GroupDeleteView
    from messenger.gui.Scaleform.view.lobby.SearchContactView import SearchContactView
    from messenger.gui.Scaleform.view.lobby.ContactsListPopover import ContactsListPopover
    from messenger.gui.Scaleform.view.lobby.group_manage_views import GroupRenameView, GroupCreateView
    return (GroupedViewSettings(MESSENGER_VIEW_ALIAS.FAQ_WINDOW, FAQWindow, 'FAQWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, ChannelsManagementWindow, 'channelsManagementWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, LazyChannelWindow, 'lazyChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False, canClose=False),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, LobbyChannelWindow, 'lobbyChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, ConnectToSecureChannelWindow, 'connectToSecureChannelWindow.swf', ViewTypes.WINDOW, '', MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=True),
     GroupedViewSettings(CONTACTS_ALIASES.CONTACTS_POPOVER, ContactsListPopover, 'contactsListPopover.swf', ViewTypes.WINDOW, 'contactsListPopover', CONTACTS_ALIASES.CONTACTS_POPOVER, ScopeTemplates.WINDOW_VIEWED_MULTISCOPE),
     ViewSettings(MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT, ChannelComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.FIND_CONTACT_VIEW_ALIAS, SearchContactView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.CONTACTS_TREE, ContactsTreeComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.GROUP_RENAME_VIEW_ALIAS, GroupRenameView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.GROUP_CREATE_VIEW_ALIAS, GroupCreateView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.CONTACT_EDIT_NOTE_VIEW_ALIAS, ContactEditNoteView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.CONTACT_CREATE_NOTE_VIEW_ALIAS, ContactCreateNoteView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.GROUP_DELETE_VIEW_ALIAS, GroupDeleteView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(CONTACTS_ALIASES.CONTACTS_SETTINGS_VIEW_ALIAS, ContactsSettingsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_MessengerPackageBusinessHandler(),)


class _MessengerPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((MESSENGER_VIEW_ALIAS.FAQ_WINDOW, self.loadViewByCtxEvent),
         (MESSENGER_VIEW_ALIAS.CHANNEL_MANAGEMENT_WINDOW, self.loadViewByCtxEvent),
         (MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, self.__showLazyChannelWindow),
         (MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, self.__showLobbyChannelWindow),
         (MESSENGER_VIEW_ALIAS.CONNECT_TO_SECURE_CHANNEL_WINDOW, self.loadViewByCtxEvent),
         (CONTACTS_ALIASES.CONTACTS_POPOVER, self.loadViewByCtxEvent))
        super(_MessengerPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showLazyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW
        self.loadViewWithDefName(alias, getViewName(MESSENGER_VIEW_ALIAS.LAZY_CHANNEL_WINDOW, event.ctx.get('clientID')), event.ctx)

    def __showLobbyChannelWindow(self, event):
        alias = MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW
        self.loadViewWithDefName(alias, getViewName(MESSENGER_VIEW_ALIAS.LOBBY_CHANNEL_WINDOW, event.ctx['clientID']), event.ctx)
