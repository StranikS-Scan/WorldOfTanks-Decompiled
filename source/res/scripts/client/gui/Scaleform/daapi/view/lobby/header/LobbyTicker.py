# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyTicker.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.common.BaseTicker import BaseTicker
from gui import GUI_SETTINGS, game_control

class LobbyTicker(BaseTicker):

    def __init__(self):
        super(LobbyTicker, self).__init__()

    def _handleBrowserLink(self, link):
        openBrowser = BigWorld.wg_openWebBrowser
        if GUI_SETTINGS.movingText.internalBrowser:
            browser = game_control.g_instance.browser
            if browser is not None:
                openBrowser = browser.load
            else:
                LOG_ERROR('Attempting to open internal browser with page: `%s`,but browser is not exist. External browser will be opened.' % str(link))
        openBrowser(link)
        return
