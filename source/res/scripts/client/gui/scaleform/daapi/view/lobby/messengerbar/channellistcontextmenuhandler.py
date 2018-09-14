# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/ChannelListContextMenuHandler.py
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.managers.context_menu.AbstractContextMenuHandler import AbstractContextMenuHandler

class CHANNEL(object):
    CLOSE_CURRENT = 'closeCurrent'
    MINIMIZE_ALL = 'minimizeAll'
    CLOSE_ALL_EXCEPT_CURRENT = 'closeAllExceptCurrent'


class ChannelListContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx = None):
        super(ChannelListContextMenuHandler, self).__init__(cmProxy, ctx, {CHANNEL.MINIMIZE_ALL: 'minimizeAll',
         CHANNEL.CLOSE_CURRENT: 'closeCurrent',
         CHANNEL.CLOSE_ALL_EXCEPT_CURRENT: 'closeAllExceptCurrent'})

    def closeCurrent(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.CLOSE_BUTTON_CLICK, self._clientID), scope=EVENT_BUS_SCOPE.LOBBY)

    def minimizeAll(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.MINIMIZE_ALL_CHANNELS, None), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def closeAllExceptCurrent(self):
        self.fireEvent(ChannelCarouselEvent(self, ChannelCarouselEvent.CLOSE_ALL_EXCEPT_CURRENT, self._clientID), scope=EVENT_BUS_SCOPE.LOBBY)

    def _initFlashValues(self, ctx):
        self._clientID = int(ctx.clientID)
        self._canClose = bool(ctx.canClose)

    def _clearFlashValues(self):
        self._clientID = None
        self._canClose = None
        return

    def _generateOptions(self, ctx = None):
        return [self._makeItem(CHANNEL.MINIMIZE_ALL, MENU.contextmenu('messenger/minimizeAll')),
         self._makeSeparator(),
         self._makeItem(CHANNEL.CLOSE_CURRENT, MENU.contextmenu('messenger/closeCurrent'), {'enabled': self._canClose}),
         self._makeSeparator(),
         self._makeItem(CHANNEL.CLOSE_ALL_EXCEPT_CURRENT, MENU.contextmenu('messenger/closeAllExceptCurrent'))]
