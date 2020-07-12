# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/entities.py
from collections import deque
from helpers import dependency, i18n
from ids_generators import SequenceIDGenerator
from gui.shared.utils.decorators import ReprInjector
from messenger.m_constants import USER_GUI_TYPE, MESSAGES_HISTORY_MAX_LEN, MESSENGER_COMMAND_TYPE, USER_TAG, USER_DEFAULT_NAME_PREFIX, GAME_ONLINE_STATUS, PRIMARY_CHANNEL_ORDER, UserEntityScope
from messenger.proto.events import ChannelEvents, MemberEvents
from messenger.storage import storage_getter
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.battle_session import IBattleSessionProvider
_g_namesGenerator = None

def _generateUserName():
    global _g_namesGenerator
    if _g_namesGenerator is None:
        _g_namesGenerator = SequenceIDGenerator()
    return '%s %d' % (i18n.makeString(USER_DEFAULT_NAME_PREFIX), _g_namesGenerator.next())


class ChatEntity(object):
    __slots__ = ()

    def __eq__(self, other):
        try:
            return other.getProtoType() is self.getProtoType() and self.getID() == other.getID()
        except AttributeError:
            return False

    def getID(self):
        return None

    def getProtoType(self):
        pass

    def getPersistentState(self):
        return None

    def setPersistentState(self, state):
        return False


class _ChatCommand(ChatEntity):
    __slots__ = ('_clientID', '_protoData')

    def __init__(self, protoData, clientID=0):
        super(_ChatCommand, self).__init__()
        self._protoData = protoData
        self._clientID = clientID

    def getClientID(self):
        return self._clientID

    def setClientID(self, clientID):
        self._clientID = clientID

    def getProtoData(self):
        return self._protoData

    def getCommandType(self):
        return MESSENGER_COMMAND_TYPE.UNDEFINED

    def getCommandText(self):
        pass


class OutChatCommand(_ChatCommand):
    pass


class ReceivedUnitChatCommand(_ChatCommand):
    pass


class ReceivedBattleChatCommand(_ChatCommand):

    def getCommandType(self):
        return MESSENGER_COMMAND_TYPE.BATTLE

    def getSenderID(self):
        pass

    def getPosition3D(self):
        return None

    def getFirstTargetID(self):
        pass

    def getSecondTargetID(self):
        pass

    def getCellIndex(self):
        pass

    def getCommandText(self):
        pass

    def getVehMarker(self, mode=None):
        result = self._getCommandVehMarker()
        if mode and result:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def getSenderVehMarker(self, mode=None):
        result = self._getCommandSenderVehMarker()
        if mode and result:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def getVehMarkers(self):
        mode = ''
        return (self.getVehMarker(mode=mode), self.getSenderVehMarker(mode=mode))

    def getSoundEventName(self, useSoundNotification):
        if useSoundNotification is True:
            result = self._getSoundNotification()
            if result is not None:
                return result
        return 'chat_shortcut_common_fx'

    def isIgnored(self):
        user = storage_getter('users')().getUser(self.getSenderID(), scope=UserEntityScope.BATTLE)
        return user.isIgnored() if user else False

    def isOnMinimap(self):
        return False

    def hasTarget(self):
        return False

    def isPrivate(self):
        return False

    def isPublic(self):
        return True

    def isReceiver(self):
        return False

    def isSender(self):
        user = storage_getter('users')().getUser(self.getSenderID(), scope=UserEntityScope.BATTLE)
        return user.isCurrentPlayer() if user else False

    def showMarkerForReceiver(self):
        return False

    def isMsgOnMarker(self):
        return False

    def messageOnMarker(self):
        pass

    def _getCommandVehMarker(self):
        pass

    def _getCommandSenderVehMarker(self):
        pass

    def _getSoundNotification(self):
        pass


