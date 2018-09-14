# Embedded file name: scripts/client/messenger/proto/bw_chat2/ClubListener.py
from debug_utils import LOG_ERROR
from gui.clubs.club_helpers import MyClubListener
from gui.clubs.settings import CLIENT_CLUB_STATE
from messenger.m_constants import USER_TAG, PROTO_TYPE, GAME_ONLINE_STATUS
from messenger.proto.bw_chat2.find_criteria import BWChatTypeFindCriteria
from messenger.proto.bw_chat2.wrappers import CHAT_TYPE
from messenger.proto.entities import SharedUserEntity
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import UserTagsFindCriteria
from messenger.storage import storage_getter
_TAGS = {USER_TAG.CLUB_MEMBER}

class ClubListener(MyClubListener):

    def __init__(self):
        super(ClubListener, self).__init__()
        self.__clubChannel = None
        self.__channelCriteria = None
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def start(self):
        self.startMyClubListening()
        events = g_messengerEvents.channels
        events.onChannelInited += self.__ce_onChannelInited
        events.onChannelDestroyed += self.__ce_onChannelDestroyed

    def stop(self):
        self.stopMyClubListening()
        self.__clearClubChannel()
        events = g_messengerEvents.channels
        events.onChannelInited -= self.__ce_onChannelInited
        events.onChannelDestroyed -= self.__ce_onChannelDestroyed

    def onAccountClubStateChanged(self, state):
        self.__updateClubData()

    def onClubUpdated(self, club):
        self.__updateClubData()

    def onClubNameChanged(self, name):
        self.playerCtx.setMyClubName(name)
        g_messengerEvents.users.onUsersListReceived(_TAGS)

    def onClubMembersChanged(self, members):
        self.__setClubMembersList(members)

    def __updateClubData(self):
        club = self.getClub()
        if self.clubsState.getStateID() != CLIENT_CLUB_STATE.HAS_CLUB or not club:
            self.usersStorage.removeTags(_TAGS)
            self.playerCtx.setMyClubName('')
            g_messengerEvents.users.onUsersListReceived(_TAGS)
            return
        self.playerCtx.setMyClubName(club.getUserName())
        self.__setClubMembersList(club.getMembers())
        self.__channelCriteria = BWChatTypeFindCriteria(CHAT_TYPE.CLUB)
        self.__findClubChannel()

    def __findClubChannel(self):
        channel = storage_getter('channels')().getChannelByCriteria(self.__channelCriteria)
        if channel is not None:
            self.__initClubChannel(channel)
        return

    def __initClubChannel(self, channel):
        if self.__clubChannel is None:
            self.__clubChannel = channel
            self.__clubChannel.onMembersListChanged += self.__ce_onMembersListChanged
            self.__setClubMembersStatues()
        return

    def __clearClubChannel(self):
        if not self.__clubChannel:
            return
        else:
            self.__clubChannel.onMembersListChanged -= self.__ce_onMembersListChanged
            self.__clubChannel = None
            bit = GAME_ONLINE_STATUS.IN_CLUB_CHAT
            for user in self.usersStorage.getList(UserTagsFindCriteria(_TAGS)):
                user.update(gosBit=-bit)

            g_messengerEvents.users.onUsersListReceived(_TAGS)
            return

    def __setClubMembersList(self, members):
        self.usersStorage.removeTags(_TAGS)
        getter = self.usersStorage.getUser
        setter = self.usersStorage.setUser
        unresolved = set()
        for dbID in members.iterkeys():
            contact = getter(dbID)
            if contact:
                contact.addTags(_TAGS)
            else:
                unresolved.add(dbID)
                setter(SharedUserEntity(dbID, tags={USER_TAG.CLUB_MEMBER}))

        if unresolved:
            from messenger.proto import proto_getter
            xmpp = proto_getter(PROTO_TYPE.XMPP).get()
            xmpp.nicknames.resolve(unresolved, self.__onClubMembersReceived)
        else:
            self.__onClubMembersReceived()

    def __setClubMembersStatues(self):
        getter = self.__clubChannel.getMember
        events = g_messengerEvents.users
        bit = GAME_ONLINE_STATUS.IN_CLUB_CHAT
        for user in self.usersStorage.getList(UserTagsFindCriteria(_TAGS)):
            dbID = user.getID()
            isOnline = user.getGOS() & bit > 0
            member = getter(dbID)
            if member is not None:
                if not isOnline:
                    user.update(name=member.getName(), gosBit=bit)
                    events.onUserStatusUpdated(user)
            elif isOnline:
                user.update(gosBit=-bit)
                events.onUserStatusUpdated(user)

        return

    def __onClubMembersReceived(self, result = None, error = None):
        g_messengerEvents.users.onUsersListReceived(_TAGS)

    def __ce_onChannelInited(self, channel):
        if self.__channelCriteria and self.__channelCriteria.filter(channel):
            self.__initClubChannel(channel)

    def __ce_onChannelDestroyed(self, channel):
        if self.__channelCriteria and self.__channelCriteria.filter(channel):
            self.__clearClubChannel()

    def __ce_onMembersListChanged(self):
        self.__setClubMembersStatues()
