# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientChat.py
# Compiled at: 2011-11-15 15:15:07
import cPickle
import zlib
import time
from collections import deque
from invites import INVITE_TYPES
import helpers.time_utils as tm
import BigWorld
import Event
import chat_shared
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_RF, LOG_ERROR
from chat_shared import CHAT_RESPONSES, CHAT_ACTIONS, CHAT_COMMANDS, parseCommandMessage, ChatCommandError, isCommandMessage, buildChatActionData, ChatError, ChatCommandInCooldown, SYS_MESSAGE_TYPE
from ids_generators import SequenceIDGenerator
from messenger.gui import MessengerDispatcher
from constants import USER_SEARCH_MODE

class ClientChat(object):
    __dataProcessors = ['_ClientChat__dataTimeProcessor', '_ClientChat__inviteDataTimeProcessor', '_ClientChat__systemMessageTimeProcessor']
    __actionHandlers = {CHAT_ACTIONS.receiveInvite.index(): '_ClientChat__onReceiveInvite'}

    def __init__(self):
        assert isinstance(self, BigWorld.Entity)
        self.__chatActionCallbacks = {}
        self._idGen = SequenceIDGenerator()

    def acquireRequestID(self):
        return self._idGen.next()

    def requestSystemChatChannels(self):
        self.__baseChatCommand(CHAT_COMMANDS.requestSystemChatChannels)

    def findChatChannels(self, sample, requestID=None):
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

    def createChatChannel(self, channelName, password=None):
        try:
            self.__baseChatCommand(CHAT_COMMANDS.createChatChannel, stringArg1=channelName, stringArg2=password if password is not None else '', ignoreCooldown=False)
        except ChatError as ex:
            self._processChatError(CHAT_COMMANDS.createChatChannel, 0, ex)

        return

    def destroyChatChannel(self, channelId):
        self.__baseChannelChatCommand(channelId, CHAT_COMMANDS.destroyChatChannel)

    def enterChat(self, channelId, password=None):
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
        MessengerDispatcher.g_instance.onChatActionFailure(actionData)

    def onChatAction(self, chatActionData):
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

    def findUsers(self, userNamePattern, onlineMode=None, requestID=None):
        if onlineMode is None:
            searchMode = USER_SEARCH_MODE.ALL
        elif onlineMode:
            searchMode = USER_SEARCH_MODE.ONLINE
        else:
            searchMode = USER_SEARCH_MODE.OFFLINE
        self.__baseChatCommand(CHAT_COMMANDS.findUser, int16Arg=searchMode, stringArg1=userNamePattern, requestID=requestID)
        return

    def requestUsersRoster(self, flags=0):
        self.__baseChatCommand(CHAT_COMMANDS.requestUsersRoster, int16Arg=flags)

    def logVivoxLogin(self):
        self.__baseChatCommand(CHAT_COMMANDS.logVivoxLogin)

    def requestFriendStatus(self, friendID=-1):
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

    def createPrebattleInvite(self, receiverName, auxText, prebattleID, prebattleType, requestID=None):
        self.__baseInviteCommand(CHAT_COMMANDS.createInvite, INVITE_TYPES.PREBATTLE, receiverName, prebattleID, prebattleType, stringArg2=auxText, requestID=requestID)

    def createBarterInvite(self, receiverName, auxText, itemID, requestID=None):
        self.__baseInviteCommand(CHAT_COMMANDS.createInvite, INVITE_TYPES.BARTER, receiverName, itemID, stringArg2=auxText, requestID=requestID)

    def acceptPrebattleInvite(self, inviteID, requestID=None):
        if requestID is None:
            requestID = self.acquireRequestID()
        self.base.ackCommand(requestID, CHAT_COMMANDS.acceptInvite.index(), time.time(), inviteID, -1)
        return

    def rejectInvite(self, inviteID, requestID=None):
        if requestID is None:
            requestID = self.acquireRequestID()
        self.base.ackCommand(requestID, CHAT_COMMANDS.rejectInvite.index(), time.time(), inviteID, -1)
        return

    def getActiveInvites(self):
        self.__baseInviteCommand(CHAT_COMMANDS.getActiveInvites)

    def getArchiveInvites(self):
        self.__baseInviteCommand(CHAT_COMMANDS.getArchiveInvites)

    def requestVOIPCredentials(self):
        self.__baseChatCommand(CHAT_COMMANDS.requestVOIPCredentials)

    def subscribeChatAction(self, callback, action, channelId=None):
        cbs = self.__getChatActionCallbacks(action, channelId)
        cbs += callback

    def unsubscribeChatAction(self, callback, action, channelId=None):
        cbs = self.__getChatActionCallbacks(action, channelId)
        cbs -= callback

    def setChatActionsCallbacks(self, callbacks):
        self.__chatActionCallbacks = callbacks

    def sendChannelChatCommand(self, channelID, command, int64Arg=0, int16Arg=0, stringArg1='', stringArg2=''):
        self.__baseChannelChatCommand(channelID, command, int64Arg, int16Arg, stringArg1, stringArg2)

    def _processChatError(self, action, channelId, chatError, requestID=-1):
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

    def __receiveStreamedData--- This code section failed: ---

 365       0	LOAD_GLOBAL       'False'
           3	STORE_FAST        'failed'

 366       6	SETUP_EXCEPT      '43'

 367       9	LOAD_GLOBAL       'zlib'
          12	LOAD_ATTR         'decompress'
          15	LOAD_FAST         'data'
          18	CALL_FUNCTION_1   ''
          21	STORE_FAST        'data'

 368      24	LOAD_GLOBAL       'cPickle'
          27	LOAD_ATTR         'loads'
          30	LOAD_FAST         'data'
          33	CALL_FUNCTION_1   ''
          36	STORE_FAST        'chatMessages'
          39	POP_BLOCK         ''
          40	JUMP_FORWARD      '63'
        43_0	COME_FROM         '6'

 369      43	POP_TOP           ''
          44	POP_TOP           ''
          45	POP_TOP           ''

 370      46	LOAD_GLOBAL       'LOG_CURRENT_EXCEPTION'
          49	CALL_FUNCTION_0   ''
          52	POP_TOP           ''

 371      53	LOAD_GLOBAL       'True'
          56	STORE_FAST        'failed'
          59	JUMP_FORWARD      '63'
          62	END_FINALLY       ''
        63_0	COME_FROM         '40'
        63_1	COME_FROM         '62'

 372      63	LOAD_FAST         'failed'
          66	JUMP_IF_TRUE      '200'

 374      69	LOAD_GLOBAL       'sorted'
          72	LOAD_FAST         'chatMessages'
          75	LOAD_ATTR         'keys'
          78	CALL_FUNCTION_0   ''
          81	LOAD_CONST        'cmp'
          84	LOAD_LAMBDA       '<code_object <lambda>>'
          87	MAKE_FUNCTION_0   ''
          90	CALL_FUNCTION_257 ''
          93	STORE_FAST        'chIds'

 375      96	SETUP_LOOP        '200'
          99	LOAD_FAST         'chIds'
         102	GET_ITER          ''
         103	FOR_ITER          '196'
         106	STORE_FAST        'chId'

 376     109	LOAD_FAST         'chatMessages'
         112	LOAD_ATTR         'get'
         115	LOAD_FAST         'chId'
         118	LOAD_GLOBAL       'deque'
         121	CALL_FUNCTION_0   ''
         124	CALL_FUNCTION_2   ''
         127	STORE_FAST        'channelQueue'

 377     130	SETUP_LOOP        '193'
         133	LOAD_GLOBAL       'True'
         136	JUMP_IF_FALSE     '192'

 378     139	SETUP_EXCEPT      '171'

 379     142	LOAD_FAST         'channelQueue'
         145	LOAD_ATTR         'popleft'
         148	CALL_FUNCTION_0   ''
         151	STORE_FAST        'actionData'

 380     154	LOAD_FAST         'self'
         157	LOAD_ATTR         'onChatAction'
         160	LOAD_FAST         'actionData'
         163	CALL_FUNCTION_1   ''
         166	POP_TOP           ''
         167	POP_BLOCK         ''
         168	JUMP_BACK         '133'
       171_0	COME_FROM         '139'

 381     171	DUP_TOP           ''
         172	LOAD_GLOBAL       'IndexError'
         175	COMPARE_OP        'exception match'
         178	JUMP_IF_FALSE     '188'
         181	POP_TOP           ''
         182	POP_TOP           ''
         183	POP_TOP           ''

 382     184	BREAK_LOOP        ''
         185	JUMP_BACK         '133'
         188	END_FINALLY       ''
       189_0	COME_FROM         '188'
         189	JUMP_BACK         '133'
         192	POP_BLOCK         ''
       193_0	COME_FROM         '130'
         193	JUMP_BACK         '103'
         196	POP_BLOCK         ''
       197_0	COME_FROM         '96'
         197	JUMP_FORWARD      '200'
       200_0	COME_FROM         '197'

 384     200	LOAD_FAST         'self'
         203	LOAD_ATTR         '__baseChatCommand'
         206	LOAD_GLOBAL       'CHAT_COMMANDS'
         209	LOAD_ATTR         'initAck'
         212	LOAD_CONST        'int64Arg'
         215	LOAD_FAST         'streamID'
         218	LOAD_CONST        'int16Arg'
         221	LOAD_FAST         'failed'
         224	CALL_FUNCTION_513 ''
         227	POP_TOP           ''

