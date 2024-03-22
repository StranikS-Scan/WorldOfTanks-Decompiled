# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/strongholds.py
from gui.clans.clan_helpers import getStrongholdUrl
from gui.impl.lobby.clan_supply.clan_supply_helpers import showClanSupplyView
from gui.shared import event_dispatcher as shared_events
from uilogging.clan_supply.constants import ClanSupplyLogKeys
from web.web_client_api import w2c, W2CSchema

class StrongholdsWebApiMixin(object):

    @w2c(W2CSchema, 'strongholds')
    def openStrongholds(self, cmd):
        url = getStrongholdUrl() + cmd.custom_parameters.get('url', '')
        shared_events.showStrongholds(url)

    @w2c(W2CSchema, 'clan_supply')
    def openClanSupply(self, cmd):
        tabID = cmd.custom_parameters.get('page')
        showClanSupplyView(tabId=tabID, parentScreenLog=ClanSupplyLogKeys.CLAN_LANDING)
