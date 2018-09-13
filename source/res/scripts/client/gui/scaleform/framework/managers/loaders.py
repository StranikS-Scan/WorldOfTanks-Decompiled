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
_TokenItem = namedtuple('_TokenItem', ('name', 'pyEntity', 'factoryIdx', 'args', 'kwargs'))
NO_IMPL_ALIAS = 'noImpl'
NO_IMPL_URL = 'development/noImpl.swf'

class LoaderManager(LoaderManagerMeta):
    eManager = Event.EventManager()
    onViewLoadInit = Event.Event(eManager)
    onViewLoaded = Event.Event(eManager)
    onViewLoadError = Event.Event(eManager)

    def __init__(self):
        super(LoaderManager, self).__init__()
        self.__tokens = {}

    def loadView(self, alias, name, *args, **kwargs):
        token = uuid.uuid4().hex
        return self.__loadViewForToken(alias, name, token, *args, **kwargs)

    def isViewLoading(self, viewAlias):
        result = False
        for item in self.__tokens.itervalues():
            pyEntity = item.pyEntity
            if pyEntity and pyEntity.settings.alias == viewAlias:
                result = True
                break

        return result

    def viewLoaded(self, token, gfxEntity):
        if token in self.__tokens:
            item = self.__tokens.pop(token)
            pyEntity = g_entitiesFactories.initialize(item.pyEntity, gfxEntity, item.factoryIdx, extra={'name': item.name,
             'token': token})
            if pyEntity is not None:
                self.onViewLoaded(pyEntity)
            else:
                LOG_ERROR('Error during until DAAPI initializing.')
        else:
            LOG_ERROR('View load for token has no associated data', token)
        return

    def viewLoadError(self, token, name, errorTxt):
        msg = 'Error during view {0} load. Token: {1}, error:{2}'
        msg = msg.format(name, token, errorTxt)
        LOG_ERROR(msg)
        item = None
        if token in self.__tokens:
            item = self.__tokens.pop(token)
        self.onViewLoadError(token, msg, item)
        if item is not None:
            settings = item.pyEntity.settings
            if constants.IS_DEVELOPMENT and settings.url != NO_IMPL_URL:
                g_entitiesFactories.addSettings(ViewSettings(NO_IMPL_ALIAS, View, NO_IMPL_URL, settings.type, None, ScopeTemplates.DEFAULT))
                LOG_WARNING('Try to load noImpl swf...')
                self.__loadViewForToken(NO_IMPL_ALIAS, item.name, token)
        return

    def cancelLoadingByToken(self, token):
        if token in self.__tokens:
            self.__tokens.pop(token)

    def viewInitializationError(self, token, config, alias):
        msg = "View '{0}' does not implement net.wg.infrastructure.interfaces.IView"
        msg = msg.format(alias)
        LOG_ERROR(msg)
        item = None
        if token in self.__tokens:
            item = self.__tokens.pop(token)
            pyEntity = item.pyEntity
            pyEntity.destroy()
        self.onViewLoadError(token, msg, item)
        return

    def _dispose(self):
        self.__tokens.clear()
        self.eManager.clear()
        super(LoaderManager, self)._dispose()

    def __loadViewForToken(self, alias, name, token, *args, **kwargs):
        if token in self.__tokens:
            item = self.__tokens[token]
            self.as_loadViewS(item.pyEntity.settings._asdict(), token, alias, name)
            return item.pyEntity
        else:
            pyEntity, factoryIdx = g_entitiesFactories.factory(alias, *args, **kwargs)
            if pyEntity is not None:
                self.__tokens[token] = _TokenItem(name, pyEntity, factoryIdx, args, kwargs)
                pyEntity.setToken(token)
                self.onViewLoadInit(pyEntity)
                self.as_loadViewS(pyEntity.settings._asdict(), token, alias, name)
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
