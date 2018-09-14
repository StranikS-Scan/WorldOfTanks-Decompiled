# Embedded file name: scripts/client/messenger/gui/Scaleform/view/__init__.py
from messenger.gui.Scaleform.view.BattleChannelView import BattleChannelView
from messenger.gui.Scaleform.view.ChannelComponent import ChannelComponent
from messenger.gui.Scaleform.view.ChannelsManagementWindow import ChannelsManagementWindow
from messenger.gui.Scaleform.view.ConnectToSecureChannelWindow import ConnectToSecureChannelWindow
from messenger.gui.Scaleform.view.FAQWindow import FAQWindow
from messenger.gui.Scaleform.view.LazyChannelWindow import LazyChannelWindow
from messenger.gui.Scaleform.view.LobbyChannelWindow import LobbyChannelWindow
from messenger.gui.Scaleform.view.ContactsWindow import ContactsWindow
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
ACCOUNT_NAME_MIN_CHARS_LENGTH = 2
ACCOUNT_NAME_MAX_CHARS_LENGTH = 24
__all__ = ('BattleChannelView', 'ChannelComponent', 'ChannelsManagementWindow', 'ConnectToSecureChannelWindow', 'FAQWindow', 'LazyChannelWindow', 'LobbyChannelWindow', 'ContactsWindow', 'BaseContactView', 'ContactsListPopover')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CONTACTS_GROUP, 'messenger.gui.Scaleform.data.contacts_cm_handlers', 'SimpleContactsCMHandler')
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.PLAYER_CONTACTS, 'messenger.gui.Scaleform.data.contacts_cm_handlers', 'PlayerContactsCMHandler')
