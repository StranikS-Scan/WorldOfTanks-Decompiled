# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/UsersManager.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
from chat_shared import CHAT_ACTIONS, USERS_ROSTER_FRIEND, USERS_ROSTER_IGNORED, CHAT_RESPONSES, USERS_ROSTER_VOICE_MUTED
from collections import defaultdict, deque
from messenger import BREAKERS_MAX_LENGTH
from messenger.common import MessangerSubscriber, MessengerGlobalStorage
from messenger.wrappers import UserWrapper
import Event
import constants
from adisp import async
from debug_utils import LOG_ERROR, LOG_DEBUG

def _userWrapperFactory():
    return UserWrapper()


class USERS_ROSTER_ACTIONS(object):
    AddToFriend, RemoveFromFriend, AddToIgnored, RemoveFromIgnored, SetMuted, UnsetMuted = range(6)


class CLAN_INIT_STEPS(object):
    RECEIVE_CLAN_INFO = 1
    RECEIVE_MEMBERS_LIST = 2
    RECEIVE_MEMBERS_STATUSES = 4
    INIT = RECEIVE_CLAN_INFO | RECEIVE_MEMBERS_LIST | RECEIVE_MEMBERS_STATUSES


class UsersManager(MessangerSubscriber):
    __contacts = defaultdict(_userWrapperFactory)
    __clanMembers = defaultdict(_userWrapperFactory)
    __clanInitSteps = 0
    __breakers = deque([], BREAKERS_MAX_LENGTH)
    _cp_playerDbId = MessengerGlobalStorage('_playerDbId', -1L)
    _cp_accountAttrs = MessengerGlobalStorage('_accountAttrs', -1)
    _cp_clanInfo = MessengerGlobalStorage('_clanInfo', None)

    def __init__(self):
        MessangerSubscriber.__init__(self)
        self.__eventManager = Event.EventManager()
        self.onFindUsersComplete = Event.Event(self.__eventManager)
        self.onFindUsersFailed = Event.Event(self.__eventManager)
        self.onFriendStatusUpdated = Event.Event(self.__eventManager)
        self.onUsersRosterUpdate = Event.Event(self.__eventManager)
        self.onClanMembersListRefresh = Event.Event(self.__eventManager)
        self.onClanMemberStatusesUpdated = Event.Event(self.__eventManager)
        self.onUsersRosterReceived = Event.Event()
        self.onDenunciationReceived = Event.Event()
        self.onAccountDossierRequest = Event.Event()
        self.onVehicleDossierRequest = Event.Event()
        self._responseHandlers = {CHAT_RESPONSES.commandInCooldown: '_UsersManager__onCommandInCooldown',
         CHAT_RESPONSES.incorrectCharacter: '_UsersManager__onIncorrectCharacter'}
        self.__replayCtrl = None
        return

    def subscribeToActions(self):
        """
        Subscribe to chat action.
        """
        self.subscribeAction(self.onFindUsers, CHAT_ACTIONS.findUsers)
        self.subscribeAction(self.onAddFriend, CHAT_ACTIONS.addFriend)
        self.subscribeAction(self.onAddIgnored, CHAT_ACTIONS.addIgnored)
        self.subscribeAction(self.onRemoveFriend, CHAT_ACTIONS.removeFriend)
        self.subscribeAction(self.onRemoveIgnored, CHAT_ACTIONS.removeIgnored)
        self.subscribeAction(self.onFriendStatusUpdate, CHAT_ACTIONS.friendStatusUpdate)
        self.subscribeAction(self.onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        self.subscribeAction(self.onSetMuted, CHAT_ACTIONS.setMuted)
        self.subscribeAction(self.onUnsetMuted, CHAT_ACTIONS.unsetMuted)

    def findUsers(self, token, onlineMode=None, requestID=None):
        """
        Request to server: finds users with specified criteria - token
        @param token: searches name of users
        @param onlineMode: defines search mode:
                None - search routine returns online and offline users
                True - search routine returns only online users
                False - search routine returns only offline users
        @param requestID: unique id to search request
        """
        BigWorld.player().findUsers(token, onlineMode=onlineMode, requestID=requestID)

    def addFriend(self, friendID, friendName):
        """
        Request to server: adds user to the fiends list.
        @param friendID: user database id
        @param friendName: user name
        """
        BigWorld.player().addFriend(friendID, friendName)

    def setMuted(self, userID, userName):
        """
        Request to server: set user muted
        @param userID: user database id
        @param userName: user name
        """
        BigWorld.player().setMuted(userID, userName)

    def addIgnored(self, ignoredID, ignoredName):
        """
        Request to server: adds user to the ignored list.
        @param ignoredID: user database id
        @param ignoredName: user name
        """
        BigWorld.player().addIgnored(ignoredID, ignoredName)

    def removeFriend(self, friendID):
        """
        Request to server: remove user to the fiends list.
        @param friendID: user database id
        """
        BigWorld.player().removeFriend(friendID)

    def unsetMuted(self, userID):
        """
        Request to server: unset user muted.
        @param userID: user database id
        """
        BigWorld.player().unsetMuted(userID)

    def makeDenunciation(self, userID, userName, topicID):
        BigWorld.player().makeDenunciation(userID, topicID, constants.VIOLATOR_KIND.UNKNOWN)
        self.onDenunciationReceived(userName, topicID)

    def removeIgnored(self, ignoredID):
        """
        Request to server: remove user to the ignored list.
        @param ignoredID: user database id
        """
        BigWorld.player().removeIgnored(ignoredID)

    def requestUsersRoster(self):
        """
        Request to server: get list of friends and ignored users.
        """
        BigWorld.player().requestUsersRoster()

    def requestFriendStatus(self, friendID=-1):
        """
        Request to server: get friend online status.
        @param friendID: user id
        """
        BigWorld.player().requestFriendStatus(friendID)

    def createPrivateChannel(self, friendID, friendName):
        """
        Request to server: create private channel with friend.
        @param friendID: user id
        @param friendName: user name
        """
        BigWorld.player().createPrivate(friendID, friendName)

    @async
    def requestClanInfo(self, name, callback):

        def response(resultID, clanDBID, clanInfo):
            if resultID < 0:
                LOG_ERROR('Server return error for clan info request: responseCode=%s' % resultID)
                return
            callback((clanDBID, clanInfo))

        BigWorld.player().requestPlayerClanInfo(name, response)

    @async
    def requestClanEmblem(self, clanDBID, callback):

        def response(url, file):
            callback((url, file))

        clan_emblems = BigWorld.player().serverSettings['file_server']['clan_emblems']
        BigWorld.player().customFilesCache.get(clan_emblems['url_template'] % clanDBID, clan_emblems['cache_life_time'], response)

    def requestUserInfo(self, uid, name):
        user = UserWrapper(uid, name)
        if uid in self.__contacts:
            user = self.__contacts[uid]
        self.onAccountDossierRequest(user)

    def requestVehicleStat(self, uid, name, vehicleID):
        user = UserWrapper(uid, name)
        if uid in self.__contacts:
            user = self.__contacts[uid]
        self.onVehicleDossierRequest(user, vehicleID)

    def setClanInfo(self, clanInfo):
        LOG_DEBUG('setClanInfo', clanInfo)
        if clanInfo is not None:
            hasClanInfo = len(clanInfo) > 0
            if not self.__clanInitSteps & CLAN_INIT_STEPS.RECEIVE_CLAN_INFO and hasClanInfo:
                self.__clanInitSteps |= CLAN_INIT_STEPS.RECEIVE_CLAN_INFO
            if hasClanInfo:
                for uid in self.__clanMembers.iterkeys():
                    self.__clanMembers[uid].clanName = clanInfo[1]

            self._cp_clanInfo = clanInfo
            self.__clanInitSteps & CLAN_INIT_STEPS.INIT and self.onClanMembersListRefresh()
        return

    def setClanMembersList(self, clanMembers):
        LOG_DEBUG('setClanMembersList', clanMembers)
        if not self.__clanInitSteps & CLAN_INIT_STEPS.RECEIVE_MEMBERS_LIST:
            self.__clanInitSteps |= CLAN_INIT_STEPS.RECEIVE_MEMBERS_LIST
        clanAbbrev = self._cp_clanInfo[1] if self._cp_clanInfo is not None and len(self._cp_clanInfo) > 0 else None
        for uid, name in clanMembers.iteritems():
            if self._cp_playerDbId != uid:
                self.__clanMembers[uid].uid = uid
                self.__clanMembers[uid].userName = name
                self.__clanMembers[uid].clanName = clanAbbrev

        if self.__clanInitSteps & CLAN_INIT_STEPS.INIT:
            self.onClanMembersListRefresh()
        return

    def setClanMemberStatus(self, uid, status):
        LOG_DEBUG('setClanMemberStatus', uid, status)
        if not self.__clanInitSteps & CLAN_INIT_STEPS.RECEIVE_MEMBERS_STATUSES:
            self.__clanInitSteps |= CLAN_INIT_STEPS.RECEIVE_MEMBERS_STATUSES
        if self._cp_playerDbId != uid:
            self.__clanMembers[uid].uid = uid
            self.__clanMembers[uid].online = status
            if self.__clanInitSteps & CLAN_INIT_STEPS.INIT:
                self.onClanMemberStatusesUpdated()

    def setClanMemberStatuses(self, uids, status):
        LOG_DEBUG('setClanMemberStatuses', uids, status)
        updated = False
        if not self.__clanInitSteps & CLAN_INIT_STEPS.RECEIVE_MEMBERS_STATUSES:
            self.__clanInitSteps |= CLAN_INIT_STEPS.RECEIVE_MEMBERS_STATUSES
        for uid in uids:
            if self._cp_playerDbId != uid:
                self.__clanMembers[uid].uid = uid
                self.__clanMembers[uid].online = status
                updated = True

        if self.__clanInitSteps & CLAN_INIT_STEPS.INIT and updated:
            self.onClanMemberStatusesUpdated()

    def onFindUsers(self, chatAction):
        chatActionDict = dict(chatAction)
        result = chatActionDict.get('data', [])
        requestID = chatActionDict.get('requestID', [])
        users = []
        for userData in result:
            user = UserWrapper.fromSearchAction(*userData)
            if not len(user.userName):
                continue
            user.himself = self.isCurrentPlayer(user.uid)
            if user.uid in self.__contacts:
                user.roster = self.__contacts[user.uid].roster
            users.append(user)

        self.onFindUsersComplete(requestID, users)

    def onAddFriend(self, chatAction):
        """
        Response from server to a add to friends request (@see: UsersManager.addFriend).
        @param chatAction: chat action data
        """
        userData = [-1, False]
        if chatAction.has_key('data'):
            userData = list(chatAction['data'])
        user = UserWrapper(*userData)
        if user.uid in self.__contacts:
            user.roster = self.__contacts[user.uid].roster
        user.roster |= USERS_ROSTER_FRIEND
        if bool(user.roster & USERS_ROSTER_IGNORED):
            user.roster ^= USERS_ROSTER_IGNORED
        self.__contacts[user.uid].update(user)
        if self.__clanMembers.has_key(user.uid):
            self.__clanMembers[user.uid].update(user)
        self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.AddToFriend, user)

    def onSetMuted(self, chatAction):
        """
        Response from server to set user muted (@see: UsersManager.addFriend).
        @param chatAction: chat action data
        """
        userData = [-1, False]
        if chatAction.has_key('data'):
            userData = list(chatAction['data'])
        user = UserWrapper(*userData)
        if user.uid in self.__contacts:
            user.roster = self.__contacts[user.uid].roster
        user.roster |= USERS_ROSTER_VOICE_MUTED
        self.__contacts[user.uid].update(user)
        if self.__clanMembers.has_key(user.uid):
            self.__clanMembers[user.uid].update(user)
        self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.SetMuted, user)

    def onUnsetMuted(self, chatAction):
        """
        Response from server to unset user muted (@see: UsersManager.removeFriend).
        @param chatAction: chat action data
        """
        userData = chatAction['data'] if chatAction.has_key('data') else -1
        uid = long(userData)
        if self.__contacts.has_key(uid) and bool(self.__contacts[uid].roster & USERS_ROSTER_VOICE_MUTED):
            user = self.__contacts[uid]
            user.roster ^= USERS_ROSTER_VOICE_MUTED
            self.__contacts[user.uid].update(user)
            if self.__clanMembers.has_key(user.uid):
                self.__clanMembers[user.uid].update(user)
            self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.UnsetMuted, user)

    def onAddIgnored(self, chatAction):
        """
        Response from server to a add to ignored request (@see: UsersManager.addIgnored).
        @param chatAction: chat action data
        """
        userData = [-1, False]
        if chatAction.has_key('data'):
            userData = list(chatAction['data'])
        user = UserWrapper(*userData)
        if user.uid in self.__contacts:
            user.roster = self.__contacts[user.uid].roster
        user.roster |= USERS_ROSTER_IGNORED | USERS_ROSTER_VOICE_MUTED
        if bool(user.roster & USERS_ROSTER_FRIEND):
            user.roster ^= USERS_ROSTER_FRIEND
        self.__contacts[user.uid].update(user)
        if self.__clanMembers.has_key(user.uid):
            self.__clanMembers[user.uid].update(user)
        self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.AddToIgnored, user)

    def onRemoveFriend(self, chatAction):
        """
        Response from server to a remove from friends request (@see: UsersManager.removeFriend).
        @param chatAction: chat action data
        """
        userData = chatAction['data'] if chatAction.has_key('data') else -1
        uid = long(userData)
        if self.__contacts.has_key(uid) and bool(self.__contacts[uid].roster & USERS_ROSTER_FRIEND):
            user = self.__contacts[uid]
            user.roster ^= USERS_ROSTER_FRIEND
            self.__contacts[user.uid].update(user)
            if self.__clanMembers.has_key(user.uid):
                self.__clanMembers[user.uid].update(user)
            self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.RemoveFromFriend, user)

    def onRemoveIgnored(self, chatAction):
        """
        Response from server to a remove from ignored request (@see: UsersManager.removeIgnored).
        @param chatAction: chat action data
        """
        userData = chatAction['data'] if chatAction.has_key('data') else -1
        uid = long(userData)
        if self.__contacts.has_key(uid) and bool(self.__contacts[uid].roster & USERS_ROSTER_IGNORED):
            user = self.__contacts[uid]
            user.roster ^= USERS_ROSTER_IGNORED
            self.__contacts[user.uid].update(user)
            if self.__clanMembers.has_key(user.uid):
                self.__clanMembers[user.uid].update(user)
            self.onUsersRosterUpdate(USERS_ROSTER_ACTIONS.RemoveFromIgnored, user)

    def onFriendStatusUpdate(self, chatAction):
        userData = chatAction['data'] if chatAction.has_key('data') else [-1, False]
        uid, status = userData.iteritems().next()
        if self.__contacts.has_key(uid):
            self.__contacts[uid].online = status
        self.onFriendStatusUpdated()

    def onRequestUsersRoster(self, chatAction):
        """
        Server response to a request friends and ignore list (@see: UsersManager.requestUsersRoster).
        @param chatAction: chat action data
        """
        if self.__replayCtrl is None:
            import BattleReplay
            self.__replayCtrl = BattleReplay.g_replayCtrl
        if self.__replayCtrl.isRecording:
            self.__replayCtrl.cancelSaveCurrMessage()
        data = dict(chatAction)
        result = data.get('data', [])
        flags = data.get('flags', 0)
        if not flags:
            self.__contacts.clear()
        for userData in result:
            user = UserWrapper(*userData)
            self.__contacts[user.uid].update(user)

        self.onUsersRosterReceived()
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
        if action == CHAT_ACTIONS.findUsers.index():
            result = True
            self.onFindUsersFailed(chatAction.get('requestID', -1L), actionResponse, None)
        return result

    def clear(self):
        self.__contacts = defaultdict(_userWrapperFactory)
        self.__clanMembers.clear()
        self.__clanInitSteps = 0
        self.__breakers.clear()
        self.__eventManager.clear()
        self._cp_playerDbId = -1L
        self._cp_accountAttrs = -1

    def getFriendsCount(self, isOnline=None):
        if isOnline is not None:
            filtered = filter(lambda user: user.online == isOnline and bool(user.roster & USERS_ROSTER_FRIEND), self.__contacts.values())
        else:
            filtered = filter(lambda user: bool(user.roster & USERS_ROSTER_FRIEND), self.__contacts.values())
        return len(filtered)

    def getMutedCount(self, isOnline=None):
        filtered = filter(lambda user: bool(user.roster & USERS_ROSTER_VOICE_MUTED), self.__contacts.values())
        return len(filtered)

    def getIgnoredCount(self):
        filtered = filter(lambda user: bool(user.roster & USERS_ROSTER_IGNORED), self.__contacts.values())
        return len(filtered)

    def getClanMembersCount(self, isOnline=None):
        if isOnline is not None:
            filtered = filter(lambda user: user.online == isOnline, self.__clanMembers.values())
            length = len(filtered)
        else:
            length = len(self.__clanMembers)
        return length

    def getFriendsList(self, isOnline=None):
        if isOnline is not None:
            users = filter(lambda user: user.online == isOnline and bool(user.roster & USERS_ROSTER_FRIEND), self.__contacts.values())
        else:
            users = filter(lambda user: bool(user.roster & USERS_ROSTER_FRIEND), self.__contacts.values())
        return [ user.tuple() for user in users ]

    def getMutedList(self, isOnline=None):
        users = filter(lambda user: bool(user.roster & USERS_ROSTER_VOICE_MUTED), self.__contacts.values())
        return [ user.tuple() for user in users ]

    def getIgnoredList(self):
        users = filter(lambda user: bool(user.roster & USERS_ROSTER_IGNORED), self.__contacts.values())
        return [ user.tuple() for user in users ]

    def getClanMembersList(self, isOnline=None):
        if isOnline is not None:
            users = filter(lambda user: user.online == isOnline, self.__clanMembers.values())
        else:
            users = self.__clanMembers.values()
        return [ user.tuple() for user in users ]

    def getUser(self, uid, name):
        user = UserWrapper(uid, name)
        if user.uid in self.__contacts:
            user = self.__contacts[uid]
        user.himself = self.isCurrentPlayer(user.uid)
        user.breaker = uid in self.__breakers
        return user

    def markAsBreaker(self, uid, flag):
        if flag:
            if uid not in self.__breakers:
                self.__breakers.append(uid)
        elif uid in self.__breakers:
            self.__breakers.remove(uid)

    def resetBreakers(self):
        self.__breakers.clear()

    def cp_canViewColoringBadWords(self):
        return self._cp_accountAttrs & constants.ACCOUNT_ATTR.CHAT_ADMIN != 0 or self._cp_accountAttrs & constants.ACCOUNT_ATTR.ADMIN != 0

    @classmethod
    def isCurrentPlayer(cls, playerDbId):
        return UsersManager._cp_playerDbId.value() == playerDbId
