# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/clans/__init__.py
from gui.shared.ClanCache import g_clanCache
from messenger.proto.shared_find_criteria import MutualFriendsFindCriteria
from web.web_client_api import w2capi, w2c, W2CSchema
from web.web_client_api.social import getStatuses
from helpers import dependency
from skeletons.gui.game_control import IClanNotificationController
from skeletons.gui.web import IWebController

@w2capi(name='clan_management', key='action')
class ClansWebApi(object):
    __notificationCtrl = dependency.descriptor(IClanNotificationController)
    __webCtrl = dependency.descriptor(IWebController)

    @w2c(W2CSchema, name='members_online')
    def membersOnline(self, cmd):
        members = g_clanCache.clanMembers
        onlineCount = 0
        for member in members:
            if member.isOnline():
                onlineCount += 1

        return {'action': 'members_online',
         'all_members': len(members),
         'online_members': onlineCount}

    @w2c(W2CSchema, name='members_status')
    def membersStatus(self, cmd):
        members = g_clanCache.clanMembers
        return {'action': 'members_status',
         'members_status': getStatuses(members)}

    @w2c(W2CSchema, name='friends_status')
    def friendsStatus(self, cmd):
        storage = g_clanCache.usersStorage
        friends = storage.getList(MutualFriendsFindCriteria(), iterator=storage.getClanMembersIterator(False))
        return {'action': 'friends_status',
         'friends_status': getStatuses(friends)}

    @w2c(W2CSchema, name='set_news_counter')
    def setNewsCounter(self, cmd):
        alias = cmd.custom_parameters.get('alias')
        value = cmd.custom_parameters.get('count', 1)
        self.__notificationCtrl.setCounters(alias, value)
        return {'action': 'set_news_counter'}

    @w2c(W2CSchema, name='get_news_counters')
    def getNewsCounters(self, cmd):
        aliases = cmd.custom_parameters.get('aliases', [])
        return {'action': 'get_news_counters',
         'news_counts': self.__notificationCtrl.getCounters(aliases)}

    @w2c(W2CSchema, name='get_clan_info')
    def getClanInfo(self, cmd):
        return {'action': 'get_clan_info',
         'clan_info': self.__webCtrl.getClanInfo()}
