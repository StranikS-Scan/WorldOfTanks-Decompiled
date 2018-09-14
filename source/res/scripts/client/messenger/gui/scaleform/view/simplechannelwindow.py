# Embedded file name: scripts/client/messenger/gui/Scaleform/view/SimpleChannelWindow.py
from gui.shared.events import FocusEvent
from messenger.gui.Scaleform.meta.BaseChannelWindowMeta import BaseChannelWindowMeta
from gui.shared import events, EVENT_BUS_SCOPE
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS
from messenger.inject import channelsCtrlProperty

class SimpleChannelWindow(BaseChannelWindowMeta):

    def __init__(self, ctx):
        super(SimpleChannelWindow, self).__init__()
        self._clientID = ctx.get('clientID')
        self._controller = self.channelsCtrl.getController(self._clientID)
        if self._controller is None:
            raise ValueError, 'Controller for lobby channel by clientID={0:1} is not found'.format(self._clientID)
        return

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self._clientID}))

    @channelsCtrlProperty
    def channelsCtrl(self):
        return None

    def onWindowClose(self):
        chat = self.chat
        if chat:
            chat.close()
        self.destroy()

    def onWindowMinimize(self):
        chat = self.chat
        if chat:
            chat.minimize()
        self.destroy()

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return self._clientID

    def getChannelID(self):
        return self._controller.getChannel().getID()

    def getProtoType(self):
        return self._controller.getChannel().getProtoType()

    @property
    def chat(self):
        chat = None
        if MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT in self.components:
            chat = self.components[MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT]
        return chat

    def _populate(self):
        super(SimpleChannelWindow, self)._populate()
        channel = self._controller.getChannel()
        channel.onChannelInfoUpdated += self.__ce_onChannelInfoUpdated
        self.as_setTitleS(channel.getFullName())
        self.as_setCloseEnabledS(not channel.isSystem())

    def _dispose(self):
        if self._controller is not None:
            channel = self._controller.getChannel()
            if channel is not None:
                channel.onChannelInfoUpdated -= self.__ce_onChannelInfoUpdated
            self._controller = None
        super(SimpleChannelWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            self._controller.setView(viewPy)

    def __ce_onChannelInfoUpdated(self, channel):
        self.as_setTitleS(channel.getFullName())
