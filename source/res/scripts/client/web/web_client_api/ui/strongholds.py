# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/strongholds.py
from gui.clans.clan_helpers import getStrongholdUrl
from web.web_client_api import w2c, W2CSchema
from gui.shared import event_dispatcher as shared_events

class StrongholdsWebApiMixin(object):

    @w2c(W2CSchema, 'strongholds')
    def openStrongholds(self, cmd):
        url = getStrongholdUrl() + cmd.custom_parameters.get('url', '')
        shared_events.showStrongholds(url)
