# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/components/browser_view_page.py
import logging
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.BrowserViewStackExPaddingMeta import BrowserViewStackExPaddingMeta
from helpers import dependency
from skeletons.gui.game_control import IBrowserController
_logger = logging.getLogger(__name__)

class BrowserPageComponent(BrowserViewStackExPaddingMeta):
    browserCtrl = dependency.descriptor(IBrowserController)

    def __init__(self):
        super(BrowserPageComponent, self).__init__()
        self._wasError = False
        self.__browserId = None
        self.__url = None
        self.__size = None
        self.__browserViewCreated = False
        return

    def setViewSize(self, width, height):
        previousSize = self.__size
        self.__size = (width, height)
        if previousSize is None and self.__size:
            self.__initializeBrowser()
        return

    def invalidateUrl(self):
        self._wasError = False
        self.__url = self._getUrl()
        if self.__url is not None:
            browser = self.browserCtrl.getBrowser(self.__browserId)
            if browser is not None:
                browser.navigate(self.__url)
            else:
                _logger.error('Failed to invalidate browser url!')
        return

    def refreshUrl(self):
        self._wasError = False
        browser = self.browserCtrl.getBrowser(self.__browserId)
        if browser is not None:
            browser.refresh()
        else:
            _logger.error('Failed to refresh browser!')
        return

    def _populate(self):
        super(BrowserPageComponent, self)._populate()
        self.as_setWaitingMessageS(backport.text(R.strings.waiting.browser.init()))
        self.as_setAllowWaitingS(True, True)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BrowserPageComponent, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError += self._onError
            viewPy.init(self.__browserId, self._getWebHandlers())

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == VIEW_ALIAS.BROWSER:
            viewPy.onError -= self._onError
        super(BrowserPageComponent, self)._onUnregisterFlashComponent(viewPy, alias)

    def _onError(self):
        self._wasError = True

    @classmethod
    def _isRightClickAllowed(cls):
        return False

    def _getWebHandlers(self):
        return None

    def _getUrl(self):
        return None

    def __initializeBrowser(self):
        self.__url = self._getUrl()
        if self.__url is not None:
            self.__createBrowser()
        return

    @process
    def __createBrowser(self):
        width, height = self.__size
        self.__browserId = yield self.browserCtrl.load(url=self.__url, useBrowserWindow=False, showBrowserCallback=self.__showBrowser, browserSize=(width, height))
        browser = self.browserCtrl.getBrowser(self.__browserId)
        if browser:
            browser.useSpecialKeys = False
            browser.allowRightClick = self._isRightClickAllowed()
        else:
            _logger.error('Failed to create browser!')

    def __showBrowser(self):
        if not self.__browserViewCreated:
            BigWorld.callback(0.01, self.as_createBrowserViewS)
            self.__browserViewCreated = True
