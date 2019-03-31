# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/ChannelsManager.py
# Compiled at: 2011-07-13 19:55:29
import constants
import BigWorld
from chat_shared import CHAT_ACTIONS, CHAT_RESPONSES
from collections import defaultdict, deque
from debug_utils import deprecated
from messenger import VISIBLE_MESSAGE_MAX_LENGTH
from messenger.common import MessangerSubscriber
from messenger.exeptions import ChannelNotFound
from messenger.wrappers import ChatActionWrapper, ChannelWrapper, MemberWrapper
import Event
import time

def _messageDequeFactory():
    return deque([], VISIBLE_MESSAGE_MAX_LENGTH)


def _channelFactory():
    return ChannelWrapper()


def _memberFactory():
    return []


class CREATE_CHANNEL_RESULT(object):
    doRequest, activeChannelLimitReached = range(2)


class ChannelsManager(MessangerSubscriber):
    __channelMap = defaultdict(_channelFactory)
    __channelMessages = defaultdict(_messageDequeFactory)
    __memberMap = defaultdict(_memberFactory)
    __creationChannelInfo = {}

    def __init__(self):
        MessangerSubscriber.__init__(self)
        self.__eventManager = Event.EventManager()
        self.onRequestChannelsComplete = Event.Event(self.__eventManager)
        self.onFindChannelsFailed = Event.Event(self.__eventManager)
        self.onConnectingToSecureChannel = Event.Event(self.__eventManager)
        self.onChannelRefresh = Event.Event(self.__eventManager)
        self.onReceiveLazyChannels = Event.Event(self.__eventManager)
        self.onJoinedToChannel = Event.Event(self.__eventManager)
        self._responseHandlers = {CHAT_RESPONSES.commandInCooldown: '_ChannelsManager__onCommandInCooldown'}

    def subscribeToActions(self):
        self.subscribeAction(self.onRequestChannels, CHAT_ACTIONS.requestChannels)
        self.subscribeAction(self.onRequestChannelMembers, CHAT_ACTIONS.requestMembers)
        self.subscribeAction(self.onChannelInfoUpdated, CHAT_ACTIONS.channelInfoUpdated)
        self.subscribeAction(self.onChatChannelCreated, CHAT_ACTIONS.createChannel)

    def requestSystemChannels(self):
        """
        Request system channels from server.
        To process the response through subscribing
        BigWorld.player().subscribeChatAction
        """
        self.subscribeAction(self.onRequestSystemChannels, CHAT_ACTIONS.requestChannels)
        BigWorld.player().requestSystemChatChannels()

    def joinToSystemChannels(self):
        """
        Request system channels from server and join to received channels.
        To process the response through subscribing
        BigWorld.player().subscribeChatAction
        """
        self.subscribeAction(self.onRequestSystemChannelsForJoin, CHAT_ACTIONS.requestChannels)
        BigWorld.player().requestSystemChatChannels()

    def requestChannelMembers(self, cid):
        """
        Request to the server about the members of this channel.
        @param cid: channel id
        """
        BigWorld.player().requestChatChannelMembers(cid)

    def joinToChannel(self, cid, password=None, selected=False):
        """
        Request to the server on the current player's accession to the channel.
        @param cid: channel id
        @param password: channel password
        @param selected: is activate channel tab
        """
        channel = self.getChannel(cid)
        if not channel:
            raise ChannelNotFound(cid)
        channel.selected = selected
        if channel.joined:
            return
        if channel and channel.isSecured and not password:
            self.onConnectingToSecureChannel(channel)
            return
        BigWorld.player().enterChat(cid, password)

    def exitFromChannel(self, cid):
        """
        Request to the server on the current player leave channel.
        @param cid: channel id
        """
        BigWorld.player().leaveChat(cid)

    def createChannel(self, name, password=None):
        """
        Request to the server creating channel with name and
        password (optional, need for secure channels).
        @param name: channel name
        @param password: channel password
        """
        if self.isActiveChannelLimitReached():
            return CREATE_CHANNEL_RESULT.activeChannelLimitReached
        if name.startswith('#'):
            name = name[1:]
        if password:
            self.__creationChannelInfo[name] = password
        BigWorld.player().createChatChannel(name, password)
        return CREATE_CHANNEL_RESULT.doRequest

    def findChannels(self, token, requestID=None):
        """
        Search on a server channels by token.
        Note: to be excluded channels in which the player is already connected.
        @param token: word which is searched in name of channels
        @param requestID: unique id to search request
        """
        BigWorld.player().findChatChannels(token, requestID=requestID)

    def onRequestChannels(self, chatAction, isSystem=False, join=False, selected=False):
        chatActionDict = dict(chatAction)
        data = chatActionDict.get('data', [])
        requestID = chatActionDict.get('requestID', [])
        channels = set()
        lazy = set()
        for channelData in data:
            channel = ChannelWrapper(**dict(channelData))
            channels.add(channel)
            cid = channel.cid
            if channel.lazy:
                channel.hidden = self.__hiddenAttrForLazyChannels.get(channel.lazy, False)
                lazy.add(channel)
            self.__channelMap[cid] = self.__channelMap[cid].update(channel)
            if join:
                self.joinToChannel(cid, selected=selected)

        self.onRequestChannelsComplete(requestID, channels)
        if len(lazy) > 0:
            self.onReceiveLazyChannels(lazy)

    def onRequestSystemChannels(self, chatAction):
        self.onRequestChannels(chatAction, isSystem=True, join=False)
        self.unsubscribeActionByName(self, 'onRequestSystemChannels', CHAT_ACTIONS.requestChannels)

    def onRequestSystemChannelsForJoin(self, chatAction):
        self.onRequestChannels(chatAction, isSystem=True, join=True, selected=True)
        self.unsubscribeActionByName(self, 'onRequestSystemChannelsForJoin', CHAT_ACTIONS.requestChannels)

    def onRequestPrebattleChannelForJoin(self, chatAction):
        self.onRequestChannels(chatAction, isSystem=True, join=True, selected=True)
        self.unsubscribeActionByName(self, 'onRequestPrebattleChannelForJoin', CHAT_ACTIONS.requestChannels)

    def onRequestChannelMembers(self, chatAction):
        wrapper = ChatActionWrapper(**dict(chatAction))
        cid = wrapper.channel
        for memberData in wrapper.data:
            member = MemberWrapper(**dict(memberData))
            if member not in self.__memberMap[cid]:
                self.__memberMap[cid].append(member)

    def onChannelInfoUpdated(self, chatAction):
        result = chatAction['data'] if chatAction.has_key('data') else {}
        channel = ChannelWrapper(**result)
        cid = channel.cid
        self.__channelMap[cid] = self.__channelMap[cid].update(channel)
        self.onChannelRefresh(self.__channelMap[cid])

    def onChatChannelCreated(self, chatAction):
        """
        Event handler. Channel is created.
        """
        result = chatAction['data'] if chatAction.has_key('data') else {}
        channel = ChannelWrapper(**dict(result))
        cid = channel.cid
        self.__channelMap[cid] = self.__channelMap[cid].update(channel)
        password = None
        if self.__creationChannelInfo.has_key(channel.channelName):
            password = self.__creationChannelInfo.pop(channel.channelName)
        self.joinToChannel(cid, password=password, selected=True)
        return

    def __onCommandInCooldown(self, actionResponse, chatAction):
        data = chatAction.get('data', {'command': None,
         'cooldownPeriod': -1})
        result = False
        if data['command'] == 'findChatChannels':
            result = True
            self.onFindChannelsFailed(chatAction.get('requestID', -1), actionResponse, data)
        return result

    def addChannelMessage(self, cid, message):
        self.__channelMessages[cid].append(message)

    def getChannelMessages(self, cid):
        return self.__channelMessages[cid]

    def getChannelList(self, joined=True, lazy=False, isBattle=False):
        return filter(lambda channel: (channel.joined == joined or lazy is True and channel.lazy != 0) and not channel.hidden and channel.isBattle == isBattle, self.__channelMap.values())

    def getLazyChannelList(self, joined=None):
        return filter(lambda channel: channel.lazy != 0 and (joined is None or channel.joined == joined), self.__channelMap.values())

    def getPrebattleChannelList(self):
        return filter(lambda channel: channel.isPrebattle and not channel.waitingDestroyedEvent, self.__channelMap.values())

    def getWaitinigToDestroyChannelList(self):
        return filter(lambda channel: channel.waitingDestroyedEvent, self.__channelMap.values())

    def getChannelCount(self, joined=True, isBattle=False):
        return len(self.getChannelList(joined=joined, isBattle=isBattle))

    def _addChannel(self, channel):
        old = self.__channelMap[channel.cid]
        self.__channelMap[channel.cid] = old._replace(**channel._asdict())

    def _removeChannel(self, cid, clearChannelInfo=True, waitingDestroyedEvent=False):
        if not clearChannelInfo:
            forceClearChannelInfo = self.isBattle(cid)
            if forceClearChannelInfo:
                if self.__channelMap.has_key(cid):
                    self.__channelMap.pop(cid)
            else:
                self._setJoinedFlag(cid, False)
                self.__channelMap[cid].waitingDestroyedEvent = waitingDestroyedEvent
            if self.__memberMap.has_key(cid):
                self.__memberMap.pop(cid)
            self.__channelMessages.has_key(cid) and self.__channelMessages.pop(cid)

    def _setJoinedFlag(self, cid, flag):
        self.__channelMap[cid].joined = flag
        if flag:
            self.__channelMap[cid].joinedTime = time.time()
        self.__channelMessages[cid].clear()

    def getMemberCount(self, cid):
        return len(self.__memberMap[cid])

    def getMemberList(self, cid):
        return self.__memberMap[cid]

    @deprecated
    def getMemberIdByName(self, cid, nickName):
        for member in self.__memberMap[cid]:
            if member.nickName == nickName:
                return member.uid

        return None

    def hasExistMemeber(self, cid, uid):
        return MemberWrapper(id=uid) in self.__memberMap[cid]

    def _addMember(self, cid, member):
        if member not in self.__memberMap[cid]:
            self.__memberMap[cid].append(member)

    def _addMembers(self, cid, members):
        filtered = filter(lambda member: member not in self.__memberMap[cid], members)
        if len(filtered) > 0:
            self.__memberMap[cid].extend(filtered)
            return True
        return False

    def _removeMemeber(self, cid, uid):
        member = MemberWrapper(id=uid)
        if member in self.__memberMap[cid]:
            self.__memberMap[cid].remove(member)
            return True
        return False

    def _removeMembers(self, cid, members):
        filtered = filter(lambda member: member in self.__memberMap[cid], members)
        if len(filtered) > 0:
            for member in filtered:
                self.__memberMap[cid].remove(member)

            return True
        return False

    def _setMemberStatus(self, cid, uid, status):
        if not self.__memberMap.has_key(cid):
            return
        member = MemberWrapper(id=uid)
        if member in self.__memberMap[cid]:
            index = self.__memberMap[cid].index(member)
            self.__memberMap[cid][index].status = status

    def getNickName(self, cid, uid):
        member = MemberWrapper(id=uid)
        if member in self.__memberMap[cid]:
            index = self.__memberMap[cid].index(member)
            return self.__memberMap[cid][index].nickName

    def getChannel(self, cid):
        if self.__channelMap.has_key(cid):
            return self.__channelMap[cid]
        else:
            return None

    def isActiveChannelLimitReached(self):
        chlist = self.getChannelList(joined=True, isBattle=False)
        return constants.USER_ACTIVE_CHANNELS_LIMIT < len(chlist)

    def clear(self):
        self.__channelMap.clear()
        self.__memberMap.clear()
        self.__channelMessages.clear()
        self.__creationChannelInfo.clear()
        self.__eventManager.clear()

    def isReadOnly(self, cid):
        return self.__channelMap[cid].isReadOnly

    def isSystem(self, cid):
        return self.__channelMap[cid].isSystem

    def isBattle(self, cid):
        return self.__channelMap[cid].isBattle

    def isLazyChannel(self, cid):
        return self.__channelMap[cid].lazy

    __hiddenAttrForLazyChannels = {}

    def getLazyChannelIdByClientIdx(self, clientIdx):
        for channel in self.__channelMap.itervalues():
            if channel.lazy == clientIdx:
                return channel.cid

        return None

    def exitFromAllLazyChannels(self):
        for channel in self.getLazyChannelList(joined=True):
            self.exitFromChannel(channel.cid)

    def setIsLazyChannelHidden(self, clientIdx, flag):
        result = None
        self.__hiddenAttrForLazyChannels[clientIdx] = flag
        for channel in self.__channelMap.itervalues():
            if channel.lazy == clientIdx:
                if channel.hidden != flag:
                    channel.hidden = flag
                    result = channel.cid
                break

        return result
