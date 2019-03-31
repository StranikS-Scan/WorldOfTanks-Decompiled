# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/JabberPlugin.py
# Compiled at: 2011-06-20 14:33:14
import BigWorld
from Jabber import Client
from adisp import process
from debug_utils import LOG_DEBUG
from functools import partial
from gui.Scaleform.utils.requesters import StatsRequester
from messenger.gui.interfaces import ProtocolPlugin
from messenger.wrappers import ChannelWrapper, MemberWrapper, ChatActionWrapper
from functools import partial

class JabberPlugin(ProtocolPlugin):
    __fakeChannel = ChannelWrapper()

    def __init__(self):
        self.__client = Client.Client()
        self.__mucEntities = {}

    def connect(self):
        settings = getattr(BigWorld.player(), 'serverSettings', {})
        host = settings.get('xmpp_host')
        port = settings.get('xmpp_port')
        if host is None or port is None:
            raise Exception, 'XMPP: Jabber: server host or port is not defined'
        credentials = settings.get('xmpp_credentials', '')
        if credentials:
            self.__processConnect((host, port), credentials)
        return

    def __processConnect(self, host, credentials):
        self.__client.eventConnected += self.onJabberConnected
        self.__client.eventDisconnected += self.onJabberServerDisconnected
        h = (host[0].decode('utf-8'), host[1].decode('utf-8'))
        c = (BigWorld.player().name.decode('utf-8'), credentials.decode('utf-8'))
        self.__client.connect(h, c)

    def disconnect(self):
        for entity in self.__mucEntities.itervalues():
            entity.eventMessage -= self.onJabberMessage
            entity.eventUserOnline -= self.onJabberUserOnline
            entity.eventUserOffline -= self.onJabberUserOffline

        self.__mucEntities.clear()
        self.__client.eventConnected -= self.onJabberConnected
        self.__client.eventDisconnected -= self.onJabberServerDisconnected
        self.__client.disconnect()

    def broadcast(self, cid, message):
        result = False
        entity = self.__mucEntities.get(cid)
        if entity is not None:
            entity.sendMessage(message.decode('utf-8'))
            result = True
        return result

    def onJabberServerDisconnected(self):
        settings = getattr(BigWorld.player(), 'serverSettings', {})
        credentials = (BigWorld.player().name.decode('utf-8'), settings.get('xmpp_credentials', '').decode('utf-8'))
        host = (settings.get('xmpp_host').decode('utf-8'), settings.get('xmpp_port').decode('utf-8'))
        BigWorld.callback(10, partial(self.__client.connect, host, credentials))

    @process
    def __requestClanInfo(self):
        clanInfo = yield StatsRequester().getClanInfo()
        if len(clanInfo) > 1 and clanInfo[1] is not None and len(clanInfo[1]) > 0:
            room = unicode(clanInfo[1].lower(), 'utf-8', errors='ignore')
            self.__joinToClanConference(room)
        return

    def __joinToClanConference(self, room):
        LOG_DEBUG('__joinToClanConference', room)
        self.__fakeChannel = ChannelWrapper(id=hash(room), channelName=room, isSystem=True, flags=0)
        self.channels._addChannel(self.__fakeChannel)
        entity = self.__client.joinConference(room, Client.Client.CLAN_CONFERENCE_NAME)
        self.__receiveMUCEntity(entity)

    def __receiveMUCEntity(self, entity):
        cid = self.__fakeChannel.cid
        self.channels._setJoinedFlag(cid, True)
        self.__mucEntities[cid] = entity
        currentWindow = self._dispatcherProxy._getCurrent(cid)
        if currentWindow.addChannel(self.__fakeChannel):
            if self.__fakeChannel.greeting:
                self.channels.addChannelMessage(cid, self.__fakeChannel.greeting)
        entity.eventMessage += self.onJabberMessage
        entity.eventUserOnline += self.onJabberUserOnline
        entity.eventUserOffline += self.onJabberUserOffline

    def __receiveUserOnline(self, nickName):
        cid = self.__fakeChannel.cid
        uid = hash(nickName)
        if not self.channels.hasExistMemeber(cid, uid):
            member = MemberWrapper(id=uid, nickName=nickName)
            self.channels._addMember(cid, member)
            currentWindow = self._dispatcherProxy._getCurrent(cid)
            page = currentWindow.getChannelPage(cid)
            if page:
                page.addMember(member)

    def __receiveUserOffline(self, nickName):
        cid = self.__fakeChannel.cid
        uid = hash(nickName)
        if self.channels._removeMemeber(cid, uid):
            currentWindow = self._dispatcherProxy._getCurrent(cid)
            page = currentWindow.getChannelPage(cid)
            if page:
                page.removeMember(uid)

    def __receiveMessage(self, nickName, message):
        cid = self.__fakeChannel.cid
        uid = hash(nickName)
        wrapper = ChatActionWrapper(channel=cid, originator=uid, originatorNickName=nickName, data=message)
        currentWindow = self._dispatcherProxy._getCurrent(cid)
        self._dispatcherProxy._filterChain.chainIn(wrapper)
        messageText = currentWindow.addChannelMessage(wrapper)
        if messageText:
            self.channels.addChannelMessage(cid, messageText)

    def onJabberConnected(self):
        LOG_DEBUG('onJabberConnected')
        self.__requestClanInfo()

    def onJabberMessage(self, nickName, message):
        LOG_DEBUG('onJabberMessage')
        self.__receiveMessage(nickName, message)

    def onJabberUserOnline(self, nickName):
        LOG_DEBUG('onJabberUserOnline', nickName)
        self.__receiveUserOnline(nickName)

    def onJabberUserOffline(self, userName):
        LOG_DEBUG('onJabberUserOffline', userName)
        self.__receiveUserOffline(userName)
