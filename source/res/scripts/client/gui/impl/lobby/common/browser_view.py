# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/browser_view.py
import typing
from frameworks.wulf import ViewFlags
from gui.impl import backport
from gui.impl.common.browser import Browser, BrowserSettings
from gui.impl.gen.view_models.views.browser_view_model import BrowserViewModel
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from sound_gui_manager import CommonSoundSpaceSettings
from web.web_client_api import webApiCollection
BrowserViewSettings = typing.NamedTuple('BrowserViewSettings', (('url', str),
 ('webHandlers', typing.Optional[webApiCollection]),
 ('isClosable', bool),
 ('useSpecialKeys', bool),
 ('allowRightClick', bool),
 ('waitingMessageID', int),
 ('disabledKeys', typing.Iterable[typing.Tuple[str, bool, bool, bool, bool]]),
 ('soundSpaceSettings', typing.Optional[CommonSoundSpaceSettings]),
 ('returnClb', typing.Optional[typing.Callable])))

def makeSettings(url, webHandlers=None, isClosable=False, useSpecialKeys=False, allowRightClick=False, waitingMessageID=R.invalid(), disabledKeys=(), soundSpaceSettings=None, returnClb=None):
    return BrowserViewSettings(url, webHandlers, isClosable, useSpecialKeys, allowRightClick, waitingMessageID, disabledKeys, soundSpaceSettings, returnClb)


class BrowserView(Browser[BrowserViewModel]):
    __slots__ = ('__settings', '__closedByUser', '__forceClosed')
    __background_alpha__ = 1.0
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, settings):
        self._COMMON_SOUND_SPACE = settings.soundSpaceSettings
        super(BrowserView, self).__init__(url=settings.url, settings=BrowserSettings(layoutID=layoutID, flags=ViewFlags.LOBBY_SUB_VIEW, model=BrowserViewModel()), webHandlersMap=settings.webHandlers, preload=True)
        self.__settings = settings
        self.__closedByUser = False
        self.__forceClosed = False
        if self.browser is not None:
            self.__setupBrowser()
        else:
            self.onBrowserObtained += self.__onBrowserObtained
        return

    def onCloseView(self):
        self.__forceClosed = True
        self.destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(BrowserView, self)._onLoading(*args, **kwargs)
        self.getViewModel().onClose += self.__onClose
        with self.getViewModel().transaction() as model:
            model.setIsClosable(self.__settings.isClosable)
            if self.__settings.waitingMessageID != R.invalid():
                self.setWaitingMessage(backport.msgid(self.__settings.waitingMessageID))

    def _initialize(self, *args, **kwargs):
        super(BrowserView, self)._initialize(*args, **kwargs)
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(self.__background_alpha__)

    def _finalize(self):
        self.getViewModel().onClose -= self.__onClose
        self.onBrowserObtained -= self.__onBrowserObtained
        returnCallback = self.__settings.returnClb
        if returnCallback is not None:
            returnCallback(byUser=self.__closedByUser, url=self.browser.url if self.browser else '', forceClosed=self.__forceClosed)
        super(BrowserView, self)._finalize()
        return

    def __onClose(self):
        self.__closedByUser = True
        self.onCloseView()

    def __setupBrowser(self):
        self.browser.useSpecialKeys = self.__settings.useSpecialKeys
        self.browser.allowRightClick = self.__settings.allowRightClick
        self.browser.setDisabledKeys(self.__settings.disabledKeys)

    def __onBrowserObtained(self, _):
        self.__setupBrowser()
