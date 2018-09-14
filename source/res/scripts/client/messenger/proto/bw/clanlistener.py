# Embedded file name: scripts/client/messenger/proto/bw/ClanListener.py
import BigWorld
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR
from messenger.ext.player_helpers import getPlayerDatabaseID
from messenger.m_constants import USER_TAG
from messenger.proto.bw.find_criteria import BWClanChannelFindCriteria
from messenger.proto.entities import CurrentUserEntity, SharedUserEntity
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

class _INIT_STEPS(object):
    CLAN_INFO_RECEIVED = 1
    MEMBERS_LIST_RECEIVED = 2
    LIST_INITED = CLAN_INFO_RECEIVED | MEMBERS_LIST_RECEIVED


class ClanListener(object):

    def __init__(self):
        super(ClanListener, self).__init__()
        self.__initSteps = 0
        self.__clanChannel = None
        self.__channelCriteria = BWClanChannelFindCriteria()
        return

    @storage_getter('users')
    def usersStorage(self):
        return None

    @storage_getter('playerCtx')
    def playerCtx(self):
        return None

    def start(self):
        self.__findClanChannel()
        cEvents = g_messengerEvents.channels
        cEvents.onChannelInited += self.__ce_onChannelInited
        cEvents.onChannelDestroyed += self.__ce_onChannelDestroyed
        g_playerEvents.onClanMembersListChanged += self.__pe_onClanMembersListChanged
        self.playerCtx.onClanInfoChanged += self.__pc_onClanInfoChanged

    def stop(self):
        cEvents = g_messengerEvents.channels
        cEvents.onChannelInited -= self.__ce_onChannelInited
        cEvents.onChannelDestroyed -= self.__ce_onChannelDestroyed
        self.__clearClanChannel()
        g_playerEvents.onClanMembersListChanged -= self.__pe_onClanMembersListChanged
        self.playerCtx.onClanInfoChanged -= self.__pc_onClanInfoChanged

    def __findClanChannel(self):
        channel = storage_getter('channels')().getChannelByCriteria(self.__channelCriteria)
        if channel is not None:
            self.__initClanChannel(channel)
        return

    def __initClanChannel(self, channel):
        if self.__clanChannel is not None:
            LOG_ERROR('Clan channel is defined', self.__clanChannel, channel)
            return
        else:
            self.__clanChannel = channel
            self.__clanChannel.onMembersListChanged += self.__ce_onMembersListChanged
            self.__refreshClanMembers()
            return

    def __clearClanChannel(self):
        if self.__clanChannel is not None:
            self.__clanChannel.onMembersListChanged -= self.__ce_onMembersListChanged
            self.__clanChannel = None
            for user in self.usersStorage.getClanMembersIterator():
                user.update(isOnline=False)

            g_messengerEvents.users.onClanMembersListChanged()
        return

    def __refreshClanMembers(self):
        getter = self.__clanChannel.getMember
        events = g_messengerEvents.users
        changed = False
        for user in self.usersStorage.getClanMembersIterator():
            dbID = user.getID()
            isOnline = user.isOnline()
            member = getter(dbID)
            if member is not None:
                if not isOnline:
                    user.update(isOnline=True)
                    events.onUserStatusUpdated(user)
                    changed = True
            elif isOnline:
                user.update(isOnline=False)
                events.onUserStatusUpdated(user)
                changed = True

        if changed:
            events.onClanMembersListChanged()
        return

    def __pe_onClanMembersListChanged(self):
        clanMembers = getattr(BigWorld.player(), 'clanMembers', {})
        LOG_DEBUG('setClanMembersList', clanMembers)
        if not self.__initSteps & _INIT_STEPS.MEMBERS_LIST_RECEIVED:
            self.__initSteps |= _INIT_STEPS.MEMBERS_LIST_RECEIVED
        clanAbbrev = self.playerCtx.getClanAbbrev()
        members = []
        if self.__clanChannel is not None:
            getter = self.__clanChannel.getMember
        else:
            getter = lambda dbID: None
        playerID = getPlayerDatabaseID()
        for dbID, (name, roleFlags) in clanMembers.iteritems():
            isOnline = False if getter(dbID) is None else True
            if playerID == dbID:
                user = CurrentUserEntity(dbID, name=name, clanAbbrev=clanAbbrev, clanRole=roleFlags)
            else:
                user = SharedUserEntity(dbID, name=name, clanAbbrev=clanAbbrev, clanRole=roleFlags, isOnline=isOnline, tags={USER_TAG.CLAN_MEMBER})
            members.append(user)

        self.usersStorage._setClanMembersList(members)
        if self.__initSteps & _INIT_STEPS.LIST_INITED != 0:
            g_messengerEvents.users.onClanMembersListChanged()
        return

    def __pc_onClanInfoChanged(self):
        clanInfo = self.playerCtx.clanInfo
        hasClanInfo = clanInfo is not None and len(clanInfo) > 0
        if not self.__initSteps & _INIT_STEPS.CLAN_INFO_RECEIVED and hasClanInfo:
            self.__initSteps |= _INIT_STEPS.CLAN_INFO_RECEIVED
        user = self.usersStorage.getUser(getPlayerDatabaseID())
        if user:
            user.update(clanRole=self.playerCtx.getClanRole())
        clanAbbrev = self.playerCtx.getClanAbbrev()
        for user in self.usersStorage.getClanMembersIterator():
            user.update(clanAbbrev=clanAbbrev)

        if self.__initSteps & _INIT_STEPS.LIST_INITED != 0:
            g_messengerEvents.users.onClanMembersListChanged()
        return

    def __ce_onChannelInited(self, channel):
        if self.__channelCriteria.filter(channel):
            self.__initClanChannel(channel)

    def __ce_onChannelDestroyed(self, channel):
        if self.__channelCriteria.filter(channel):
            self.__clearClanChannel()

    def __ce_onMembersListChanged(self):
        self.__refreshClanMembers()
