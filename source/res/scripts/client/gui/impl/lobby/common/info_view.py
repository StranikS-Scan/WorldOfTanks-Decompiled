# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/info_view.py
import logging
import typing
from functools import partial
import wg_async
from BWUtil import AsyncReturn
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from frameworks.wulf import Window
from gui.impl.gen.view_models.views.lobby.common.info_view_model import InfoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class InfoView(ViewImpl):

    def __init__(self, settings, *args, **kwargs):
        super(InfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(InfoView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(InfoView, self)._initialize()
        self.viewModel.onClose += self.__onClose

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        super(InfoView, self)._finalize()

    def __onClose(self):
        self.destroyWindow()


class ContentData(typing.NamedTuple('_ContentData', (('clazz', typing.Type),
 ('modelClazz', typing.Type),
 ('args', typing.Tuple),
 ('kwargs', typing.Dict)))):

    def createContent(self, layoutID):
        settings = ViewSettings(layoutID=layoutID, model=self.modelClazz())
        return self.clazz(settings, *self.args, **self.kwargs)


def createContentData(clazz, modelClazz=InfoViewModel, *args, **kwargs):
    return ContentData(clazz, modelClazz, args, kwargs)


DEFAULT_CONTENT_DATA = createContentData(InfoView)

class IInfoWindowProcessor(object):

    def showAllowed(self):
        raise NotImplementedError

    def setShown(self):
        raise NotImplementedError

    def show(self, parent=None):
        raise NotImplementedError


class _InfoWindow(LobbyWindow):
    __slots__ = ('__closeCallback',)

    def __init__(self, layoutID, parent, contentData, wndFlags, callback):
        super(_InfoWindow, self).__init__(wndFlags=wndFlags, decorator=None, content=contentData.createContent(layoutID), parent=parent)
        self.__closeCallback = callback
        return

    def _initialize(self):
        super(_InfoWindow, self)._initialize()
        g_playerEvents.onDisconnected += self.__onDisconnected

    def _finalize(self):
        g_playerEvents.onDisconnected -= self.__onDisconnected
        if self.__closeCallback is not None:
            closeCallback, self.__closeCallback = self.__closeCallback, None
            closeCallback(None)
        super(_InfoWindow, self)._finalize()
        return

    def __onDisconnected(self):
        self.destroy()


class _InfoWindowProcessor(IInfoWindowProcessor):
    __slots__ = ('layoutID', 'contentData', 'uiStorageKey', 'wndFlags')
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, layoutID, contentData, uiStorageKey, wndFlags):
        self.layoutID = layoutID
        self.contentData = contentData
        self.uiStorageKey = uiStorageKey
        self.wndFlags = wndFlags

    def showAllowed(self):
        allowedByUIStorage = self.uiStorageKey is None or not self.__settingsCore.serverSettings.getUIStorage().get(self.uiStorageKey, False)
        return allowedByUIStorage

    def setShown(self):
        if self.uiStorageKey is not None:
            self.__settingsCore.serverSettings.saveInUIStorage({self.uiStorageKey: True})
        return

    @wg_async.wg_async
    def show(self, parent=None):
        if self.showAllowed():
            yield wg_async.await_callback(partial(self.__loadWindow, parent))()
        raise AsyncReturn(None)
        return

    def __loadWindow(self, parent, callback):
        window = _InfoWindow(self.layoutID, parent, self.contentData, self.wndFlags, callback)
        window.load()
        self.setShown()


def getInfoWindowProc(layoutID, contentData=DEFAULT_CONTENT_DATA, uiStorageKey=None, wndFlags=WindowFlags.WINDOW_FULLSCREEN | WindowFlags.WINDOW):
    return _InfoWindowProcessor(layoutID, contentData, uiStorageKey, wndFlags)
