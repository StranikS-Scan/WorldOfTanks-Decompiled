# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/low_tier_rewards.py
from gui.shared.event_dispatcher import showLowTierRewardsOverlay
from web.web_client_api import W2CSchema, w2c

class LowTierRewardsApiMixin(object):

    @w2c(W2CSchema, name='open_low_tier_rewards')
    def openBrowser(self, cmd):
        showLowTierRewardsOverlay()
        return {'action': 'open_browser'}
