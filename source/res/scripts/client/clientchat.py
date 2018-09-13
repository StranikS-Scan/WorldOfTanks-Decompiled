# Embedded file name: scripts/client/ClientChat.py
import cPickle
import zlib
import time
from collections import deque
from invites import INVITE_TYPES
import helpers.time_utils as tm
import BigWorld
import Event
import chat_shared
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from chat_shared import CHAT_RESPONSES, CHAT_ACTIONS, CHAT_COMMANDS, parseCommandMessage, ChatCommandError, isCommandMessage, buildChatActionData, ChatError, ChatCommandInCooldown, SYS_MESSAGE_TYPE
from ids_generators import SequenceIDGenerator
from messenger import MessengerEntry
from constants import USER_SEARCH_MODE
g_replayCtrl = None

class ClientChat(object):
    __dataProcessors = ['_ClientChat__dataTimeProcessor', '_ClientChat__inviteDataTimeProcessor', '_ClientChat__systemMessageTimeProcessor']
    __actionHandlers = {CHAT_ACTIONS.receiveInvite.index(): '_ClientChat__onReceiveInvite'}

    def __init__(self):
        raise isinstance(self, BigWorld.Entity) or AssertionError
        self.__chatActionCallbacks = {}
        self._idGen = SequenceIDGenerator()

    def acquireRequestID(self):
        return self._idGen.next()

    def requestSystemChatChannels(self):
        self.__baseChatCommand(CHAT_COMMANDS.requestSystemChatChannels)

    def findChatChannels(self, sample, requestID = None):
        if requestID is None:
            requestID = self.acquireRequestID()
        try:
            self.__baseChatCommand(CHAT_COMMANDS.findChatChannels, stringArg1=sample, ignoreCooldown=False, requestID=requestID)
        except ChatError as ex:
            self._processChatError(CHAT_ACTIONS.requestChannels, 0, ex, requestID=requestID)

        return

    def getChannelInfoById(self, channelId):
        self.__baseChatCommand(CHAT_COMMANDS.getChannelInfoById, int64Arg=channelId)

    def requestChatChannelMembers(self, channelId):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.requestChatChannelMembers)

    def requestChatChannelMembersCount(self, channelId):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.getMembersCount)

    def createChatChannel(self, channelName, password = None):
        try:
            self.__baseChatCommand(CHAT_COMMANDS.createChatChannel, stringArg1=channelName, stringArg2=password if password is not None else '', ignoreCooldown=False)
        except ChatError as ex:
            self._processChatError(CHAT_COMMANDS.createChatChannel, 0, ex)

        return

    def destroyChatChannel(self, channelId):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.destroyChatChannel)

    def enterChat(self, channelId, password = None):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.enterChatChannel, stringArg1=password if password is not None else '')
        return

    def broadcast(self, channelId, message):
        if not len(message) or message.isspace():
            return
        message = message.rstrip()
        if not isCommandMessage(message):
            try:
                self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.broadcast, stringArg1=message, ignoreCooldown=False)
            except ChatError as ex:
                self._processChatError(CHAT_ACTIONS.broadcast, channelId, ex)

        else:
            try:
                command, int64Arg, int16Arg, stringArg1, stringArg2 = parseCommandMessage(message)
                self.__baseChannelChatCommand(channelId, command, int64Arg, int16Arg, stringArg1, stringArg2, ignoreCooldown=False)
            except ChatCommandError as ex:
                self._processChatError(CHAT_ACTIONS.userChatCommand, channelId, ex)

    def leaveChat(self, channelId):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.leaveChatChannel)

    def onChatActionFailure(self, actionData):
        MessengerEntry.g_instance.protos.BW.onChatActionFailure(actionData)

    def onChatAction(self, chatActionData):
        global g_replayCtrl
        if g_replayCtrl is None:
            import BattleReplay
            g_replayCtrl = BattleReplay.g_replayCtrl
        if g_replayCtrl.isRecording:
            g_replayCtrl.cancelSaveCurrMessage()
        elif g_replayCtrl.isPlaying:
            g_replayCtrl.onChatAction(chatActionData)
            return
        for processor in self.__dataProcessors:
            getattr(self, processor)(chatActionData)

        if CHAT_RESPONSES[chatActionData['actionResponse']] != CHAT_RESPONSES.success:
            self.onChatActionFailure(chatActionData)
        else:
            hanlerName = self.__actionHandlers.get(chatActionData['action'], None)
            if hanlerName:
                getattr(self, hanlerName)(chatActionData)
            chId = chatActionData['channel']
            commonCallbacks = self.__getChatActionCallbacks(CHAT_ACTIONS[chatActionData['action']], 0)
            commonCallbacks(chatActionData)
            if chId != 0:
                channelCallbacks = self.__getChatActionCallbacks(CHAT_ACTIONS[chatActionData['action']], chId)
                channelCallbacks(chatActionData)
        return

    def requestLastSysMessages(self):
        self.__baseChatCommand(CHAT_COMMANDS.requestLastSysMessages)

    def findUsers(self, userNamePattern, onlineMode = None, requestID = None):
        if onlineMode is None:
            searchMode = USER_SEARCH_MODE.ALL
        elif onlineMode:
            searchMode = USER_SEARCH_MODE.ONLINE
        else:
            searchMode = USER_SEARCH_MODE.OFFLINE
        self.__baseChatCommand(CHAT_COMMANDS.findUser, int16Arg=searchMode, stringArg1=userNamePattern, requestID=requestID)
        return

    def requestUsersRoster(self, flags = 0):
        self.__baseChatCommand(CHAT_COMMANDS.requestUsersRoster, int16Arg=flags)

    def logVivoxLogin(self):
        self.__baseChatCommand(CHAT_COMMANDS.logVivoxLogin)

    def requestFriendStatus(self, friendID = -1):
        self.__baseChatCommand(CHAT_COMMANDS.requestFriendStatus, int64Arg=friendID)

    def addFriend(self, friendID, friendName):
        self.__baseChatCommand(CHAT_COMMANDS.addFriend, int64Arg=friendID, stringArg1=friendName)

    def createPrivate(self, friendID, friendName):
        self.__baseChatCommand(CHAT_COMMANDS.createPrivate, int64Arg=friendID, stringArg1=friendName)

    def removeFriend(self, friendID):
        self.__baseChatCommand(CHAT_COMMANDS.removeFriend, int64Arg=friendID)

    def addIgnored(self, ignoredID, ignoredName):
        self.__baseChatCommand(CHAT_COMMANDS.addIgnored, int64Arg=ignoredID, stringArg1=ignoredName)

    def removeIgnored(self, ignoredID):
        self.__baseChatCommand(CHAT_COMMANDS.removeIgnored, int64Arg=ignoredID)

    def setMuted(self, mutedID, mutedName):
        self.__baseChatCommand(CHAT_COMMANDS.setMuted, int64Arg=mutedID, stringArg1=mutedName)

    def unsetMuted(self, mutedID):
        self.__baseChatCommand(CHAT_COMMANDS.unsetMuted, int64Arg=mutedID)

    def createPrebattleInvite(self, receiverName, auxText, prebattleID, prebattleType, requestID = None):
        self.__baseInviteCommand(CHAT_COMMANDS.createInvite, INVITE_TYPES.PREBATTLE, receiverName, prebattleID, prebattleType, stringArg2=auxText, requestID=requestID)

    def createBarterInvite(self, receiverName, auxText, itemID, requestID = None):
        self.__baseInviteCommand(CHAT_COMMANDS.createInvite, INVITE_TYPES.BARTER, receiverName, itemID, stringArg2=auxText, requestID=requestID)

    def acceptPrebattleInvite(self, inviteID, requestID = None):
        if requestID is None:
            requestID = self.acquireRequestID()
        self.base.ackCommand(requestID, CHAT_COMMANDS.acceptInvite.index(), time.time(), inviteID, -1)
        return

    def rejectInvite(self, inviteID, requestID = None):
        if requestID is None:
            requestID = self.acquireRequestID()
        self.base.ackCommand(requestID, CHAT_COMMANDS.rejectInvite.index(), time.time(), inviteID, -1)
        return

    def getActiveInvites(self):
        self.__baseInviteCommand(CHAT_COMMANDS.getActiveInvites)

    def getArchiveInvites(self):
        self.__baseInviteCommand(CHAT_COMMANDS.getArchiveInvites)

    def requestVOIPCredentials(self, changePwd = 0):
        self.__baseChatCommand(CHAT_COMMANDS.requestVOIPCredentials, int16Arg=changePwd)

    def subscribeChatAction(self, callback, action, channelId = None):
        cbs = self.__getChatActionCallbacks(action, channelId)
        cbs += callback

    def unsubscribeChatAction(self, callback, action, channelId = None):
        cbs = self.__getChatActionCallbacks(action, channelId)
        cbs -= callback

    def setChatActionsCallbacks(self, callbacks):
        self.__chatActionCallbacks = callbacks

    def sendChannelChatCommand(self, channelID, command, int64Arg = 0, int16Arg = 0, stringArg1 = '', stringArg2 = ''):
        self.__baseChannelChatCommand(channelID, command, int64Arg, int16Arg, stringArg1, stringArg2)

    def _processChatError(self, action, channelId, chatError, requestID = -1):
        if isinstance(chatError, ChatError):
            actionData = chatError.messageArgs if chatError.messageArgs is not None else chatError.message
        else:
            actionData = ''
        chatAction = buildChatActionData(action=action, requestID=requestID, channelId=channelId, originatorNickName=self.name, data=actionData, actionResponse=chatError.response if isinstance(chatError, ChatError) else CHAT_RESPONSES.internalError)
        self.onChatAction(chatAction)
        return

    def __getChatActionCallbacks(self, action, channelId):
        channelId = channelId if channelId is not None else 0
        key = (action, channelId)
        if key not in self.__chatActionCallbacks:
            handlers = self.__chatActionCallbacks[key] = Event.Event()
        else:
            handlers = self.__chatActionCallbacks[key]
        return handlers

    def __receiveStreamedData(self, streamID, data):
        failed = False
        try:
            data = zlib.decompress(data)
            chatMessages = cPickle.loads(data)
        except:
            LOG_CURRENT_EXCEPTION()
            failed = True

        if not failed:
            chIds = sorted(chatMessages.keys(), cmp=lambda x, y: cmp(abs(x), abs(y)))
            for chId in chIds:
                channelQueue = chatMessages.get(chId, deque())
                while True:
                    try:
                        actionData = channelQueue.popleft()
                        self.onChatAction(actionData)
                    except IndexError:
                        break

        self.__baseChatCommand(CHAT_COMMANDS.initAck, int64Arg=streamID, int16Arg=failed)

    def __baseChannelChatCommand(self, channelID, command, int64Arg = 0, int16Arg = 0, stringArg1 = '', stringArg2 = '', ignoreCooldown = True):
        if 0 == channelID:
            LOG_ERROR('Can`t execute chat channel command for channelId: %s' % (channelID,))
        else:
            if chat_shared.isOperationInCooldown(chat_shared.g_chatCooldownData, command):
                if ignoreCooldown:
                    return
                raise ChatCommandInCooldown(command)
            self.__baseChatCommand(command, channelID, int64Arg, int16Arg, stringArg1, stringArg2)

    def __baseChatCommand(self, command, channelID = 0, int64Arg = 0, int16Arg = 0, stringArg1 = '', stringArg2 = '', ignoreCooldown = True, requestID = None):
        if requestID is None:
            requestID = self.acquireRequestID()
        if chat_shared.isOperationInCooldown(chat_shared.g_chatCooldownData, command):
            if not ignoreCooldown:
                raise ChatCommandInCooldown(command)
        self.base.chatCommandFromClient(requestID, command.index(), channelID, int64Arg, int16Arg, stringArg1, stringArg2)
        return

    def __baseInviteCommand(self, command, inviteType = None, receiverName = '', int64Arg = 0, int16Arg = 0, stringArg1 = '', stringArg2 = '', requestID = None):
        if requestID is None:
            requestID = self.acquireRequestID()
        self.base.inviteCommand(requestID, command.index(), inviteType.index() if inviteType is not None else -1, receiverName, int64Arg, int16Arg, stringArg1, stringArg2)
        return

    def __onReceiveInvite(self, chatActionData):
        inviteID = chatActionData['data'].get('id', None)
        receivedAt = chatActionData['data'].get('received_at', None)
        if inviteID is not None and receivedAt is None:
            requestID = self.acquireRequestID()
            self.base.ackCommand(requestID, CHAT_COMMANDS.inviteReceived.index(), time.time(), inviteID, -1)
        return

    def __dataTimeProcessor(self, actionData):
        actionData['time'] = tm.makeLocalServerTime(actionData['time'])
        actionData['sentTime'] = tm.makeLocalServerTime(actionData['sentTime'])

    def __inviteDataTimeProcessor(self, actionData):
        isInviteAction = CHAT_ACTIONS[actionData['action']] in (CHAT_ACTIONS.createInvite, CHAT_ACTIONS.receiveInvite, CHAT_ACTIONS.receiveArchiveInvite)
        if isInviteAction:
            if actionData.has_key('data'):
                inviteData = actionData['data']
                if 'sent_at' in inviteData:
                    inviteData['sent_at'] = tm.utcToLocalDatetime(tm.makeLocalServerDatetime(inviteData['sent_at']))
                if 'received_at' in inviteData:
                    inviteData['received_at'] = tm.utcToLocalDatetime(tm.makeLocalServerDatetime(inviteData['received_at']))
                if 'processed_at' in inviteData:
                    inviteData['processed_at'] = tm.utcToLocalDatetime(tm.makeLocalServerDatetime(inviteData['processed_at']))

    def __systemMessageTimeProcessor(self, actionData):
        isSystemMessage = CHAT_ACTIONS[actionData['action']] in (CHAT_ACTIONS.personalSysMessage, CHAT_ACTIONS.sysMessage)
        if isSystemMessage:
            if actionData.has_key('data'):
                messageData = actionData['data']
                messageType = messageData['type']
                if 'created_at' in messageData:
                    messageData['created_at'] = tm.makeLocalServerDatetime(messageData['created_at'])
                if 'finished_at' in messageData:
                    messageData['finished_at'] = tm.makeLocalServerDatetime(messageData['finished_at'])
                if 'started_at' in messageData:
                    messageData['started_at'] = tm.makeLocalServerDatetime(messageData['started_at'])
                if messageType == SYS_MESSAGE_TYPE.serverReboot.index():
                    messageData['data'] = tm.makeLocalServerDatetime(messageData['data'])
                elif messageType == SYS_MESSAGE_TYPE.battleResults.index():
                    messageData['data']['arenaCreateTime'] = tm.makeLocalServerTime(messageData['data']['arenaCreateTime'])
                elif messageType == SYS_MESSAGE_TYPE.goldReceived.index():
                    messageData['data']['date'] = tm.makeLocalServerTime(messageData['data']['date'])
                elif messageType in (SYS_MESSAGE_TYPE.accountTypeChanged.index(),
                 SYS_MESSAGE_TYPE.premiumBought.index(),
                 SYS_MESSAGE_TYPE.premiumExtended.index(),
                 SYS_MESSAGE_TYPE.premiumExpired.index()):
                    if 'expiryTime' in messageData['data']:
                        messageData['data']['expiryTime'] = tm.makeLocalServerTime(messageData['data']['expiryTime'])
