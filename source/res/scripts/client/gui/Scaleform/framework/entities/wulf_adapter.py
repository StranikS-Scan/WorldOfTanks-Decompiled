# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/wulf_adapter.py
import logging
from functools import partial
import typing
import BigWorld
from Event import Event, EventManager
from frameworks.wulf import WindowStatus, WindowLayer
from frameworks.wulf.gui_constants import ShowingStatus
from gui.impl.pub import WindowImpl
from .View import ViewKey
_logger = logging.getLogger(__name__)

class WulfPackageLayoutAdapter(object):
    __slots__ = ('__window', '__loadID', '__sfWindow', '__key', '__scope', '__settings', '__eManager', '__app', '__isDestroyed', 'onCreated', 'onDispose', 'onDisposed', 'onWulfViewLoaded', 'onWulfViewLoadError', '__background_alpha__')

    def __init__(self):
        super(WulfPackageLayoutAdapter, self).__init__()
        self.__background_alpha__ = 0.0
        self.__window = None
        self.__loadID = None
        self.__app = None
        self.__isDestroyed = False
        self.__key = ViewKey(None, None)
        self.__sfWindow = None
        from gui.Scaleform.framework import ScopeTemplates
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        from gui.Scaleform.framework import ViewSettings
        self.__settings = ViewSettings()
        self.__eManager = EventManager()
        self.onCreated = Event(self.__eManager)
        self.onDispose = Event(self.__eManager)
        self.onDisposed = Event(self.__eManager)
        self.onWulfViewLoaded = Event(self.__eManager)
        self.onWulfViewLoadError = Event(self.__eManager)
        return

    @classmethod
    def shoudBeWrapped(cls, windowClass):
        return issubclass(windowClass, WindowImpl)

    def create(self):
        self.onCreated(self)

    def initWindow(self, windowClass, *args, **kwargs):
        window = windowClass(*args, **kwargs)
        window.onStatusChanged += self.__onStatusChanged
        window.onShowingStatusChanged += self.__onShowingStatusChanged
        self.__window = window
        if hasattr(window, '__background_alpha__'):
            self.__background_alpha__ = window.__background_alpha__
        self.__window.onReady += partial(self.onWulfViewLoaded, self)

    def load(self):
        if self.__window.content is None and self.__window.decorator is None:
            if self.__loadID is not None:
                BigWorld.cancelCallback(self.__loadID)
                self.__loadID = None
            self.__loadID = BigWorld.callback(0.0, self.__windowLoad)
        else:
            self.__windowLoad()
        return

    @property
    def uiImpl(self):
        from gui.Scaleform.framework import UIFrameworkImpl
        return UIFrameworkImpl.WULF_WINDOW

    def isCreated(self):
        return self.__window.windowStatus not in (WindowStatus.UNDEFINED, WindowStatus.DESTROYED)

    def isDisposed(self):
        return self.__isDestroyed

    def setEnvironment(self, app):
        self.__app = app

    def setUniqueName(self, name):
        if name is not None:
            self.__key = ViewKey(self.alias, name)
        else:
            _logger.debug('Unique name cannot be set to None: %r', self)
        return

    @property
    def key(self):
        return self.__key

    def getSubContainersSettings(self):
        pass

    @property
    def alias(self):
        return self.__key.alias

    def getAlias(self):
        return self.__key.alias

    @property
    def layer(self):
        return self.__settings.layer

    @property
    def uniqueName(self):
        return self.__key.name

    @property
    def viewScope(self):
        return self.__settings.scope

    def setSettings(self, settings):
        from gui.Scaleform.framework import ScopeTemplates
        if settings is not None:
            self.__settings = settings.toImmutableSettings()
            if self.__settings.scope != ScopeTemplates.DYNAMIC_SCOPE:
                self.__scope = self.__settings.scope
            self.__key = ViewKey(self.__settings.alias, self.uniqueName)
        else:
            _logger.error('settings can`t be None!')
        return

    @property
    def settings(self):
        return self.__settings

    def getCurrentScope(self):
        return self.__scope

    def destroy(self):
        self.__isDestroyed = True
        self.onDispose(self)
        if self.__window:
            if self.__loadID is not None:
                BigWorld.cancelCallback(self.__loadID)
                self.__loadID = None
            self.__window.onStatusChanged -= self.__onStatusChanged
            self.__window.onShowingStatusChanged -= self.__onShowingStatusChanged
            self.__window.destroy()
            self.__window = None
        self.__app = None
        self.onDisposed(self)
        self.__eManager.clear()
        return

    def isViewModal(self):
        return self.__window.isModal()

    def validate(self, *args, **kwargs):
        pass

    def setParentWindow(self, window):
        self.__sfWindow = window

    def getParentWindow(self):
        return self.__sfWindow

    @property
    def content(self):
        return self.__window.content if self.__window else None

    def __repr__(self):
        return '{} (key = {}, settings = {}, window = {}, isDestroyed = {})'.format(self.__class__.__name__, self.__key, self.__settings, self.__window, self.__isDestroyed)

    def __windowLoad(self):
        self.__loadID = None
        self.__window.load()
        return

    def __onStatusChanged(self, newStatus):
        if newStatus == WindowStatus.DESTROYING and self.__window.windowStatus != WindowStatus.LOADED:
            self.onWulfViewLoadError(self)
        elif newStatus == WindowStatus.DESTROYED:
            if not self.__isDestroyed:
                self.__sfWindow.destroy()
            self.__sfWindow = None
        return

    def __onShowingStatusChanged(self, newStatus):
        if newStatus == ShowingStatus.SHOWING and self.__window.layer == WindowLayer.SUB_VIEW:
            self.__app.setBackgroundAlpha(self.__background_alpha__)
