# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/xmpp/messages/provider.py
from messenger.proto.events import g_messengerEvents
from messenger.proto.xmpp import find_criteria
from messenger.proto.xmpp.errors import createChatBanError
from messenger.proto.xmpp.extensions import chat as chat_ext
from messenger.proto.xmpp.find_criteria import XMPPChannelByJIDFindCriteria, XMPPChannelByNameFindCriteria
from messenger.proto.xmpp.gloox_wrapper import ClientHolder
from messenger.storage import storage_getter

class ChatProvider(ClientHolder):
    __slots__ = ()

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def clear(self):
        pass

    def release(self):
        pass

    def suspend(self):
        pass

    def restore(self, jid, state):
        return False

    def getChannelByJID(self, jid):
        return self.channelsStorage.getChannelByCriteria(XMPPChannelByJIDFindCriteria(jid))

    def getChannelByName(self, jid):
        return self.channelsStorage.getChannelByCriteria(XMPPChannelByNameFindCriteria(jid))

    def hasChannel(self, jid):
        return self.getChannelByJID(jid) is not None

    def setUserAction(self, actionID, contact):
        pass

    def sendMessage(self, jid, body, filters):
        _, exists = self._searchChannel(jid)
        if exists is None:
            return
        elif self.playerCtx.isBanned(components=exists.getBanComponent()):
            error = createChatBanError(self.playerCtx.getBanInfo())
            if error:
                g_messengerEvents.onErrorReceived(error)
            return
        else:
            self._repeatMessage(exists, body, filters)
            self.client().sendMessage(chat_ext.ChatMessageHolder(exists.getMessageType(), jid, msgBody=body))
            return

    def addMessage(self, jid, message):
        _, exists = self._searchChannel(jid)
        if exists is None:
            return
        else:
            if message.body:
                g_messengerEvents.channels.onMessageReceived(message, exists)
            return

    def handlePresence(self, jid, resource):
        return False

    def handleIQ(self, iqID, iqType, pyGlooxTag):
        return False

    def _searchChannel(self, jid, name=''):
        raise NotImplementedError

    def _repeatMessage(self, channel, body, filters):
        pass

    def _addChannel(self, channel, byAction=False, isJoined=True):
        result = self.channelsStorage.addChannel(channel)
        if result:
            g_messengerEvents.channels.onChannelInited(channel)
        if byAction:
            g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
        channel.setJoined(isJoined)
        channel.setStored(True)
        return result

    def _removeChannel(self, channel):
        result = self.channelsStorage.removeChannel(channel, clear=False)
        if result:
            g_messengerEvents.channels.onChannelDestroyed(channel)
            channel.clear()
        return result

    def _getChannelsIterator(self, msgType):
        channels = self.channelsStorage.getChannelsByCriteria(find_criteria.XMPPChannelFindCriteria(msgType))
        for channel in channels:
            yield channel
