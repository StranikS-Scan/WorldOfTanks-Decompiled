# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/cosmic.py
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from web.web_client_api import W2CSchema, w2c

class CosmicEventLobbyWebApiMixin(object):

    @w2c(W2CSchema, 'cosmic_lobby')
    def openCosmicLobbyView(self, _):
        g_eventBus.handleEvent(events.CosmicEvent(events.CosmicEvent.OPEN_COSMIC), scope=EVENT_BUS_SCOPE.LOBBY)
