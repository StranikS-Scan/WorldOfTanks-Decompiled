# Embedded file name: scripts/client/gui/Scaleform/framework/package_layout.py
from gui.Scaleform.framework import g_entitiesFactories, ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from ids_generators import SequenceIDGenerator
_SF_SETTING_NAME = '__init__'
_SF_SETTING_PATH = '{0:>s}.' + _SF_SETTING_NAME
_addListener = g_eventBus.addListener
_removeListener = g_eventBus.removeListener

class PackageBusinessHandler(object):
    __counter = SequenceIDGenerator()
    __slots__ = ('_listeners', '_scope', '_app', '_appNS')

    def __init__(self, listeners, appNS = None, scope = None):
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
        for eventType, listener in self._listeners:
            _addListener(eventType, listener, self._scope)

    def fini(self):
        self._app = None
        for eventType, listener in self._listeners:
            _removeListener(eventType, listener, self._scope)

        self._listeners = ()
        return

    def loadViewWithDefName(self, alias, *args, **kwargs):
        self._app.loadView(alias, *args, **kwargs)

    def loadViewWithGenName(self, alias, *args, **kwargs):
        self._app.loadView(alias, 'rw{0}'.format(self.__counter.next()), *args, **kwargs)

    def loadViewBySharedEvent(self, event):
        self._app.loadView(event.eventType, event.name)

    def loadViewByCtxEvent(self, event):
        self._app.loadView(event.eventType, event.name, event.ctx)

    def findViewByAlias(self, viewType, alias):
        container = self.__getContainer(viewType)
        if not container:
            return None
        else:
            return container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: alias})

    def findViewByName(self, viewType, name):
        container = self.__getContainer(viewType)
        if not container:
            return None
        else:
            return container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: name})

    def bringViewToFront(self, name):
        manager = self._app.containerManager if self._app else None
        if manager is None:
            return
        else:
            isOnTop = manager.as_isOnTopS(ViewTypes.WINDOW, name)
            if not isOnTop:
                manager.as_bringToFrontS(ViewTypes.WINDOW, name)
            return

    def __getContainer(self, viewType):
        if not self._app:
            return None
        else:
            manager = self._app.containerManager
            if not manager:
                return None
            return manager.getContainer(viewType)


class PackageImporter(object):
    __slots__ = ('_aliases', '_handlers')

    def __init__(self):
        super(PackageImporter, self).__init__()
        self._aliases = {}
        self._handlers = {}

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

    def unload(self, seq = None):
        if seq is None:
            seq = self._handlers.keys()
        isLoaded = self.isPackageLoaded
        clearSettings = g_entitiesFactories.clearSettings
        for path in seq:
            if not isLoaded(path):
                continue
            handlers = self._handlers.pop(path)
            for handler in handlers:
                handler.fini()

            aliases = self._aliases.pop(path)
            if aliases:
                clearSettings(aliases)

        return

    def _loadPackage(self, path):
        if self.isPackageLoaded(path):
            return
        imported = __import__(_SF_SETTING_PATH.format(path), fromlist=[_SF_SETTING_NAME])
        try:
            settings = imported.getViewSettings()
        except AttributeError:
            raise Exception, 'Package {0} does not have method getViewSettings'.format(path)

        aliases = g_entitiesFactories.initSettings(settings)
        handlers = imported.getBusinessHandlers()
        processed = set()
        for handler in handlers:
            if not isinstance(handler, PackageBusinessHandler):
                for handler in processed:
                    handler.fini()

                raise Exception, 'Package {0} has invalid business handler {1}'.format(path, handler.__class__.__name__)
            handler.init()
            processed.add(handler)

        self._aliases[path] = aliases
        self._handlers[path] = processed
