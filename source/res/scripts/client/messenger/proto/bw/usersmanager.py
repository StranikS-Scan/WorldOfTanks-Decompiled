# Embedded file name: scripts/client/messenger/proto/bw/UsersManager.py
import BigWorld
import chat_shared
from gui.shared.utils import getPlayerDatabaseID
from messenger.m_constants import USER_ACTION_ID as _ACTION_ID
from messenger.m_constants import USER_TAG as _TAG
from messenger.m_constants import MESSENGER_SCOPE, PROTO_TYPE
from messenger.proto import notations
from messenger.proto.bw import entities
from messenger.proto.bw.ChatActionsListener import ChatActionsListener
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import ProtoFindCriteria
from messenger.storage import storage_getter

def _getTagsByRoster(bwRoster):
    tags = set()
    if bwRoster & chat_shared.USERS_ROSTER_FRIEND > 0:
        tags.add(_TAG.FRIEND)
        tags.add(_TAG.SUB_TO)
    elif bwRoster & chat_shared.USERS_ROSTER_IGNORED > 0:
        tags.add(_TAG.IGNORED)
    if bwRoster & chat_shared.USERS_ROSTER_VOICE_MUTED > 0:
        tags.add(_TAG.MUTED)
    return tags


def _getRosterByTags(tags):
    bwRoster = 0
    if _TAG.FRIEND in tags:
        bwRoster |= chat_shared.USERS_ROSTER_FRIEND
    elif _TAG.IGNORED in tags:
        bwRoster |= chat_shared.USERS_ROSTER_IGNORED
    if _TAG.MUTED:
        bwRoster |= chat_shared.USERS_ROSTER_VOICE_MUTED
    return bwRoster


