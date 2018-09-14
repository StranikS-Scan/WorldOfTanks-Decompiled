# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/__init__.py
from gui.Scaleform.daapi.view.lobby.messengerBar.MessengerBar import MessengerBar
from gui.Scaleform.daapi.view.lobby.messengerBar.ChannelCarousel import ChannelCarousel
from gui.Scaleform.daapi.view.lobby.messengerBar.NotificationListButton import NotificationListButton
from gui.Scaleform.daapi.view.lobby.messengerBar.ContactsListButton import ContactsListButton
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.managers.context_menu import ContextMenuManager
__all__ = ['MessengerBar',
 'ChannelCarousel',
 'NotificationListButton',
 'ContactsListButton']
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.CHANNEL_LIST, 'gui.Scaleform.daapi.view.lobby.messengerBar.ChannelListContextMenuHandler', 'ChannelListContextMenuHandler')
