# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/web_handlers.py
from gui.shared.ClanCache import g_clanCache
from gui.shared.event_dispatcher import showClanProfileWindow, showClanInvitesWindow, showClanSearchWindow
from messenger.m_constants import USER_TAG
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from web_client_api import WebCommandException
from web_client_api.commands import instantiateObject
from web_client_api.commands.window_navigator import OpenClanCardCommand

class ONLINE_STATUS(object):
    OFFLINE = 0
    ONLINE = 1
    BUSY = 2


def handleClanManagementCommand(command, ctx):
    """
    Executes clan management actions
    """
    if command.action in CLAN_MANAGEMENT_ACTIONS:

        def onCallback(data):
            data['action'] = command.action
            callback = ctx.get('callback')
            if callable(callback):
                callback(data)

        subCommand, handler = CLAN_MANAGEMENT_ACTIONS[command.action]
        if subCommand:
            subCommandInstance = instantiateObject(subCommand, command.custom_parameters)
            handler(subCommandInstance, onCallback)
        else:
            handler(onCallback)
    else:
        raise WebCommandException('Unknown clan management action: %s!' % command.action)


def _getMembersOnline(callback):
    members = g_clanCache.clanMembers
    onlineCount = 0
    for member in members:
        if member.isOnline():
            onlineCount += 1

    callback({'all_members': len(members),
     'online_members': onlineCount})


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


def _getMembersStatus(callback):
    members = g_clanCache.clanMembers
    callback({'members_status': _getStatuses(members)})


def _getFriendsStatus(callback):
    storage = g_clanCache.usersStorage
    friends = storage.getList(MutualFriendsFindCriteria(), iterator=storage.getClanMembersIterator(False))
    callback({'friends_status': _getStatuses(friends)})


CLAN_MANAGEMENT_ACTIONS = {'members_online': (None, _getMembersOnline),
 'members_status': (None, _getMembersStatus),
 'friends_status': (None, _getFriendsStatus)}

def _openClanCard(command):
    """
    Opens clan card window
    """
    showClanProfileWindow(command.clan_dbid, command.clan_abbrev)


def _openClanInvites():
    """
    Opens clan invites window
    """
    showClanInvitesWindow()


def _openClanSearch():
    """
    Opens clan search window
    """
    showClanSearchWindow()


OPEN_WINDOW_CLAN_SUB_COMMANDS = {'clan_card_window': (OpenClanCardCommand, _openClanCard),
 'clan_invites_window': (None, _openClanInvites),
 'clan_search_window': (None, _openClanSearch)}
