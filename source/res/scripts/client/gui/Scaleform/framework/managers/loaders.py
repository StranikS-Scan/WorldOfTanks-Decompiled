# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/loaders.py
import Event
import constants
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_UNEXPECTED
from shared_utils import CONST_CONTAINER
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.LoaderManagerMeta import LoaderManagerMeta
from gui.Scaleform.framework.entities.View import View, ViewKey
NO_IMPL_ALIAS = 'noImpl'
NO_IMPL_URL = 'development/noImpl.swf'

class _LoadingItem(object):
    __slots__ = ('loadParams', 'pyEntity', 'factoryIdx', 'args', 'kwargs', 'isCancelled')

    def __init__(self, loadParams, pyEntity, factoryIdx, args, kwargs):
        super(_LoadingItem, self).__init__()
        self.loadParams = loadParams
        self.pyEntity = pyEntity
        self.factoryIdx = factoryIdx
        self.args = args
        self.kwargs = kwargs
        self.isCancelled = False

    def __repr__(self):
        return '{}[{}]=[loadParams={}, pyEntity={}]'.format(self.__class__.__name__, hex(id(self)), self.loadParams, self.pyEntity)

    @property
    def name(self):
        return self.loadParams.viewKey.name

    @property
    def loadMode(self):
        return self.loadParams.loadMode


class ViewLoadMode(CONST_CONTAINER):
    DEFAULT = 'default'
    PRELOAD = 'preload'


class ViewLoadParams(object):
    __slots__ = ('__viewKey', '__loadMode')

    def __init__(self, alias, name=None, loadMode=ViewLoadMode.DEFAULT):
        super(ViewLoadParams, self).__init__()
        self.__viewKey = ViewKey(alias, name)
        self.__loadMode = loadMode

    def __repr__(self):
        return '{}[viewKey={}, loadMode={}]'.format(self.__class__.__name__, self.__viewKey, self.__loadMode)

    @property
    def viewKey(self):
        return self.__viewKey

    @property
    def loadMode(self):
        return self.__loadMode


