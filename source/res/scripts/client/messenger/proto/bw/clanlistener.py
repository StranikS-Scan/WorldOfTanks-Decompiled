# Embedded file name: scripts/client/messenger/proto/bw/ClanListener.py
import BigWorld
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.shared.utils import getPlayerDatabaseID
from messenger.m_constants import USER_TAG, GAME_ONLINE_STATUS
from messenger.proto.bw.find_criteria import BWClanChannelFindCriteria
from messenger.proto.entities import CurrentUserEntity, SharedUserEntity, ClanInfo
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
                user.update(gosBit=-GAME_ONLINE_STATUS.IN_CLAN_CHAT)

            g_messengerEvents.users.onClanMembersListChanged()
        return

    def __refreshClanMembers(self):
        getter = self.__clanChannel.getMember
        events = g_messengerEvents.users
        changed = False
        for user in self.usersStorage.getClanMembersIterator():
            dbID = user.getID()
            isOnline = user.getGOS() & GAME_ONLINE_STATUS.IN_CLAN_CHAT > 0
            member = getter(dbID)
            if member is not None:
                if not isOnline:
                    user.update(gosBit=GAME_ONLINE_STATUS.IN_CLAN_CHAT)
                    events.onUserStatusUpdated(user)
                    changed = True
            elif isOnline:
                user.update(gosBit=-GAME_ONLINE_STATUS.IN_CLAN_CHAT)
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
            if getter(dbID) is None:
                gos = GAME_ONLINE_STATUS.UNDEFINED
            else:
                gos = GAME_ONLINE_STATUS.ONLINE
            if playerID == dbID:
                user = CurrentUserEntity(dbID, name=name, clanInfo=ClanInfo(0L, clanAbbrev, roleFlags))
            else:
                user = SharedUserEntity(dbID, name=name, clanInfo=ClanInfo(0L, clanAbbrev, roleFlags), gos=gos, tags={USER_TAG.CLAN_MEMBER})
            members.append(user)

        self.usersStorage._setClanMembersList(members)
        if self.__initSteps & _INIT_STEPS.LIST_INITED != 0:
            g_messengerEvents.users.onClanMembersListChanged()
        return

    def __pc_onClanInfoChanged(self):
        clanInfo = self.playerCtx.getClanInfo()
        if clanInfo:
            isInClan = clanInfo.isInClan()
            clanAbbrev = clanInfo.abbrev
        else:
            isInClan = False
            clanAbbrev = ''
        if not self.__initSteps & _INIT_STEPS.CLAN_INFO_RECEIVED and isInClan:
            self.__initSteps |= _INIT_STEPS.CLAN_INFO_RECEIVED
        for user in self.usersStorage.getClanMembersIterator():
            user.update(clanInfo=ClanInfo(abbrev=clanAbbrev))

        if self.__initSteps & _INIT_STEPS.LIST_INITED != 0:
            g_messengerEvents.users.onClanMembersListChanged()

    def __ce_onChannelInited(self, channel):
        if self.__channelCriteria.filter(channel):
            self.__initClanChannel(channel)

    def __ce_onChannelDestroyed(self, channel):
        if self.__channelCriteria.filter(channel):
            self.__clearClanChannel()

    def __ce_onMembersListChanged(self):
        self.__refreshClanMembers()
