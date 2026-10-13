# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/impl.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from frameworks.wulf.resource_manager import ResourceManager
    from frameworks.wulf.system_locale import SystemLocale
    from frameworks.wulf.formatters import Formatters
    from frameworks.wulf.tutorial import Tutorial
    from frameworks.wulf.ui_logger import UILogger
    from frameworks.wulf.windows_system.windows_manager import WindowsManager
    from frameworks.wulf.view.layout_manager import LayoutManager
    from gui.impl.gui_factories import GuiEntitiesFactories

class IGuiLoader(object):
    __slots__ = ()

    @property
    def resourceManager(self):
        raise NotImplementedError

    @property
    def windowsManager(self):
        raise NotImplementedError

    @property
    def layoutManager(self):
        raise NotImplementedError

    @property
    def systemLocale(self):
        raise NotImplementedError

    @property
    def formatters(self):
        raise NotImplementedError

    @property
    def tutorial(self):
        raise NotImplementedError

    @property
    def uiLogger(self):
        raise NotImplementedError

    @property
    def scale(self):
        raise NotImplementedError

    @property
    def entitiesFactory(self):
        raise NotImplementedError

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError


class INotificationWindowController(IGameController):
    if typing.TYPE_CHECKING:
        onPostponedQueueUpdated = None

    def append(self, command):
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

    @property
    def activeQueueLength(self):
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
