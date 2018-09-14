# Embedded file name: scripts/client/messenger/proto/entities.py
from collections import deque
from gui.LobbyContext import g_lobbyContext
from messenger.m_constants import USER_GUI_TYPE, MESSAGES_HISTORY_MAX_LEN, MESSENGER_COMMAND_TYPE, USER_TAG
from messenger.proto.events import ChannelEvents, MemberEvents
from messenger.storage import storage_getter

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
        return 0

    def getPersistentState(self):
        return None

    def setPersistentState(self, state):
        return False


class _ChatCommand(ChatEntity):
    __slots__ = ('_clientID', '_protoData')

    def __init__(self, protoData, clientID = 0):
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
        return ''


class OutChatCommand(_ChatCommand):
    pass


class ReceivedBattleChatCommand(_ChatCommand):

    def getCommandType(self):
        return MESSENGER_COMMAND_TYPE.BATTLE

    def getSenderID(self):
        return 0L

    def getFirstTargetID(self):
        return 0

    def getSecondTargetID(self):
        return 0

    def getCellIndex(self):
        return 0

    def getCommandText(self):
        return ''

    def getVehMarker(self, mode = None, vehicle = None):
        result = self._getCommandVehMarker()
        if vehicle:
            mode = 'SPG' if 'SPG' in vehicle.vehicleType.tags else ''
        if mode:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def getVehMarkers(self, vehicle = None):
        mode = ''
        if vehicle:
            mode = 'SPG' if 'SPG' in vehicle.vehicleType.tags else ''
        return (self.getVehMarker(mode=mode), 'attackSender{0:>s}'.format(mode))

    def getSoundEventName(self):
        return 'chat_shortcut_common_fx'

    def isIgnored(self):
        user = storage_getter('users')().getUser(self.getSenderID())
        if user:
            return user.isIgnored()
        return False

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
        user = storage_getter('users')().getUser(self.getSenderID())
        if user:
            return user.isCurrentPlayer()
        return False

    def showMarkerForReceiver(self):
        return False

    def _getCommandVehMarker(self):
        return ''


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
        return ''

    def getFullName(self):
        return ''

    def isSystem(self):
        return False

    def isPrivate(self):
        return False

    def isBattle(self):
        return False

    def isPrebattle(self):
        return False

    def getPrebattleType(self):
        return 0

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
        while len(self._members):
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
                self._members[memberID].update(status=member.getStatus())
            else:
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

    def clear(self):
        super(MemberEntity, self).clear()

    def getFullName(self, isClan = True, isRegion = True):
        if isRegion:
            pDBID = self._memberID
        else:
            pDBID = None
        return g_lobbyContext.getPlayerFullName(self._nickName, pDBID=pDBID, regionCode=g_lobbyContext.getRegionCode(pDBID))


class UserEntity(ChatEntity):
    __slots__ = ('_databaseID', '_name', '_note', '_tags', '_clanAbbrev', '_clanRole')

    def __init__(self, databaseID, name = 'Unknown', tags = None, clanAbbrev = None, clanRole = 0):
        super(UserEntity, self).__init__()
        self._databaseID = databaseID
        self._name = name
        self._note = ''
        self._tags = tags or set()
        self._clanAbbrev = clanAbbrev
        self._clanRole = clanRole

    def __repr__(self):
        return 'UserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, clanRole={3:n})'.format(self._databaseID, self.getFullName(), self._tags, self._clanRole)

    def __eq__(self, other):
        return self.getID() == other.getID()

    def __hash__(self):
        return self.getID()

    def getID(self):
        return self._databaseID

    def getName(self):
        return self._name

    def getFullName(self, isClan = True, isRegion = True):
        if isClan:
            clanAbbrev = self._clanAbbrev
        else:
            clanAbbrev = None
        if isRegion:
            pDBID = self._databaseID
        else:
            pDBID = None
        return g_lobbyContext.getPlayerFullName(self.getName(), clanAbbrev=clanAbbrev, pDBID=pDBID)

    def getGroups(self):
        return set()

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
            else:
                return USER_GUI_TYPE.OTHER
        elif self.isIgnored():
            return USER_GUI_TYPE.IGNORED
        return USER_GUI_TYPE.OTHER

    def isOnline(self):
        return False

    def getClanAbbrev(self):
        return self._clanAbbrev

    def getClanRole(self):
        return self._clanRole

    def getNote(self):
        return self._note

    def isCurrentPlayer(self):
        return False

    def isFriend(self):
        return USER_TAG.FRIEND in self.getTags()

    def isIgnored(self):
        return USER_TAG.IGNORED in self.getTags()

    def isMuted(self):
        return USER_TAG.MUTED in self.getTags()

    def setSharedProps(self, other):
        self._clanAbbrev = other.getClanAbbrev()
        self._clanRole = other.getClanRole()
        tags = USER_TAG.filterSharedTags(other.getTags())
        if tags:
            self.addTags(tags)
        return True

    def update(self, **kwargs):
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'note' in kwargs:
            self._note = kwargs['note']
        if 'tags' in kwargs:
            self._tags = kwargs['tags']
        if 'clanAbbrev' in kwargs:
            self._clanAbbrev = kwargs['clanAbbrev']
        if 'clanRole' in kwargs:
            self._clanRole = kwargs['clanRole']
        if 'clanMember' in kwargs:
            member = kwargs['clanMember']
            self._name = member.getName()
            self._clanAbbrev = member.getClanAbbrev()
            self._clanRole = member.getClanRole()
            self._tags.add(USER_TAG.CLAN_MEMBER)
        if 'noClan' in kwargs and kwargs['noClan']:
            self._clanAbbrev = None
            self._clanRole = 0
            self._tags.discard(USER_TAG.CLAN_MEMBER)
        return

    def clear(self):
        self._databaseID = 0
        self._name = 'Unknown'
        self._tags = set()
        self._clanAbbrev = None
        self._clanRole = 0
        return


class SharedUserEntity(UserEntity):
    __slots__ = ('_isOnline',)

    def __init__(self, databaseID, name = 'Unknown', tags = None, isOnline = False, clanAbbrev = None, clanRole = 0):
        super(SharedUserEntity, self).__init__(databaseID, name, tags, clanAbbrev, clanRole)
        self._tags = tags or set()
        self._isOnline = isOnline

    def __repr__(self):
        return 'SharedUserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, isOnline={3!r:s}, clanRole={4:n})'.format(self._databaseID, self.getFullName(), self._tags, self._isOnline, self._clanRole)

    def isOnline(self):
        return self._isOnline

    def update(self, **kwargs):
        if 'isOnline' in kwargs:
            self._isOnline = kwargs['isOnline']
        super(SharedUserEntity, self).update(**kwargs)

    def clear(self):
        super(SharedUserEntity, self).clear()
        self._isOnline = False


class CurrentUserEntity(UserEntity):

    def __init__(self, databaseID, name = 'Unknown', clanAbbrev = None, clanRole = 0):
        super(CurrentUserEntity, self).__init__(databaseID, name=name, clanAbbrev=clanAbbrev, clanRole=clanRole, tags={USER_TAG.CURRENT})

    def __repr__(self):
        return 'CurrentUserEntity(dbID={0!r:s}, fullName={1:>s}, clanRole={2:n})'.format(self._databaseID, self.getFullName(), self._clanRole)

    def getTags(self):
        tags = super(CurrentUserEntity, self).getTags()
        tags.add(USER_TAG.CURRENT)
        return tags

    def isOnline(self):
        return True

    def getGuiType(self):
        return USER_GUI_TYPE.CURRENT_PLAYER

    def isCurrentPlayer(self):
        return True