class LoaderManager(LoaderManagerMeta):

    def __init__(self, app):
        super(LoaderManager, self).__init__()
        self.__eManager = Event.EventManager()
        self.onViewLoadInit = Event.Event(self.__eManager)
        self.onViewLoaded = Event.Event(self.__eManager)
        self.onViewLoadError = Event.Event(self.__eManager)
        self.onViewLoadCanceled = Event.Event(self.__eManager)
        self.__app = app
        self.__loadingItems = {}

    def __repr__(self):
        return '{}[{}]=[loadingItems=[{}]]'.format(self.__class__.__name__, hex(id(self)), self.__loadingItems)

    def loadView(self, loadParams, *args, **kwargs):
        return self.__doLoadView(loadParams, *args, **kwargs)

    def cancelLoading(self, key):
        if key in self.__loadingItems:
            item = self.__loadingItems.pop(key)
            item.pyEntity.onDispose -= self.__handleViewDispose
            item.isCancelled = True
            self.as_cancelLoadViewS(key.name)
            self.onViewLoadCanceled(key, item)
            if not item.pyEntity.isDisposed():
                item.pyEntity.destroy()

    def getViewLoadingItem(self, key):
        return self.__loadingItems.get(key, None)

    def isViewLoading(self, key):
        return key in self.__loadingItems

    def viewLoaded(self, alias, name, gfxEntity):
        viewKey = ViewKey(alias, name)
        if viewKey in self.__loadingItems:
            item = self.__loadingItems.pop(viewKey)
            if item.isCancelled:
                self.onViewLoadCanceled(viewKey, item)
            else:
                pyEntity = g_entitiesFactories.initialize(item.pyEntity, gfxEntity, item.factoryIdx, extra={'name': item.name})
                item.pyEntity.onDispose -= self.__handleViewDispose
                if pyEntity is not None:
                    self.onViewLoaded(pyEntity, item.loadParams)
                else:
                    msg = 'An error occurred before DAAPI initialization. View {} will be destroyed.'.format(item.pyEntity)
                    LOG_ERROR(msg)
                    if not item.pyEntity.isDisposed():
                        item.pyEntity.destroy()
                    self.onViewLoadError(viewKey, msg, item)
        else:
            LOG_ERROR('View loading for key has no associated data', viewKey)
        return

    def viewLoadCanceled(self, alias, name):
        viewKey = ViewKey(alias, name)
        if viewKey in self.__loadingItems:
            LOG_UNEXPECTED('View loading for key {} has been canceled on FE side.'.format(viewKey), self.__loadingItems[viewKey])
            self.cancelLoading(viewKey)

    def viewLoadError(self, alias, name, errorTxt):
        viewKey = ViewKey(alias, name)
        msg = 'Error occurred during view {0} loading. Error:{1}'.format(viewKey, errorTxt)
        LOG_ERROR(msg)
        if viewKey in self.__loadingItems:
            item = self.__loadingItems.pop(viewKey)
            if item.isCancelled:
                self.onViewLoadCanceled(viewKey, item)
            else:
                self.onViewLoadError(viewKey, msg, item)
                if item is not None:
                    settings = item.pyEntity.settings
                    if constants.IS_DEVELOPMENT and settings.url != NO_IMPL_URL:
                        g_entitiesFactories.addSettings(ViewSettings(NO_IMPL_ALIAS, View, NO_IMPL_URL, settings.type, None, ScopeTemplates.DEFAULT_SCOPE, False))
                        LOG_WARNING('Try to load noImpl swf...')
                        self.__doLoadView(ViewLoadParams(NO_IMPL_ALIAS, item.name))
        else:
            LOG_WARNING('View loading for name has no associated data', name)
        return

    def viewInitializationError(self, alias, name):
        viewKey = ViewKey(alias, name)
        msg = "View '{0}' does not implement net.wg.infrastructure.interfaces.IView".format(viewKey)
        LOG_ERROR(msg)
        item = None
        if viewKey in self.__loadingItems:
            item = self.__loadingItems.pop(viewKey)
            pyEntity = item.pyEntity
            pyEntity.destroy()
        self.onViewLoadError(viewKey, msg, item)
        return

    def _dispose(self):
        self.__app = None
        self.__loadingItems.clear()
        self.__eManager.clear()
        super(LoaderManager, self)._dispose()
        return

    def __handleViewDispose(self, view):
        self.cancelLoading(view.key)

    def __doLoadView(self, loadParams, *args, **kwargs):
        key = loadParams.viewKey
        viewTutorialID = self.__app.tutorialManager.getViewTutorialID(key.name)
        pyEntity = None
        if key in self.__loadingItems:
            item = self.__loadingItems[key]
            item.isCancelled = False
            if not item.pyEntity.isDisposed():
                pyEntity = item.pyEntity
        if pyEntity is not None:
            pyEntity.onDispose += self.__handleViewDispose
            viewDict = {'config': pyEntity.settings.getDAAPIObject(),
             'alias': key.alias,
             'name': key.name,
             'viewTutorialId': viewTutorialID}
            self.as_loadViewS(viewDict)
        else:
            pyEntity, factoryIdx = g_entitiesFactories.factory(key.alias, *args, **kwargs)
            if pyEntity is not None:
                pyEntity.setUniqueName(key.name)
                pyEntity.setEnvironment(self.__app)
                pyEntity.onDispose += self.__handleViewDispose
                self.__loadingItems[key] = _LoadingItem(loadParams, pyEntity, factoryIdx, args, kwargs)
                self.onViewLoadInit(pyEntity)
                viewDict = {'config': pyEntity.settings.getDAAPIObject(),
                 'alias': key.alias,
                 'name': key.name,
                 'viewTutorialId': viewTutorialID}
                self.as_loadViewS(viewDict)
            else:
                LOG_WARNING('PyEntity for alias %s is None' % key.alias)
        return pyEntity
