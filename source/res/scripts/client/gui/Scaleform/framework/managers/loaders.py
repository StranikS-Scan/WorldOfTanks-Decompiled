# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/loaders.py
import logging
import Event
import constants
from gui.Scaleform.framework.entities.ub_view_adaptor import UnboundViewAdaptor
from gui.Scaleform.framework.settings import UIFrameworkImpl
from helpers import dependency
from shared_utils import CONST_CONTAINER
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.abstract.LoaderManagerMeta import LoaderManagerMeta
from gui.Scaleform.framework.entities.View import View, ViewKey
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
NO_IMPL_ALIAS = 'noImpl'
NO_IMPL_URL = 'development/noImpl.swf'
_logger = logging.getLogger(__name__)

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

    def __init__(self, viewKey, loadMode=ViewLoadMode.DEFAULT):
        super(ViewLoadParams, self).__init__()
        self.__viewKey = viewKey
        self.__loadMode = loadMode

    def __repr__(self):
        return '{}[viewKey={}, loadMode={}]'.format(self.__class__.__name__, self.__viewKey, self.loadMode)

    @property
    def uiImpl(self):
        return UIFrameworkImpl.UNDEFINED

    @property
    def viewKey(self):
        return self.__viewKey

    @property
    def loadMode(self):
        return self.__loadMode


class SFViewLoadParams(ViewLoadParams):
    __slots__ = ()

    def __init__(self, alias, name=None, loadMode=ViewLoadMode.DEFAULT):
        super(SFViewLoadParams, self).__init__(ViewKey(alias, name), loadMode=loadMode)

    @property
    def uiImpl(self):
        return UIFrameworkImpl.SCALEFORM


class UBViewLoadParams(ViewLoadParams):
    __slots__ = ('__viewClass',)

    def __init__(self, layoutID, viewClass, loadMode=ViewLoadMode.DEFAULT):
        super(UBViewLoadParams, self).__init__(ViewKey(layoutID, None), loadMode=loadMode)
        self.__viewClass = viewClass
        return

    @property
    def uiImpl(self):
        return UIFrameworkImpl.UNBOUND

    @property
    def viewClass(self):
        return self.__viewClass


class LoaderManager(LoaderManagerMeta):
    uiLoader = dependency.descriptor(IGuiLoader)

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
        if loadParams.uiImpl == UIFrameworkImpl.UNBOUND:
            return self.__doLoadUBView(loadParams, *args, **kwargs)
        if loadParams.uiImpl == UIFrameworkImpl.SCALEFORM:
            return self.__doLoadSFView(loadParams, *args, **kwargs)
        raise SoftException('View can not be loaded. UI implementation "{}" is not handled'.format(loadParams.uiImpl))

    def cancelLoading(self, key):
        if key.name is None:
            _logger.error('View loading can not be canceled by key %r', key)
            return
        else:
            if key in self.__loadingItems:
                item = self.__loadingItems.pop(key)
                item.pyEntity.onDispose -= self.__handleViewDispose
                item.isCancelled = True
                self.as_cancelLoadViewS(key.name)
                self.onViewLoadCanceled(key, item)
                if not item.pyEntity.isDisposed():
                    item.pyEntity.destroy()
            return

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
                    msg = 'An error occurred before view initialization. View {} will be destroyed.'.format(item.pyEntity)
                    _logger.error(msg)
                    if not item.pyEntity.isDisposed():
                        item.pyEntity.destroy()
                    self.onViewLoadError(viewKey, msg, item)
        else:
            _logger.error('View loading for key has no associated data: %r', viewKey)
        return

    def viewLoadCanceled(self, alias, name):
        viewKey = ViewKey(alias, name)
        if viewKey in self.__loadingItems:
            _logger.warning('View loading for key %r has been canceled on FE side: %r.', viewKey, self.__loadingItems[viewKey])
            self.cancelLoading(viewKey)

    def viewLoadError(self, alias, name, errorTxt):
        viewKey = ViewKey(alias, name)
        msg = 'Error occurred during view {0} loading. Error:{1}'.format(viewKey, errorTxt)
        _logger.error(msg)
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
                        _logger.warning('Try to load noImpl swf...')
                        self.__doLoadSFView(SFViewLoadParams(NO_IMPL_ALIAS, item.name))
        else:
            _logger.warning('View loading for name has no associated data: %s', name)
        return

    def viewInitializationError(self, alias, name):
        viewKey = ViewKey(alias, name)
        msg = "View '{0}' does not implement net.wg.infrastructure.interfaces.IView".format(viewKey)
        _logger.error(msg)
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

    def __handleViewLoaded(self, view):
        viewKey = view.key
        if viewKey not in self.__loadingItems:
            _logger.warning('View is already loaded or is not found: %r', viewKey)
            return
        item = self.__loadingItems.pop(viewKey)
        pyEntity = item.pyEntity
        pyEntity.onCreated -= self.__handleViewLoaded
        pyEntity.onDispose -= self.__handleViewDispose
        if item.isCancelled:
            self.onViewLoadCanceled(viewKey, item)
        else:
            self.onViewLoaded(pyEntity, item.loadParams)

    def __doLoadSFView(self, loadParams, *args, **kwargs):
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
                _logger.warning('PyEntity for alias %s is None', key.alias)
        return pyEntity

    def __doLoadUBView(self, loadParams, *args, **kwargs):
        key = loadParams.viewKey
        if key in self.__loadingItems:
            raise SoftException('This case in not implemented: {}'.format(loadParams))
        manager = self.uiLoader.windowsManager
        layoutID = loadParams.viewKey.alias
        viewClass = loadParams.viewClass
        if manager.getView(layoutID) is not None:
            raise SoftException('There is unexpected behavior,we have unbound view, but adaptor is not created: %r'.format(loadParams))
        ubView = viewClass(layoutID, *args, **kwargs)
        adaptor = UnboundViewAdaptor()
        adaptor.setView(ubView)
        if adaptor.isLoaded():
            raise SoftException('Synchronous loading does not supported: {}'.format(loadParams))
        adaptor.onDispose += self.__handleViewDispose
        adaptor.onCreated += self.__handleViewLoaded
        self.__loadingItems[adaptor.key] = _LoadingItem(loadParams, adaptor, -1, args, kwargs)
        adaptor.loadView()
        return adaptor