class ChannelEntity(ChatEntity, ChannelEvents):
    __slots__ = ('_data', '_history', '_members', '_isJoined', '_clientID')

    def __init__(self, data):
        super(ChannelEntity, self).__init__()
        self._data = data
        self._history = deque([], MESSAGES_HISTORY_MAX_LEN)
        self._members = {}
        self._isJoined = False
        self._clientID = 0

    def __repr__(self):
        return 'ChannelEntity(type={0:n}, isJoined={1!r:s}, data={2!r:s})'.format(self.getProtoType(), self._isJoined, self._data)

    def getClientID(self):
        return self._clientID

    def setClientID(self, clientID):
        self._clientID = clientID

    def getProtoData(self):
        return self._data

    def getName(self):
        pass

    def getFullName(self):
        pass

    def isSystem(self):
        return False

    def isPrivate(self):
        return False

    def isBattle(self):
        return False

    def isPrebattle(self):
        return False

    def isLazy(self):
        return False

    def getPrebattleType(self):
        pass

    def getPrimaryOrder(self):
        if self.isSystem():
            primary = PRIMARY_CHANNEL_ORDER.SYSTEM
        else:
            primary = PRIMARY_CHANNEL_ORDER.OTHER
        return primary

    def isJoined(self):
        return self._isJoined

    def setJoined(self, isJoined):
        self._isJoined = isJoined
        self.clearHistory()
        if not isJoined:
            self.clearMembers()
        self.onConnectStateChanged(self)

    def addMessage(self, message):
        self._history.append(message)

    def getHistory(self):
        return list(self._history)

    def clearHistory(self):
        self._history.clear()

    def clearMembers(self):
        while self._members:
            _, member = self._members.popitem()
            member.clear()

    def haveMembers(self):
        return True

    def getMember(self, memberID):
        member = None
        if memberID in self._members:
            member = self._members[memberID]
        return member

    def getMembers(self):
        return self._members.values()

    def hasMember(self, memberID):
        return memberID in self._members

    def addMembers(self, members):
        isChanged = False
        for member in members:
            if member is None:
                continue
            memberID = member.getID()
            if memberID in self._members:
                self._members[memberID].clear()
            isChanged = True
            self._members[member.getID()] = member
            member.onMemberStatusChanged += self._onMemberStatusChanged

        if isChanged:
            self.onMembersListChanged()
        return

    def removeMembers(self, membersIDs):
        isChanged = False
        for memberID in membersIDs:
            member = self._members.pop(memberID, None)
            if member:
                isChanged = True
                member.clear()

        if isChanged:
            self.onMembersListChanged()
        return

    def update(self, **kwargs):
        pass

    def clear(self):
        super(ChannelEntity, self).clear()
        self._isJoined = False
        self._data = None
        self._history.clear()
        self.clearMembers()
        return

    def _onMemberStatusChanged(self, member):
        self.onMemberStatusChanged(member)


class MemberEntity(ChatEntity, MemberEvents):
    __slots__ = ('_memberID', '_nickName', '_status')
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, memberID, nickName, status):
        super(MemberEntity, self).__init__()
        self._memberID = memberID
        self._nickName = nickName
        self._status = status

    def __eq__(self, other):
        return self.getID() == other.getID()

    def __hash__(self):
        return self.getID()

    def __repr__(self):
        return 'MemberEntity(id={0!r:s}, nickName={1!r:s}, status={2!r:s})'.format(self._memberID, self._nickName, self._status)

    def getID(self):
        return self._memberID

    def getDatabaseID(self):
        pass

    def getName(self):
        return self._nickName

    def getStatus(self):
        return self._status

    def setStatus(self, status):
        self._status = status
        self.onMemberStatusChanged(self)

    def isOnline(self):
        return True

    def update(self, **kwargs):
        if 'status' in kwargs:
            self.setStatus(kwargs['status'])

    def getFullName(self, isClan=True, isRegion=True):
        if isRegion:
            pDBID = self._memberID
        else:
            pDBID = None
        return self.lobbyContext.getPlayerFullName(self._nickName, pDBID=pDBID, regionCode=self.lobbyContext.getRegionCode(pDBID))


