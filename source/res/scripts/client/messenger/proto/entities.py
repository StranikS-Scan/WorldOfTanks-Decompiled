# Embedded file name: scripts/client/messenger/proto/entities.py
from collections import deque
from gui.LobbyContext import g_lobbyContext
from messenger.m_constants import USER_GUI_TYPE, MESSAGES_HISTORY_MAX_LEN, MESSENGER_COMMAND_TYPE
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
    __slots__ = ('_databaseID', '_name', '_roster', '_isOnline', '_clanAbbrev', '_clanRole', '_group', '_isInXMPP')

    def __init__(self, databaseID, name = 'Unknown', roster = 0, isOnline = False, clanAbbrev = None, clanRole = 0, isInXMPP = False, group = None):
        super(UserEntity, self).__init__()
        self._databaseID = databaseID
        self._name = name
        self._roster = roster
        self._isOnline = isOnline
        self._isInXMPP = isInXMPP
        self._clanAbbrev = clanAbbrev
        self._clanRole = clanRole
        self._group = group

    def __repr__(self):
        return 'UserEntity(dbID={0!r:s}, fullName={1:>s}, roster={2:n}, isOnline={3!r:s}/{4!r:s}, clanRole={5:n})'.format(self._databaseID, self.getFullName(), self._roster, self._isOnline, self._isInXMPP, self._clanRole)

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
        return g_lobbyContext.getPlayerFullName(self._name, clanAbbrev=clanAbbrev, pDBID=pDBID)

    def getGroup(self):
        return None

    def getRoster(self):
        return self._roster

    def getGuiType(self):
        name = USER_GUI_TYPE.OTHER
        if self.isFriend():
            return USER_GUI_TYPE.FRIEND
        if self.isIgnored():
            return USER_GUI_TYPE.IGNORED
        return name

    def isOnline(self):
        return self._isOnline or self._isInXMPP

    def getClanAbbrev(self):
        return self._clanAbbrev

    def getClanRole(self):
        return self._clanRole

    def isCurrentPlayer(self):
        return False

    def isFriend(self):
        return False

    def isIgnored(self):
        return False

    def isMuted(self):
        return False

    def update(self, **kwargs):
        if 'name' in kwargs:
            self._name = kwargs['name']
        if 'roster' in kwargs:
            self._roster = kwargs['roster']
        if 'isOnline' in kwargs:
            self._isOnline = kwargs['isOnline']
        if 'isInXMPP' in kwargs:
            self._isInXMPP = kwargs['isInXMPP']
        if 'clanAbbrev' in kwargs:
            self._clanAbbrev = kwargs['clanAbbrev']
        if 'clanRole' in kwargs:
            self._clanRole = kwargs['clanRole']
        if 'clanMember' in kwargs:
            member = kwargs['clanMember']
            self._name = member.getName()
            self._clanAbbrev = member.getClanAbbrev()
            self._clanRole = member.getClanRole()
        if 'noClan' in kwargs and kwargs['noClan']:
            self._clanAbbrev = None
            self._clanRole = 0
        return

    def clear(self):
        self._databaseID = 0
        self._name = ''
        self._roster = 0
        self._isOnline = False
        self._isInXMPP = False
        self._clanAbbrev = None
        self._clanRole = 0
        return


class CurrentUserEntity(UserEntity):

    def __init__(self, databaseID, name = 'Unknown', clanAbbrev = None, clanRole = 0):
        super(CurrentUserEntity, self).__init__(databaseID, name=name, isOnline=True, clanAbbrev=clanAbbrev, clanRole=clanRole)

    def __repr__(self):
        return 'CurrentUserEntity(dbID={0!r:s}, fullName={1:>s}, clanRole={2:n})'.format(self._databaseID, self.getFullName(), self._clanRole)

    def getGuiType(self):
        return USER_GUI_TYPE.CURRENT_PLAYER

    def isCurrentPlayer(self):
        return True
