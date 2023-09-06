# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/messengerBar/ChannelListContextMenuHandler.py
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import BaseAppealCMLobbyChatHandler
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ChannelCarouselEvent

class CHANNEL(object):
    CLOSE_CURRENT = 'closeCurrent'
    MINIMIZE_ALL = 'minimizeAll'
    CLOSE_ALL_EXCEPT_CURRENT = 'closeAllExceptCurrent'


class ChannelListContextMenuHandler(AbstractContextMenuHandler, EventSystemEntity):

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

    def _getHandlers(self):
        handlers = {CHANNEL.MINIMIZE_ALL: 'minimizeAll',
         CHANNEL.CLOSE_CURRENT: 'closeCurrent',
         CHANNEL.CLOSE_ALL_EXCEPT_CURRENT: 'closeAllExceptCurrent'}
        return handlers

    def _generateOptions(self, ctx=None):
        return [self._makeItem(CHANNEL.MINIMIZE_ALL, MENU.contextmenu('messenger/minimizeAll')), self._makeItem(CHANNEL.CLOSE_CURRENT, MENU.contextmenu('messenger/closeCurrent'), {'enabled': self._canClose}), self._makeItem(CHANNEL.CLOSE_ALL_EXCEPT_CURRENT, MENU.contextmenu('messenger/closeAllExceptCurrent'))]


class AppealChannelListContextMenuHandler(ChannelListContextMenuHandler, BaseAppealCMLobbyChatHandler):

    def _initFlashValues(self, ctx):
        ChannelListContextMenuHandler._initFlashValues(self, ctx)
        BaseAppealCMLobbyChatHandler._initFlashValues(self, ctx)

    def _clearFlashValues(self):
        ChannelListContextMenuHandler._clearFlashValues(self)
        BaseAppealCMLobbyChatHandler._clearFlashValues(self)

    def _getHandlers(self):
        handlers = ChannelListContextMenuHandler._getHandlers(self)
        handlers.update(BaseAppealCMLobbyChatHandler._getHandlers(self))
        return handlers

    def _generateOptions(self, ctx=None):
        options = ChannelListContextMenuHandler._generateOptions(self, ctx)
        options.extend(BaseAppealCMLobbyChatHandler._generateOptions(self, ctx))
        return options
