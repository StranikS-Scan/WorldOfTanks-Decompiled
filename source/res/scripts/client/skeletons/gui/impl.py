# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/impl.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from frameworks.wulf import ViewModel
    from frameworks.wulf.tutorial import Tutorial
    from frameworks.wulf.ui_logger import UILogger
    from frameworks.wulf.markers_manager import MarkersManager

class IGuiLoader(object):
    __slots__ = ()

    @property
    def resourceManager(self):
        raise NotImplementedError

    @property
    def windowsManager(self):
        raise NotImplementedError

    @property
    def systemLocale(self):
        raise NotImplementedError

    @property
    def tutorial(self):
        raise NotImplementedError

    @property
    def markers(self):
        raise NotImplementedError

    @property
    def uiLogger(self):
        raise NotImplementedError

    def init(self, tutorialModel, uiLoggerModel):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class INotificationWindowController(IGameController):
    __slots__ = ('onPostponedQueueUpdated',)
    if typing.TYPE_CHECKING:
        onPostponedQueueUpdated = None

    def append(self, window):
        raise NotImplementedError

    def hasWindow(self, window):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isExecuting(self):
        raise NotImplementedError

    def postponeActive(self):
        raise NotImplementedError

    def releasePostponed(self):
        raise NotImplementedError

    def lock(self, key):
        raise NotImplementedError

    def unlock(self, key):
        raise NotImplementedError

    def hasLock(self, key):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def postponedCount(self):
        raise NotImplementedError


class IFullscreenManager(object):
    __slots__ = ()

    def setEnabled(self, value):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class IWindowLoaderController(IGameController):
    __slots__ = ()


class IOverlaysManager(object):
    __slots__ = ()

    def isSuspended(self, window):
        raise NotImplementedError

    def suspend(self, condition=None):
        raise NotImplementedError

    def release(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class INewYearNavigation(object):
    onObjectStateChanged = None
    onUpdateCurrentView = None

    @classmethod
    def closeMainView(cls, switchCamera=False):
        raise NotImplementedError

    @classmethod
    def showMainView(cls, objectName, instantly=False, viewAlias=None, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def showInfoView(cls, previousViewAlias=None, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def showNavigationView(cls, viewAlias=None):
        raise NotImplementedError

    @classmethod
    def switchToIntro(cls):
        raise NotImplementedError

    @classmethod
    def switchByAnchorName(cls, anchorName):
        raise NotImplementedError

    @classmethod
    def switchFromStyle(cls, objectName, viewAlias=None, tabName=None, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def switchToQuests(cls, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def getCurrentObject(cls):
        raise NotImplementedError

    @classmethod
    def getCurrentViewName(cls):
        raise NotImplementedError

    @classmethod
    def getPreviousObject(cls):
        raise NotImplementedError

    @classmethod
    def switchToView(cls, aliasName, tabName=None, instantly=False, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def switchTo(cls, objectName, instantly=False, viewAlias=None, withFade=False, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def clear(cls):
        raise NotImplementedError
