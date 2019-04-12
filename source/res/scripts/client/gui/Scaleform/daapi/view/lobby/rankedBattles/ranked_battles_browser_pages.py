# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_browser_pages.py
from gui.Scaleform.daapi.view.lobby.components.browser_view_page import BrowserPageComponent
from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import IResetablePage
from gui.ranked_battles.ranked_helpers import getRankedBattlesUrl, getRankedBattlesInfoPageUrl
from web_client_api.ranked_battles import createRankedBattlesWebHandlers

class LeaderBoardBrowserPage(BrowserPageComponent, IResetablePage):

    def reset(self):
        pass

    def _getUrl(self):
        return getRankedBattlesUrl()

    def _getWebHandlers(self):
        return createRankedBattlesWebHandlers({})


class RankedBattlesInfoPage(LeaderBoardBrowserPage):

    def _getUrl(self):
        return getRankedBattlesInfoPageUrl()
