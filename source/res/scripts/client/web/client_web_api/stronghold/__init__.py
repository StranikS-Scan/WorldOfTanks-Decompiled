# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/stronghold/__init__.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.stronghold.stronghold_helpers import getClanSeasonProgressLevel, CLAN_SEASON_PROGRESS_PREFIX
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from web.client_web_api.api import C2WHandler, c2w

class StrongholdEventHandler(C2WHandler):

    def init(self):
        super(StrongholdEventHandler, self).init()
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        g_eventBus.addListener(events.StrongholdEvent.STRONGHOLD_REWARD_SELECTED, self.__sendRewardSelected, EVENT_BUS_SCOPE.STRONGHOLD)

    def fini(self):
        g_eventBus.removeListener(events.StrongholdEvent.STRONGHOLD_REWARD_SELECTED, self.__sendRewardSelected, EVENT_BUS_SCOPE.STRONGHOLD)
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        super(StrongholdEventHandler, self).fini()

    def __onTokensUpdate(self, diff):
        if CLAN_SEASON_PROGRESS_PREFIX in diff:
            self.__sendToken({CLAN_SEASON_PROGRESS_PREFIX: getClanSeasonProgressLevel()})

    @c2w(name='stronghold_token_update')
    def __sendToken(self, tokenInfo):
        return tokenInfo

    @c2w(name='stronghold_reward_selected')
    def __sendRewardSelected(self, *args, **kwargs):
        pass
