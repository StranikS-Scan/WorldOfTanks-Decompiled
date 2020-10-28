# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/package_layout.py
import importlib
import logging
from frameworks.wulf import WindowLayer
from gui.shared.events import ViewEventType
from soft_exception import SoftException
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.managers import context_menu
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from ids_generators import SequenceIDGenerator
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_addListener = g_eventBus.addListener
_removeListener = g_eventBus.removeListener

class PackageBusinessHandler(object):
    __counter = SequenceIDGenerator()
    __slots__ = ('_listeners', '_scope', '_app', '_appNS')

    def __init__(self, listeners, appNS=None, scope=None):
        super(PackageBusinessHandler, self).__init__()
        self._listeners = listeners
        self._scope = scope or EVENT_BUS_SCOPE.GLOBAL
        self._app = None
        self._appNS = appNS
        return

    def getScope(self):
        return self._scope

    def getAppNS(self):
        return self._appNS

    def setApp(self, app):
        self._app = app

    def init(self):
        _addListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, self._scope)

    def fini(self):
        self._app = None
        _removeListener(ViewEventType.LOAD_VIEW, self.__loadViewHandler, self._scope)
        self._listeners = ()
        return

    def loadViewWithDefName(self, alias, name=None, *args, **kwargs):
        self._app.loadView(SFViewLoadParams(alias, name), *args, **kwargs)

    def loadViewWithGenName(self, alias, *args, **kwargs):
        self._app.loadView(SFViewLoadParams(alias, 'rw{0}'.format(self.__counter.next())), *args, **kwargs)

    def loadViewBySharedEvent(self, event):
        self._app.loadView(event.loadParams)

    def loadViewByCtxEvent(self, event):
        self._app.loadView(event.loadParams, event.ctx)

    def loadView(self, event):
        self._app.loadView(event.loadParams, *event.args, **event.kwargs)

    def findViewByAlias(self, layer, alias):
        container = self.__getContainer(layer)
        return None if not container else container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias})

    def findViewByName(self, layer, name):
        container = self.__getContainer(layer)
        return None if not container else container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: name})

    def bringViewToFront(self, name):
        manager = self._app.containerManager if self._app else None
        if manager is None:
            return
        else:
            isOnTop = manager.as_isOnTopS(WindowLayer.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(WindowLayer.WINDOW, name)
            return

    def __getContainer(self, layer):
        if not self._app:
            return None
        else:
            manager = self._app.containerManager
            return None if not manager else manager.getContainer(layer)

    def __loadViewHandler(self, event):
        alias = event.alias
        for viewAlias, listener in self._listeners:
            if viewAlias == alias:
                listener(event)


class PackageImporter(object):
    __slots__ = ('_aliases', '_handlers', '_contextMenuTypes')

    def __init__(self):
        super(PackageImporter, self).__init__()
        self._aliases = {}
        self._handlers = {}
        self._contextMenuTypes = {}

    def isPackageLoaded(self, path):
        return path in self._handlers

    def getLoadedPackages(self):
        return self._handlers.keys()

    def getAliasesByPackage(self, path):
        return self._aliases.get(path)

    def load(self, app, seq):
        load = self._loadPackage
        for path in seq:
            load(path)

        appNS = app.appNS
        for handlers in self._handlers.itervalues():
            for handler in handlers:
                required = handler.getAppNS()
                if required is None or required == appNS:
                    handler.setApp(app)

        return

    def unload(self, seq=None):
        if seq is None:
            seq = self._handlers.keys()
        isLoaded = self.isPackageLoaded
        clearSettings = g_entitiesFactories.clearSettings
        for path in seq:
            if not isLoaded(path):
                continue
            _logger.debug('Tries to unload GUI package "%s"', path)
            handlers = self._handlers.pop(path)
            for handler in handlers:
                handler.fini()

            aliases = self._aliases.pop(path)
            if aliases:
                clearSettings(aliases)
            contextMenuTypes = self._contextMenuTypes.pop(path)
            if contextMenuTypes:
                context_menu.unregisterHandlers(*contextMenuTypes)

        return

    def _loadPackage(self, path):
        if self.isPackageLoaded(path):
            return
        _logger.debug('Tries to load GUI package "%s"', path)
        imported = importlib.import_module(path)
        try:
            settings = imported.getViewSettings()
        except AttributeError:
            _logger.exception('Package "%s" can not be loaded', path)
            raise SoftException('Package {0} does not have method getViewSettings'.format(path))

        aliases = g_entitiesFactories.initSettings(settings)
        try:
            handlers = imported.getContextMenuHandlers()
        except AttributeError:
            _logger.exception('Package "%s" can not be loaded', path)
            raise SoftException('Package {0} does not have method getContextMenuHandlers'.format(path))

        contextMenuTypes = context_menu.registerHandlers(*handlers)
        try:
            handlers = imported.getBusinessHandlers()
        except AttributeError:
            _logger.exception('Package "%s" can not be loaded', path)
            raise SoftException('Package {0} does not have method getBusinessHandlers'.format(path))

        processed = set()
        for handler in handlers:
            if not isinstance(handler, PackageBusinessHandler):
                for h in processed:
                    h.fini()

                raise SoftException('Package {0} has invalid business handler {1}'.format(path, handler.__class__.__name__))
            handler.init()
            processed.add(handler)

        self._aliases[path] = aliases
        self._handlers[path] = processed
        self._contextMenuTypes[path] = contextMenuTypes
