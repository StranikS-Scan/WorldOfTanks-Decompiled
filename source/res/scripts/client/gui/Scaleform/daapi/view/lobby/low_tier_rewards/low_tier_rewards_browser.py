# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/low_tier_rewards/low_tier_rewards_browser.py
import BigWorld
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.lobby.low_tier_rewards.web_handlers import createLowTierRewardsWebHandlers
from gui.Scaleform.daapi.view.lobby.shared.web_view import WebView

class LowTierRewardsHubPageOverlay(WebView):

    def __init__(self, ctx=None):
        super(LowTierRewardsHubPageOverlay, self).__init__(ctx)
        self.isLogOff = False

    def webHandlers(self):
        return createLowTierRewardsWebHandlers()

    def _populate(self):
        super(LowTierRewardsHubPageOverlay, self)._populate()
        BigWorld.worldDrawEnabled(False)
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _dispose(self):
        BigWorld.worldDrawEnabled(True)
        if not self.isLogOff:
            BigWorld.worldDrawEnabled(True)
        super(LowTierRewardsHubPageOverlay, self)._dispose()

    def __onDisconnected(self):
        self.isLogOff = True
