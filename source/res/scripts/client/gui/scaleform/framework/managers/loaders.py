# Embedded file name: scripts/client/gui/Scaleform/framework/managers/loaders.py
from collections import namedtuple
import uuid
import Event
import constants
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, AppRef, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.entities.abstract.LoaderManagerMeta import LoaderManagerMeta
from ids_generators import SequenceIDGenerator
_LoadingItem = namedtuple('_LoadingItem', ('name', 'pyEntity', 'factoryIdx', 'args', 'kwargs'))
NO_IMPL_ALIAS = 'noImpl'
NO_IMPL_URL = 'development/noImpl.swf'

class LoaderManager(LoaderManagerMeta):
    eManager = Event.EventManager()
    onViewLoadInit = Event.Event(eManager)
    onViewLoaded = Event.Event(eManager)
    onViewLoadError = Event.Event(eManager)

    def __init__(self):
        super(LoaderManager, self).__init__()
        self.__nameToLoadingItem = {}

    def loadView(self, alias, name, *args, **kwargs):
        return self.__doLoadView(alias, name, *args, **kwargs)

    def isViewLoading(self, viewAlias):
        result = False
        for item in self.__nameToLoadingItem.itervalues():
            pyEntity = item.pyEntity
            if pyEntity and pyEntity.settings.alias == viewAlias:
                result = True
                break

        return result

    def viewLoaded(self, name, gfxEntity):
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            pyEntity = g_entitiesFactories.initialize(item.pyEntity, gfxEntity, item.factoryIdx, extra={'name': item.name})
            if pyEntity is not None:
                self.onViewLoaded(pyEntity)
            else:
                LOG_ERROR('Error during until DAAPI initializing.')
        else:
            LOG_ERROR('View load for name has no associated data', name)
        return

    def viewLoadError(self, alias, name, errorTxt):
        msg = 'Error during view {0} load. Name: {1}, error:{2}'
        msg = msg.format(alias, name, errorTxt)
        LOG_ERROR(msg)
        item = None
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
        self.onViewLoadError(name, msg, item)
        if item is not None:
            settings = item.pyEntity.settings
            if constants.IS_DEVELOPMENT and settings.url != NO_IMPL_URL:
                g_entitiesFactories.addSettings(ViewSettings(NO_IMPL_ALIAS, View, NO_IMPL_URL, settings.type, None, ScopeTemplates.DEFAULT))
                LOG_WARNING('Try to load noImpl swf...')
                self.__doLoadView(NO_IMPL_ALIAS, item.name)
        return

    def cancelLoadingByName(self, name):
        if name in self.__nameToLoadingItem:
            self.__nameToLoadingItem.pop(name)

    def viewInitializationError(self, config, alias, name):
        msg = "View '{0}' does not implement net.wg.infrastructure.interfaces.IView"
        msg = msg.format(alias)
        LOG_ERROR(msg)
        item = None
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            pyEntity = item.pyEntity
            pyEntity.destroy()
        self.onViewLoadError(name, msg, item)
        return

    def _dispose(self):
        self.__nameToLoadingItem.clear()
        self.eManager.clear()
        super(LoaderManager, self)._dispose()

    def __doLoadView(self, alias, name, *args, **kwargs):
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem[name]
            self.as_loadViewS(item.pyEntity.settings._asdict(), alias, name)
            return item.pyEntity
        else:
            pyEntity, factoryIdx = g_entitiesFactories.factory(alias, *args, **kwargs)
            if pyEntity is not None:
                pyEntity.setUniqueName(name)
                self.__nameToLoadingItem[name] = _LoadingItem(name, pyEntity, factoryIdx, args, kwargs)
                self.onViewLoadInit(pyEntity)
                self.as_loadViewS(pyEntity.settings._asdict(), alias, name)
                return pyEntity
            LOG_WARNING('PyEntity for alias %s is None' % alias)
            return
            return


class SequenceIDLoader(EventSystemEntity, AppRef):
    __counter = SequenceIDGenerator()

    def __init__(self):
        super(SequenceIDLoader, self).__init__()

    def _loadView(self, alias, *args, **kwargs):
        self.app.loadView(alias, 'rw{0}'.format(self.__counter.next()), *args, **kwargs)


class PackageBusinessHandler(SequenceIDLoader):

    def __init__(self, listeners, scope = 0):
        super(PackageBusinessHandler, self).__init__()
        self._listeners = listeners
        self._scope = scope

    def init(self):
        for eventType, listener in self._listeners:
            self.addListener(eventType, listener, self._scope)

    def fini(self):
        while len(self._listeners):
            eventType, listener = self._listeners.pop()
            self.removeListener(eventType, listener, self._scope)
