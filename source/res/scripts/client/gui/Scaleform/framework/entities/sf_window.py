# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/sf_window.py
import logging
import weakref
import typing
from async import async, await, AsyncReturn
import Event
from frameworks.wulf import WindowSettings, Window, WindowStatus, WindowFlags
from gui.Scaleform.framework import g_entitiesFactories
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
    from gui.Scaleform.framework.entities.View import View
_logger = logging.getLogger(__name__)

class SFWindow(Window):
    __slots__ = ('__loadParams', '__scope', '__fireEvent', '__view', 'args', 'kwargs', 'onContentLoaded')

    def __init__(self, loadParams, scope=EVENT_BUS_SCOPE.DEFAULT, fireEvent=True, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.onContentLoaded = Event.Event()
        self.__loadParams = loadParams
        self.__view = None
        self.__scope = scope
        self.__fireEvent = fireEvent
        viewSettings = g_entitiesFactories.getSettings(loadParams.viewKey.alias)
        settings = WindowSettings()
        settings.flags = viewSettings.flags or WindowFlags.SERVICE_WINDOW
        settings.layer = viewSettings.layer
        settings.parent = loadParams.parent
        super(SFWindow, self).__init__(settings)
        self.__loadParams.window = weakref.proxy(self)
        _logger.debug('Creating %r with %r', self, loadParams)
        return

    @property
    def loadParams(self):
        return self.__loadParams

    @property
    def content(self):
        return self.__view

    @property
    def windowStatus(self):
        status = super(SFWindow, self).windowStatus
        return WindowStatus.LOADING if status == WindowStatus.LOADED and self.__view is None else status

    def isParamsEqual(self, loadParams, scope=EVENT_BUS_SCOPE.DEFAULT, fireEvent=True, *args, **kwargs):
        return self.__loadParams.viewKey == loadParams.viewKey and self.args == args and self.kwargs == kwargs

    def load(self):
        _logger.debug('Loading window: %r', self)
        if self.windowStatus != WindowStatus.CREATED:
            raise SoftException('Window {} has already loaded!'.format(self.__loadParams.viewKey))
        super(SFWindow, self).load()
        if self.__fireEvent:
            g_eventBus.handleEvent(events.LoadViewEvent(self.__loadParams, *self.args, **self.kwargs), self.__scope)

    def setContent(self, view):
        self.__view = view
        view.onDispose += self.__onViewDispose

    def setViewLoaded(self):
        _logger.debug('Content has been loaded: %r', self)
        self.onContentLoaded(self)
        self.onStatusChanged(WindowStatus.LOADED)

    @async
    def wait(self):
        _wait = getattr(self.content, 'wait')
        result = yield await(_wait())
        raise AsyncReturn(result)

    def _finalize(self):
        if self.__view is not None:
            self.__view.onDispose -= self.__onViewDispose
            if not self.__view.isDisposed():
                self.__view.destroy()
            self.__view = None
        self.onContentLoaded.clear()
        _logger.debug('View had finalized: %r', self)
        super(SFWindow, self)._finalize()
        return

    def __onViewDispose(self, _):
        self.destroy()