Syntax error at or near 'POP_BLOCK' token at offset 192

    def __baseChannelChatCommand(self, channelID, command, int64Arg=0, int16Arg=0, stringArg1='', stringArg2='', ignoreCooldown=True):
        if 0 == channelID:
            LOG_ERROR('Can`t execute chat channel command for channelId: %s' % (channelID,))
        else:
            if chat_shared.isOperationInCooldown(chat_shared.g_chatCooldownData, command):
                if ignoreCooldown:
                    return
                raise ChatCommandInCooldown(command)
            self.__baseChatCommand(command, channelID, int64Arg, int16Arg, stringArg1, stringArg2)

    def __baseChatCommand(self, command, channelID=0, int64Arg=0, int16Arg=0, stringArg1='', stringArg2='', ignoreCooldown=True, requestID=None):
        if requestID is None:
            requestID = self.acquireRequestID()
        if chat_shared.isOperationInCooldown(chat_shared.g_chatCooldownData, command):
            if not ignoreCooldown:
                raise ChatCommandInCooldown(command)
        self.base.chatCommand(None, requestID, command.index(), channelID, int64Arg, int16Arg, stringArg1, stringArg2)
        return

    def __baseInviteCommand(self, command, inviteType=None, receiverName='', int64Arg=0, int16Arg=0, stringArg1='', stringArg2='', requestID=None):
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