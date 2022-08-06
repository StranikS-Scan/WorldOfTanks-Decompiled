# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/gameface/channels/GFChannelController.py
import logging
import typing
from gui import SystemMessages
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import MessengerEvent
from messenger.formatters.chat_message import LobbyMessageBuilder
from messenger.formatters.users_messages import getBroadcastIsInCoolDownMessage
from messenger.gui.interfaces import IChannelController
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.bw_chat2.wrappers import UnitMessageVO
from messenger_common_chat2 import MESSENGER_LIMITS
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from messenger.proto.entities import ChannelEntity
    from typing import List, Union
    from messenger.gui.gameface.view.gf_channel_view_interface import GFChannelViewInterface

class GFChannelController(IChannelController):

    def __init__(self, channel):
        self.__channel = None
        self.__mBuilder = LobbyMessageBuilder()
        self._isNotifyInit = False
        self.__channel = channel
        self.__subscribedViews = list()
        self._addListeners()
        self.fireInitEvent()
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def proto(self):
        return None

    def deactivate(self, entryClosing=False):
        self._removeListeners()
        self.removeView()

    def clear(self):
        self._removeListeners()
        self.removeView()

    def removeView(self):
        self.__subscribedViews = list()

    def fireInitEvent(self):
        if not self._isNotifyInit:
            self._fireInitEvent()
            self._isNotifyInit = True

    def setHistory(self, history):
        if self.__channel:
            self.__channel.clearHistory()
            for message in history:
                self.addMessage(message, isHistoryMessage=True)

    def getHistory(self):
        if self.__channel is None:
            return []
        else:
            self._getChat().addHistory()
            history = self.__channel.getHistory()
            return history

    def canSendMessage(self):
        if self.__channel is None:
            return (False, '')
        else:
            result, errorMsg = True, ''
            if self._getChat().isBroadcastInCooldown():
                result, errorMsg = False, getBroadcastIsInCoolDownMessage(MESSENGER_LIMITS.BROADCASTS_FROM_CLIENT_COOLDOWN_SEC)
            return (result, errorMsg)

    def getChannel(self):
        return self.__channel

    def getClientID(self):
        return self.__channel.getClientID() if self.__channel else None

    def sendMessage(self, message):
        result, errorMsg = self.canSendMessage()
        if result:
            self._broadcast(message)
        else:
            SystemMessages.pushI18nMessage(errorMsg, type=SystemMessages.SM_TYPE.Error)
        return result

    def sendCommand(self, command):
        self._getChat().send(command)

    def addMessage(self, message, doFormatting=True, isHistoryMessage=False):
        if self.__channel:
            if isinstance(message, (str, unicode)):
                message = UnitMessageVO(0, -1, message, u'')
            if doFormatting:
                message.text = self.__formatText(message.text)
            self.__channel.addMessage(message)
            return self.__addMessageToView(message, isHistoryMessage)
        return False

    def addToSubscribedList(self, view):
        if view not in self.__subscribedViews:
            self.__subscribedViews.append(view)
            if self.__channel:
                view.onChannelControllerInited(self)

    def removeFromSubscribedList(self, view):
        if view in self.__subscribedViews:
            self.__subscribedViews.remove(view)

    def getSubscribedViews(self):
        return self.__subscribedViews

    def _addListeners(self):
        self.__channel.onConnectStateChanged += self._onConnectStateChanged

    def _removeListeners(self):
        self.__channel.onConnectStateChanged -= self._onConnectStateChanged

    def _onConnectStateChanged(self, channel):
        if channel == self.__channel:
            if channel.isJoined():
                self.fireInitEvent()
            else:
                self.removeView()

    def _fireInitEvent(self):
        g_eventBus.handleEvent(MessengerEvent(MessengerEvent.PRB_CHANNEL_CTRL_INITED, {'prbType': self.__channel.getPrebattleType(),
         'controller': self}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__notifyViews()

    def _getChat(self):
        return self.proto.unitChat

    def _broadcast(self, message):
        self._getChat().broadcast(message)

    def __notifyViews(self):
        for view in self.__subscribedViews:
            view.onChannelControllerInited(self)

    def __addMessageToView(self, message, isHistoryMessage=False):
        isShowing = False
        for view in self.__subscribedViews:
            isShowing |= view.addMessageToView(message, isHistoryMessage)

        return isShowing

    def __formatText(self, text):
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&apos;', "'")
        return text.replace('&quot;', '"')