@ReprInjector.simple('dbID', 'abbrev', 'role')
class ClanInfo(object):
    __slots__ = ('dbID', 'abbrev', 'role')

    def __init__(self, dbID=0L, abbrev='', role=0):
        super(ClanInfo, self).__init__()
        self.dbID = dbID
        self.abbrev = abbrev
        self.role = role

    def clear(self):
        self.dbID = 0L
        self.abbrev = ''
        self.role = 0

    def update(self, other):
        if other.dbID:
            self.dbID = other.dbID
        if other.abbrev:
            self.abbrev = other.abbrev
        if other.role:
            self.role = other.role

    def isInClan(self):
        return bool(self.abbrev)


class UserEntity(ChatEntity):
    __slots__ = ('_userID', '_name', '_tags', '_scope')

    def __init__(self, userID, name=None, tags=None, scope=None):
        super(UserEntity, self).__init__()
        self._userID = userID
        self._tags = tags or set()
        if scope is None:
            self._scope = self._getScope()
        else:
            self._scope = scope
        if name is None:
            self._name = _generateUserName()
            self._tags.add(USER_TAG.INVALID_NAME)
        else:
            self._name = name
        return

    def __eq__(self, other):
        return self.getStorageKey() == other.getStorageKey()

    def getID(self):
        return self._userID

    def getScope(self):
        return self._scope

    def getStorageKey(self):
        return (self.getID(), self.getScope())

    def getName(self):
        return self._name

    def getFullName(self):
        raise NotImplementedError

    def getTags(self):
        return self._tags.copy()

    def addTags(self, tags):
        self._tags = self._tags.union(tags)

    def removeTags(self, tags):
        self._tags = self._tags.difference(tags)

    def getGuiType(self):
        if self.isFriend():
            if USER_TAG.SUB_TO in self.getTags():
                return USER_GUI_TYPE.FRIEND
            return USER_GUI_TYPE.OTHER
        return USER_GUI_TYPE.IGNORED if self.isIgnored() else USER_GUI_TYPE.OTHER

    def isFriend(self):
        return USER_TAG.FRIEND in self.getTags()

    def isIgnored(self):
        return USER_TAG.IGNORED in self.getTags() or self.isTemporaryIgnored()

    def isTemporaryIgnored(self):
        return USER_TAG.IGNORED_TMP in self.getTags()

    def isMuted(self):
        return USER_TAG.MUTED in self.getTags()

    def isCurrentPlayer(self):
        return False

    def hasValidName(self):
        return USER_TAG.INVALID_NAME not in self._tags

    def setSharedProps(self, other):
        raise NotImplementedError

    def update(self, **kwargs):
        if 'name' in kwargs:
            if kwargs['name']:
                self._tags.discard(USER_TAG.INVALID_NAME)
            self._name = kwargs['name']
        if 'tags' in kwargs:
            self._tags = kwargs['tags']

    def clear(self):
        self._userID = None
        self._name = None
        self._tags = set()
        self._scope = None
        return

    @staticmethod
    def _getScope():
        raise NotImplementedError


@ReprInjector.simple(('getID', 'dbID'), ('getFullName', 'fullName'), ('getTags', 'tags'), ('getClanInfo', 'clanInfo'), ('getGlobalRating', 'rating'), ('getScope', 'scope'))
class LobbyUserEntity(UserEntity):
    __slots__ = ('_note', '_clanInfo', '_globalRating')
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, userID, name=None, tags=None, clanInfo=None, globalRating=-1, note='', scope=None):
        super(LobbyUserEntity, self).__init__(userID, name, tags, scope)
        self._note = note
        self._clanInfo = clanInfo or ClanInfo()
        if globalRating == -1:
            self._globalRating = 0
            self._tags.add(USER_TAG.INVALID_RATING)
        else:
            self._globalRating = globalRating

    def __hash__(self):
        return self.getID() ^ self.getScope()

    def getFullName(self):
        return self._lobbyContext.getPlayerFullName(self.getName(), clanAbbrev=self.getClanAbbrev())

    def getGlobalRating(self):
        return self._globalRating

    def getGroups(self):
        return set()

    def getResourceID(self):
        return None

    def getClientInfo(self):
        return None

    def isOnline(self):
        return False

    def getGOS(self):
        return GAME_ONLINE_STATUS.UNDEFINED

    def getClanInfo(self):
        return self._clanInfo

    def getClanAbbrev(self):
        return self._clanInfo.abbrev

    def getClanRole(self):
        return self._clanInfo.role

    def getNote(self):
        return self._note

    def hasValidRating(self):
        return USER_TAG.INVALID_RATING not in self._tags

    def setSharedProps(self, other):
        self.update(clanInfo=other.getClanInfo(), globalRating=other.getGlobalRating(), note=other.getNote())
        tags = USER_TAG.filterSharedTags(other.getTags())
        if tags:
            self.addTags(tags)
        return True

    def update(self, **kwargs):
        super(LobbyUserEntity, self).update(**kwargs)
        if 'note' in kwargs:
            self._note = kwargs['note']
        if 'globalRating' in kwargs:
            if kwargs['globalRating'] >= 0:
                self._tags.discard(USER_TAG.INVALID_RATING)
            self._globalRating = kwargs['globalRating']
        if 'clanInfo' in kwargs:
            clanInfo = kwargs['clanInfo']
            if clanInfo:
                self._clanInfo.update(clanInfo)
            elif USER_TAG.CLAN_MEMBER not in self._tags:
                self._clanInfo = ClanInfo()

    def clear(self):
        self._clanInfo.clear()
        self._globalRating = -1
        self._note = ''
        super(LobbyUserEntity, self).clear()

    @staticmethod
    def _getScope():
        return UserEntityScope.LOBBY


