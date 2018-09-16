# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/web_handlers.py
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_dispatcher import showClanProfileWindow, showClanInvitesWindow, showClanSearchWindow
from messenger.m_constants import USER_TAG
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria

class ONLINE_STATUS(object):
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2


def handleGetMembersOnline(command, ctx):
    members = g_clanCache.clanMembers
    onlineCount = 0
    for member in members:
        if member.isOnline():
            onlineCount += 1

    ctx['callback']({'all_members': len(members),
     'online_members': onlineCount,
     'action': 'members_online'})


def _getStatuses(users):
    statuses = {}
    for user in users:
        if user.isOnline():
            if USER_TAG.PRESENCE_DND in user.getTags():
                status = ONLINE_STATUS.BUSY
            else:
                status = ONLINE_STATUS.ONLINE
        else:
            status = ONLINE_STATUS.OFFLINE
        statuses[user.getID()] = status

    return statuses


def handleGetMembersStatus(command, ctx):
    members = g_clanCache.clanMembers
    ctx['callback']({'members_status': _getStatuses(members),
     'action': 'members_status'})


def handleGetFriendsStatus(command, ctx):
    storage = g_clanCache.usersStorage
    friends = storage.getList(MutualFriendsFindCriteria(), iterator=storage.getClanMembersIterator(False))
    ctx['callback']({'friends_status': _getStatuses(friends),
     'action': 'friends_status'})


def handleOpenClanCard(command, ctx):
    showClanProfileWindow(command.clan_dbid, command.clan_abbrev)


def handleOpenClanInvites(command, ctx):
    showClanInvitesWindow()


def handleOpenClanSearch(command, ctx):
    showClanSearchWindow()
