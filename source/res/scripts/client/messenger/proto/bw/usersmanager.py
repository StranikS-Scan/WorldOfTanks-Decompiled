# Embedded file name: scripts/client/messenger/proto/bw/UsersManager.py
import BigWorld
import Event
import chat_shared
from debug_utils import LOG_DEBUG
from messenger.ext.player_helpers import getPlayerDatabaseID
from messenger.m_constants import USER_ROSTER_ACTION, MESSENGER_SCOPE, PROTO_TYPE
from messenger.proto.bw import entities
from messenger.proto.bw.ChatActionsListener import ChatActionsListener
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class UsersManager(ChatActionsListener):

    def __init__(self):
        CHAT_RESPONSES = chat_shared.CHAT_RESPONSES
        ChatActionsListener.__init__(self, {CHAT_RESPONSES.commandInCooldown: '_UsersManager__onCommandInCooldown',
         CHAT_RESPONSES.incorrectCharacter: '_UsersManager__onIncorrectCharacter'})
        self.__eventManager = Event.EventManager()
        self.onFindUsersComplete = Event.Event(self.__eventManager)
        self.onFindUsersFailed = Event.Event(self.__eventManager)
        self.__replayCtrl = None
        self.__isPrivateOpen = False
        self.__isRosterReceivedOnce = False
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    def addListeners(self):
        CHAT_ACTIONS = chat_shared.CHAT_ACTIONS
        self.addListener(self.__onFindUsers, CHAT_ACTIONS.findUsers)
        self.addListener(self.__onAddFriend, CHAT_ACTIONS.addFriend)
        self.addListener(self.__onRemoveFriend, CHAT_ACTIONS.removeFriend)
        self.addListener(self.__onAddIgnored, CHAT_ACTIONS.addIgnored)
        self.addListener(self.__onRemoveIgnored, CHAT_ACTIONS.removeIgnored)
        self.addListener(self.__onSetMuted, CHAT_ACTIONS.setMuted)
        self.addListener(self.__onUnsetMuted, CHAT_ACTIONS.unsetMuted)
        self.addListener(self.__onFriendStatusUpdate, CHAT_ACTIONS.friendStatusUpdate)
        self.addListener(self.__onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        g_messengerEvents.channels.onConnectStateChanged += self.__ce_onConnectStateChanged

    def removeAllListeners(self):
        super(UsersManager, self).removeAllListeners()
        g_messengerEvents.channels.onConnectStateChanged -= self.__ce_onConnectStateChanged

    def switch(self, scope):
        self.__isPrivateOpen = False
        if scope is MESSENGER_SCOPE.LOBBY:
            self.requestFriendStatus()
            self.requestUsersRoster()

    def view(self, scope):
        if scope is MESSENGER_SCOPE.BATTLE and not self.__isRosterReceivedOnce:
            self.requestUsersRoster()

    def clear(self):
        self.__eventManager.clear()

    def findUsers(self, token, onlineMode = None, requestID = None):
        BigWorld.player().findUsers(token, onlineMode=onlineMode, requestID=requestID)

    def addFriend(self, friendID, friendName):
        BigWorld.player().addFriend(friendID, friendName)

    def setMuted(self, dbID, userName):
        BigWorld.player().setMuted(dbID, userName)

    def addIgnored(self, dbID, ignoredName):
        BigWorld.player().addIgnored(dbID, ignoredName)

    def removeFriend(self, dbID):
        BigWorld.player().removeFriend(dbID)

    def unsetMuted(self, dbID):
        BigWorld.player().unsetMuted(dbID)

    def removeIgnored(self, dbID):
        BigWorld.player().removeIgnored(dbID)

    def requestUsersRoster(self):
        BigWorld.player().requestUsersRoster()

    def requestFriendStatus(self, dbID = -1):
        BigWorld.player().requestFriendStatus(dbID)

    def createPrivateChannel(self, friendID, friendName):
        self.__isPrivateOpen = True
        BigWorld.player().createPrivate(friendID, friendName)

    def __onFindUsers(self, chatAction):
        chatActionDict = dict(chatAction)
        result = chatActionDict.get('data', [])
        requestID = chatActionDict.get('requestID', [])
        users = []
        for userData in result:
            name, dbID, isOnline, clanAbbrev = userData[:4]
            dbID = long(dbID)
            if not len(name):
                continue
            received = entities.BWUserEntity(dbID, name=name, isOnline=isOnline, clanAbbrev=clanAbbrev)
            user = self.usersStorage.getUser(dbID)
            if user:
                if user.isCurrentPlayer():
                    received = user
                else:
                    received.update(roster=user.getRoster())
            users.append(received)

        self.onFindUsersComplete(requestID, users)

    def __onUserRosterChange(self, chatAction, actionIdx, include, exclude = None):
        userData = [-1, 'Unknown', 0]
        if chatAction.has_key('data'):
            userData = list(chatAction['data'])
        dbID, name = userData[:2]
        roster = include
        user = self.usersStorage.getUser(dbID)
        if user is not None:
            roster = user.getRoster()
            if roster & include is 0:
                roster |= include
            if exclude and roster & exclude is not 0:
                roster ^= exclude
            user.update(roster=roster)
        else:
            user = entities.BWUserEntity(dbID, name=name, roster=roster)
            self.usersStorage.addUser(user)
        g_messengerEvents.users.onUserRosterChanged(actionIdx, user)
        return

    def __onUserRosterRemoved(self, chatAction, actionIdx, exclude):
        userData = chatAction['data'] if chatAction.has_key('data') else -1
        dbID = long(userData)
        user = self.usersStorage.getUser(dbID)
        if user and user.getRoster() & exclude is not 0:
            user.update(roster=user.getRoster() ^ exclude)
            g_messengerEvents.users.onUserRosterChanged(actionIdx, user)

    def __onAddFriend(self, chatAction):
        self.__onUserRosterChange(chatAction, USER_ROSTER_ACTION.AddToFriend, chat_shared.USERS_ROSTER_FRIEND, exclude=chat_shared.USERS_ROSTER_IGNORED)

    def __onRemoveFriend(self, chatAction):
        self.__onUserRosterRemoved(chatAction, USER_ROSTER_ACTION.RemoveFromFriend, chat_shared.USERS_ROSTER_FRIEND)

    def __onAddIgnored(self, chatAction):
        self.__onUserRosterChange(chatAction, USER_ROSTER_ACTION.AddToIgnored, chat_shared.USERS_ROSTER_IGNORED, exclude=chat_shared.USERS_ROSTER_FRIEND)

    def __onRemoveIgnored(self, chatAction):
        self.__onUserRosterRemoved(chatAction, USER_ROSTER_ACTION.RemoveFromIgnored, chat_shared.USERS_ROSTER_IGNORED)

    def __onSetMuted(self, chatAction):
        self.__onUserRosterChange(chatAction, USER_ROSTER_ACTION.SetMuted, chat_shared.USERS_ROSTER_VOICE_MUTED)

    def __onUnsetMuted(self, chatAction):
        self.__onUserRosterRemoved(chatAction, USER_ROSTER_ACTION.UnsetMuted, chat_shared.USERS_ROSTER_VOICE_MUTED)

    def __onFriendStatusUpdate(self, chatAction):
        userData = chatAction['data'] if chatAction.has_key('data') else [-1, False]
        dbID, isOnline = userData.iteritems().next()
        user = self.usersStorage.getUser(dbID)
        if user is not None:
            prevOnline = user.isOnline()
            user.update(isOnline=isOnline)
            if prevOnline is not user.isOnline():
                LOG_DEBUG("Player's status has been changed by BW", user)
                g_messengerEvents.users.onUserRosterStatusUpdated(user)
        return

    def __onRequestUsersRoster(self, chatAction):
        self.__isRosterReceivedOnce = True
        if self.__replayCtrl is None:
            import BattleReplay
            self.__replayCtrl = BattleReplay.g_replayCtrl
        if self.__replayCtrl.isRecording:
            self.__replayCtrl.cancelSaveCurrMessage()
        data = dict(chatAction)
        result = data.get('data', [])
        flags = data.get('flags', 0)
        if not flags:
            self.usersStorage._clearRosters()
        for userData in result:
            dbID, name, roster = userData[:3]
            user = self.usersStorage.getUser(dbID)
            if user:
                user.update(name=name, roster=roster)
            else:
                self.usersStorage.addUser(entities.BWUserEntity(dbID, name=name, roster=roster))

        g_messengerEvents.users.onUsersRosterReceived()
        return

    def __onCommandInCooldown(self, actionResponse, chatAction):
        data = chatAction.get('data', {'command': None,
         'cooldownPeriod': -1})
        result = False
        if data['command'] == 'findUser':
            result = True
            self.onFindUsersFailed(chatAction.get('requestID', -1L), actionResponse, data)
        return result

    def __onIncorrectCharacter(self, actionResponse, chatAction):
        action = chatAction.get('action')
        result = False
        if action == chat_shared.CHAT_ACTIONS.findUsers.index():
            result = True
            self.onFindUsersFailed(chatAction.get('requestID', -1L), actionResponse, None)
        return result

    def __ce_onConnectStateChanged(self, channel):
        if self.__isPrivateOpen and channel.isJoined() and channel.isPrivate() and channel.getProtoType() == PROTO_TYPE.BW and channel.getProtoData().owner == getPlayerDatabaseID():
            g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
