# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/view/lobby/SimpleChannelWindow.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.events import FocusEvent
from messenger.gui.Scaleform.meta.ChannelWindowMeta import ChannelWindowMeta
from gui.shared import events, EVENT_BUS_SCOPE
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.inject import channelsCtrlProperty
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter

class SimpleChannelWindow(ChannelWindowMeta):

    def __init__(self, ctx):
        super(SimpleChannelWindow, self).__init__()
        self._clientID = ctx.get('clientID')
        self._controller = self.channelsCtrl.getController(self._clientID)
        if self._controller is None:
            raise ValueError('Controller for lobby channel by clientID={0:1} is not found'.format(self._clientID))
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

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
        channel.onConnectStateChanged += self.__ce_onConnectStateChanged
        self.as_setTitleS(channel.getFullName())
        self.as_setCloseEnabledS(not channel.isSystem())
        self.__checkConnectStatus()

    def _dispose(self):
        if self._controller is not None:
            channel = self._controller.getChannel()
            if channel is not None:
                channel.onChannelInfoUpdated -= self.__ce_onChannelInfoUpdated
                channel.onConnectStateChanged -= self.__ce_onConnectStateChanged
            self._controller = None
        super(SimpleChannelWindow, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            self._controller.setView(viewPy)

    def __ce_onChannelInfoUpdated(self, channel):
        self.as_setTitleS(channel.getFullName())

    def __ce_onConnectStateChanged(self, _):
        self.__checkConnectStatus()

    def __checkConnectStatus(self):
        if self._controller.getChannel().isJoined():
            self.as_hideWaitingS()
        else:
            self.as_showWaitingS(backport.text(R.strings.waiting.messenger.subscribe()), {})
