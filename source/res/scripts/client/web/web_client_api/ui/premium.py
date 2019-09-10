# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/premium.py
from web.web_client_api import w2c, W2CSchema
from gui.shared import event_dispatcher as shared_events

class PremiumWindowWebApiMixin(object):

    @w2c(W2CSchema, 'premium')
    def openPremiumWindow(self, cmd):
        shared_events.showPremiumWindow()


class PremiumViewsWebApiMixin(object):

    @w2c(W2CSchema, 'premium_dashboard')
    def openPremiumDashboardWindow(self, cmd):
        shared_events.showDashboardView()

    @w2c(W2CSchema, 'maps_blacklist')
    def openMapsBlacklistView(self, cmd):
        shared_events.showMapsBlacklistView()
