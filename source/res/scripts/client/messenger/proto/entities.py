# Embedded file name: scripts/client/messenger/proto/entities.py
from collections import deque
from ids_generators import SequenceIDGenerator
from gui.LobbyContext import g_lobbyContext
from gui.shared.utils.decorators import ReprInjector
from messenger.m_constants import USER_GUI_TYPE, MESSAGES_HISTORY_MAX_LEN, MESSENGER_COMMAND_TYPE, USER_TAG, USER_DEFAULT_NAME_PREFIX, GAME_ONLINE_STATUS, PRIMARY_CHANNEL_ORDER
from messenger.proto.events import ChannelEvents, MemberEvents
from messenger.storage import storage_getter
_g_namesGenerator = None

def _generateUserName():
    global _g_namesGenerator
    if _g_namesGenerator is None:
        _g_namesGenerator = SequenceIDGenerator()
    return '%s %d' % (USER_DEFAULT_NAME_PREFIX, _g_namesGenerator.next())


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
            mode = 'SPG' if vehicle.vehicleType.classTag == 'SPG' else ''
        if mode:
            result = '{0:>s}{1:>s}'.format(result, mode)
        return result

    def getVehMarkers(self, vehicle = None):
        mode = ''
        if vehicle:
            mode = 'SPG' if vehicle.vehicleType.classTag == 'SPG' else ''
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


@ReprInjector.simple('dbID', 'abbrev', 'role')

class ClanInfo(object):
    __slots__ = ('dbID', 'abbrev', 'role')

    def __init__(self, dbID = 0L, abbrev = '', role = 0):
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
        return self.abbrev and len(self.abbrev) > 0


class UserEntity(ChatEntity):
    __slots__ = ('_databaseID', '_name', '_note', '_tags', '_clanInfo', '_globalRating')

    def __init__(self, databaseID, name = None, tags = None, clanInfo = None, globalRating = -1, note = ''):
        super(UserEntity, self).__init__()
        self._databaseID = databaseID
        self._note = note
        self._tags = tags or set()
        self._clanInfo = clanInfo or ClanInfo()
        self._globalRating = globalRating
        if globalRating == -1:
            self._globalRating = 0
            self._tags.add(USER_TAG.INVALID_RATING)
        else:
            self._globalRating = globalRating
        if name is None:
            self._name = _generateUserName()
            self._tags.add(USER_TAG.INVALID_NAME)
        else:
            self._name = name
        return

    def __repr__(self):
        return 'UserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, clanInfo={3!r:s}, rating={4:n})'.format(self._databaseID, self.getFullName(), self.getTags(), self._clanInfo, self._globalRating)

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
            clanAbbrev = self.getClanAbbrev()
        else:
            clanAbbrev = None
        if isRegion:
            pDBID = self._databaseID
        else:
            pDBID = None
        return g_lobbyContext.getPlayerFullName(self.getName(), clanAbbrev=clanAbbrev, pDBID=pDBID)

    def getGlobalRating(self):
        return self._globalRating

    def getGroups(self):
        return set()

    def getTags(self):
        return self._tags.copy()

    def getResourceID(self):
        return None

    def getClientInfo(self):
        return None

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

    def isCurrentPlayer(self):
        return False

    def isFriend(self):
        return USER_TAG.FRIEND in self.getTags()

    def isIgnored(self):
        return USER_TAG.IGNORED in self.getTags()

    def isMuted(self):
        return USER_TAG.MUTED in self.getTags()

    def hasValidName(self):
        return USER_TAG.INVALID_NAME not in self._tags

    def hasValidRating(self):
        return USER_TAG.INVALID_RATING not in self._tags

    def setSharedProps(self, other):
        self.update(clanInfo=other.getClanInfo(), globalRating=other.getGlobalRating(), note=other.getNote())
        tags = USER_TAG.filterSharedTags(other.getTags())
        if tags:
            self.addTags(tags)
        return True

    def update(self, **kwargs):
        if 'name' in kwargs:
            if kwargs['name']:
                self._tags.discard(USER_TAG.INVALID_NAME)
            self._name = kwargs['name']
        if 'note' in kwargs:
            self._note = kwargs['note']
        if 'tags' in kwargs:
            self._tags = kwargs['tags']
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
        self._databaseID = 0
        self._name = None
        self._tags = set()
        self._clanInfo.clear()
        self._globalRating = -1
        return


class SharedUserEntity(UserEntity):
    __slots__ = ('_gos',)

    def __init__(self, databaseID, name = None, tags = None, gos = GAME_ONLINE_STATUS.UNDEFINED, clanInfo = None, globalRating = -1, note = ''):
        super(SharedUserEntity, self).__init__(databaseID, name, tags, clanInfo, globalRating, note)
        self._gos = gos

    def __repr__(self):
        return 'SharedUserEntity(dbID={0!r:s}, fullName={1:>s}, tags={2!r:s}, gos={3!r:s}, clanInfo={4!r:s} rating={5:n})'.format(self._databaseID, self.getFullName(), self.getTags(), self._gos, self._clanInfo, self._globalRating)

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


class CurrentUserEntity(UserEntity):

    def __init__(self, databaseID, name = None, clanInfo = None):
        super(CurrentUserEntity, self).__init__(databaseID, name=name, clanInfo=clanInfo, tags={USER_TAG.CURRENT})

    def __repr__(self):
        return 'CurrentUserEntity(dbID={0!r:s}, fullName={1:>s}, clanInfo={2!r:s})'.format(self._databaseID, self.getFullName(), self._clanInfo)

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
