# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/LobbyTicker.py
from adisp import process
from debug_utils import LOG_ERROR
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.common.BaseTicker import BaseTicker
from helpers import dependency
from skeletons.gui.game_control import IBrowserController, IExternalLinksController

class LobbyTicker(BaseTicker):
    """
    This class maintains RSS header in Lobby.
    For internal browser - cache last browserID to show news in the same browser window.
    """
    externalBrowser = dependency.descriptor(IExternalLinksController)
    internalBrowser = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(LobbyTicker, self).__init__()
        self.__browserID = None
        return

    def _dispose(self):
        self.__browserID = None
        super(LobbyTicker, self)._dispose()
        return

    def _handleBrowserLink(self, link):
        if GUI_SETTINGS.movingText.internalBrowser:
            if self.internalBrowser is not None:
                self.__showInternalBrowser(link)
            else:
                LOG_ERROR('Attempting to open internal browser with page: {},but browser is not exist. External browser will be opened.'.format(str(link)))
                self.__showExternalBrowser(link)
        else:
            self.__showExternalBrowser(link)
        return

    @process
    def __showInternalBrowser(self, link):
        """
        Open (if not already opened) internal browser.
        Also cache a browserID to open the clicked link in the same browser window.
        :param link: URL link to open
        """
        self.__browserID = yield self.internalBrowser.load(url=link, browserID=self.__browserID)

    def __showExternalBrowser(self, link):
        """
        Open the provided URL in an external browser
        :param link: URL link to open
        """
        if self.externalBrowser is not None:
            self.externalBrowser.open(link)
        else:
            LOG_ERROR('Can not open an External Browser. The instance does not exist.')
        return