@ReprInjector.simple(('getID', 'avatarSessionID'), ('getName', 'name'), ('getTags', 'tags'), ('getScope', 'scope'))
class BattleUserEntity(UserEntity):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __hash__(self):
        return hash(self.getID()) ^ self.getScope()

    def getFullName(self):
        return self._sessionProvider.getCtx().getPlayerFullName(avatarSessionID=self.getID(), showVehShortName=False)

    def setSharedProps(self, other):
        pass

    @staticmethod
    def _getScope():
        return UserEntityScope.BATTLE


@ReprInjector.withParent(('getGOS', 'gos'))
class SharedUserEntity(LobbyUserEntity):
    __slots__ = ('_gos',)

    def __init__(self, userID, name=None, tags=None, gos=GAME_ONLINE_STATUS.UNDEFINED, clanInfo=None, globalRating=-1, note='', scope=None):
        super(SharedUserEntity, self).__init__(userID, name, tags, clanInfo, globalRating, note, scope)
        self._gos = gos

    def isOnline(self):
        return self._gos & GAME_ONLINE_STATUS.ONLINE > 0

    def getGOS(self):
        return self._gos

    def update(self, **kwargs):
        if 'gosBit' in kwargs:
            self._gos = GAME_ONLINE_STATUS.update(self._gos, kwargs['gosBit'])
        super(SharedUserEntity, self).update(**kwargs)

    def clear(self):
        super(SharedUserEntity, self).clear()
        self._gos = GAME_ONLINE_STATUS.UNDEFINED


@ReprInjector.simple(('getID', 'dbID'), ('getFullName', 'fullName'), ('getClanInfo', 'clanInfo'), ('getScope', 'scope'))
class CurrentLobbyUserEntity(LobbyUserEntity):

    def __init__(self, userID, name=None, clanInfo=None, scope=None):
        super(CurrentLobbyUserEntity, self).__init__(userID, name=name, clanInfo=clanInfo, tags={USER_TAG.CURRENT}, scope=scope)

    def getTags(self):
        tags = super(CurrentLobbyUserEntity, self).getTags()
        tags.add(USER_TAG.CURRENT)
        return tags

    def isOnline(self):
        return True

    def getGuiType(self):
        return USER_GUI_TYPE.CURRENT_PLAYER

    def isCurrentPlayer(self):
        return True


@ReprInjector.simple(('getID', 'avatarSessionID'), ('getName', 'name'), ('getScope', 'scope'))
class CurrentBattleUserEntity(BattleUserEntity):

    def getTags(self):
        tags = super(CurrentBattleUserEntity, self).getTags()
        tags.add(USER_TAG.CURRENT)
        return tags

    def getGuiType(self):
        return USER_GUI_TYPE.CURRENT_PLAYER

    def isCurrentPlayer(self):
        return True