class UsersManager(ChatActionsListener):

    def __init__(self):
        CHAT_RESPONSES = chat_shared.CHAT_RESPONSES
        ChatActionsListener.__init__(self, {CHAT_RESPONSES.commandInCooldown: '_UsersManager__onCommandInCooldown',
         CHAT_RESPONSES.incorrectCharacter: '_UsersManager__onIncorrectCharacter'})
        self.__replayCtrl = None
        self.__isPrivateOpen = False
        self.__isRosterReceivedOnce = False
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    def addListeners(self):
        self.__addContactsListeners()
        g_messengerEvents.channels.onConnectStateChanged += self.__ce_onConnectStateChanged

    def removeAllListeners(self):
        super(UsersManager, self).removeAllListeners()
        g_messengerEvents.channels.onConnectStateChanged -= self.__ce_onConnectStateChanged

    def clear(self):
        self.__isRosterReceivedOnce = False

    def switch(self, scope):
        self.__isPrivateOpen = False
        if scope is MESSENGER_SCOPE.LOBBY:
            self.requestFriendStatus()
            self.requestUsersRoster()

    @notations.contacts(PROTO_TYPE.BW, log=False)
    def view(self, scope):
        if scope is MESSENGER_SCOPE.BATTLE and not self.__isRosterReceivedOnce:
            g_messengerEvents.users.onUsersListReceived({_TAG.FRIEND, _TAG.IGNORED, _TAG.MUTED})

    @notations.contacts(PROTO_TYPE.BW)
    def addFriend(self, friendID, friendName):
        BigWorld.player().addFriend(friendID, friendName)

    @notations.contacts(PROTO_TYPE.BW)
    def setMuted(self, dbID, userName):
        BigWorld.player().setMuted(dbID, userName)

    @notations.contacts(PROTO_TYPE.BW)
    def addIgnored(self, dbID, ignoredName):
        BigWorld.player().addIgnored(dbID, ignoredName)

    @notations.contacts(PROTO_TYPE.BW)
    def removeFriend(self, dbID):
        BigWorld.player().removeFriend(dbID)

    @notations.contacts(PROTO_TYPE.BW)
    def unsetMuted(self, dbID):
        BigWorld.player().unsetMuted(dbID)

    @notations.contacts(PROTO_TYPE.BW)
    def removeIgnored(self, dbID):
        BigWorld.player().removeIgnored(dbID)

    @notations.contacts(PROTO_TYPE.BW, log=False)
    def requestUsersRoster(self):
        BigWorld.player().requestUsersRoster()

    @notations.contacts(PROTO_TYPE.BW, log=False)
    def requestFriendStatus(self, dbID = -1):
        BigWorld.player().requestFriendStatus(dbID)

    def createPrivateChannel(self, friendID, friendName):
        self.__isPrivateOpen = True
        BigWorld.player().createPrivate(friendID, friendName)

    @notations.contacts(PROTO_TYPE.BW, log=False)
    def __addContactsListeners(self):
        _ACTIONS = chat_shared.CHAT_ACTIONS
        self.addListener(self.__onRosterReceived, _ACTIONS.requestUsersRoster)
        self.addListener(self.__onAddFriend, _ACTIONS.addFriend)
        self.addListener(self.__onRemoveFriend, _ACTIONS.removeFriend)
        self.addListener(self.__onFriendStatusUpdate, _ACTIONS.friendStatusUpdate)
        self.addListener(self.__onAddIgnored, _ACTIONS.addIgnored)
        self.addListener(self.__onRemoveIgnored, _ACTIONS.removeIgnored)
        self.addListener(self.__onSetMuted, _ACTIONS.setMuted)
        self.addListener(self.__onUnsetMuted, _ACTIONS.unsetMuted)

    def __onUserRosterChange(self, chatAction, actionID, include, exclude = None):
        userData = [-1, 'Unknown', 0]
        if chatAction.has_key('data'):
            userData = list(chatAction['data'])
        dbID, name = userData[:2]
        user = self.usersStorage.getUser(dbID, PROTO_TYPE.BW)
        if user:
            tags = user.getTags()
            tags = tags.union(include)
            if exclude:
                tags = tags.difference(exclude)
            user.update(tags=tags)
        else:
            user = entities.BWUserEntity(dbID, name=name, tags=include)
            self.usersStorage.setUser(user)
        g_messengerEvents.users.onUserActionReceived(actionID, user)

    def __onUserRosterRemoved(self, chatAction, actionID, exclude):
        userData = chatAction['data'] if chatAction.has_key('data') else -1
        dbID = long(userData)
        user = self.usersStorage.getUser(dbID, PROTO_TYPE.BW)
        if not user:
            return
        tags = user.getTags()
        if exclude & tags:
            tags = tags.difference(exclude)
            if {_TAG.CLAN_MEMBER} & tags:
                user.update(tags=tags)
            else:
                user.update(tags=tags, isOnline=False)
            g_messengerEvents.users.onUserActionReceived(actionID, user)

    def __onAddFriend(self, chatAction):
        self.__onUserRosterChange(chatAction, _ACTION_ID.FRIEND_ADDED, {_TAG.FRIEND, _TAG.SUB_TO}, exclude={_TAG.IGNORED})

    def __onRemoveFriend(self, chatAction):
        self.__onUserRosterRemoved(chatAction, _ACTION_ID.FRIEND_REMOVED, {_TAG.FRIEND, _TAG.SUB_TO})

    def __onAddIgnored(self, chatAction):
        self.__onUserRosterChange(chatAction, _ACTION_ID.IGNORED_ADDED, {_TAG.IGNORED}, exclude={_TAG.FRIEND, _TAG.SUB_TO})

    def __onRemoveIgnored(self, chatAction):
        self.__onUserRosterRemoved(chatAction, _ACTION_ID.IGNORED_REMOVED, {_TAG.IGNORED})

    def __onSetMuted(self, chatAction):
        self.__onUserRosterChange(chatAction, _ACTION_ID.MUTE_SET, {_TAG.MUTED})

    def __onUnsetMuted(self, chatAction):
        self.__onUserRosterRemoved(chatAction, _ACTION_ID.MUTE_UNSET, {_TAG.MUTED})

    def __onFriendStatusUpdate(self, chatAction):
        userData = chatAction['data'] if chatAction.has_key('data') else [-1, False]
        dbID, isOnline = userData.iteritems().next()
        user = self.usersStorage.getUser(dbID, PROTO_TYPE.BW)
        if user:
            user.update(isOnline=isOnline)
            g_messengerEvents.users.onUserStatusUpdated(user)

    def __onRosterReceived(self, chatAction):
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
            self.usersStorage.removeTags({_TAG.FRIEND, _TAG.IGNORED, _TAG.MUTED}, ProtoFindCriteria(PROTO_TYPE.BW))
        getter = self.usersStorage.getUser
        setter = self.usersStorage.setUser
        for userData in result:
            dbID, name, roster = userData[:3]
            user = getter(dbID, PROTO_TYPE.BW)
            tags = _getTagsByRoster(roster)
            if user:
                user.addTags(tags)
            else:
                setter(entities.BWUserEntity(dbID, name=name, tags=tags))

        g_messengerEvents.users.onUsersListReceived({_TAG.FRIEND, _TAG.IGNORED, _TAG.MUTED})
        return

    def __onCommandInCooldown(self, actionResponse, chatAction):
        data = chatAction.get('data', {'command': None,
         'cooldownPeriod': -1})
        result = False
        if data['command'] == 'findUser':
            result = True
            g_messengerEvents.users.onFindUsersFailed(chatAction.get('requestID', -1L), actionResponse, data)
        return result

    def __onIncorrectCharacter(self, actionResponse, chatAction):
        action = chatAction.get('action')
        result = False
        if action == chat_shared.CHAT_ACTIONS.findUsers.index():
            result = True
            g_messengerEvents.users.onFindUsersFailed(chatAction.get('requestID', -1L), actionResponse, None)
        return result

    def __ce_onConnectStateChanged(self, channel):
        if self.__isPrivateOpen and channel.isJoined() and channel.isPrivate() and channel.getProtoType() == PROTO_TYPE.BW and channel.getProtoData().owner == getPlayerDatabaseID():
            g_messengerEvents.channels.onPlayerEnterChannelByAction(channel)
