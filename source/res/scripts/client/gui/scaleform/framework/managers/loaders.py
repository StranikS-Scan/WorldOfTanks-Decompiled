# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/loaders.py
import Event
import constants
from debug_utils import LOG_ERROR, LOG_WARNING
from gui.Scaleform.framework import g_entitiesFactories, ViewSettings, ScopeTemplates
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.entities.abstract.LoaderManagerMeta import LoaderManagerMeta
from gui.app_loader.decorators import sf_lobby
from ids_generators import SequenceIDGenerator
NO_IMPL_ALIAS = 'noImpl'
NO_IMPL_URL = 'development/noImpl.swf'

class _LoadingItem(object):
    """
    Represents an item (View) loaded by LoaderManager.
    """
    __slots__ = ('name', 'pyEntity', 'factoryIdx', 'args', 'kwargs', 'isCancelled')

    def __init__(self, name, pyEntity, factoryIdx, args, kwargs):
        super(_LoadingItem, self).__init__()
        self.name = name
        self.pyEntity = pyEntity
        self.factoryIdx = factoryIdx
        self.args = args
        self.kwargs = kwargs
        self.isCancelled = False


class LoaderManager(LoaderManagerMeta):
    """
    Class of loader manager. This manager works with View entities only.
    """

    def __init__(self, app):
        super(LoaderManager, self).__init__()
        self.__eManager = Event.EventManager()
        self.onViewLoadInit = Event.Event(self.__eManager)
        self.onViewLoaded = Event.Event(self.__eManager)
        self.onViewLoadError = Event.Event(self.__eManager)
        self.onViewLoadCanceled = Event.Event(self.__eManager)
        self.__app = app
        self.__nameToLoadingItem = {}

    def loadView(self, alias, name, *args, **kwargs):
        """
        Loads a view by the given alias and name with the given arguments (args and kwargs).
        
        :param alias: value of view alias.
        :param name: name of view.
        :param args: args.
        :param kwargs: kwargs.
        :return: instance of view in python.
        """
        return self.__doLoadView(alias, name, *args, **kwargs)

    def cancelLoadingByName(self, name):
        """
        Cancels loading of view with the given name.
        
        :param name: name of view.
        """
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            item.isCancelled = True
            self.onViewLoadCanceled(name, item)

    def isViewLoading(self, viewAlias):
        """
        Returns True if a view with the given alias is being loaded, otherwise returns False.
        :param viewAlias: value of view alias.
        :return: boolean.
        """
        result = False
        for item in self.__nameToLoadingItem.itervalues():
            pyEntity = item.pyEntity
            if pyEntity and pyEntity.settings.alias == viewAlias:
                result = True
                break

        return result

    def viewLoaded(self, name, gfxEntity):
        """
        Callback to be invoked by AS when a view is loaded.
        
        :param name: name of view.
        :param gfxEntity: GFXEntity (AS entity) instance.
        """
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            if item.isCancelled:
                self.onViewLoadCanceled(name, item)
            else:
                pyEntity = g_entitiesFactories.initialize(item.pyEntity, gfxEntity, item.factoryIdx, extra={'name': item.name})
                if pyEntity is not None:
                    self.onViewLoaded(pyEntity)
                else:
                    LOG_ERROR('An error occurred before DAAPI initialization.')
        else:
            LOG_WARNING('View loading for name has no associated data', name)
        return

    def viewLoadError(self, alias, name, errorTxt):
        """
        Callback to be invoked by AS when an error occurs during view loading.
        
        :param alias: value of view alias.
        :param name: name of view.
        :param errorTxt: error text represented by string.
        """
        msg = 'Error occurred during view {0} loading. Name: {1}, error:{2}'.format(alias, name, errorTxt)
        LOG_ERROR(msg)
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            if item.isCancelled:
                self.onViewLoadCanceled(name, item)
            else:
                self.onViewLoadError(name, msg, item)
                if item is not None:
                    settings = item.pyEntity.settings
                    if constants.IS_DEVELOPMENT and settings.url != NO_IMPL_URL:
                        g_entitiesFactories.addSettings(ViewSettings(NO_IMPL_ALIAS, View, NO_IMPL_URL, settings.type, None, ScopeTemplates.DEFAULT_SCOPE, False))
                        LOG_WARNING('Try to load noImpl swf...')
                        self.__doLoadView(NO_IMPL_ALIAS, item.name)
        else:
            LOG_WARNING('View loading for name has no associated data', name)
        return

    def viewInitializationError(self, alias, name):
        """
        Callback to be invoked by AS when initialization error occurs during view loading.
        
        :param alias: value of view alias.
        :param name: name of view.
        """
        msg = "View '{0}' does not implement net.wg.infrastructure.interfaces.IView".format(alias)
        LOG_ERROR(msg)
        item = None
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem.pop(name)
            pyEntity = item.pyEntity
            pyEntity.destroy()
        self.onViewLoadError(name, msg, item)
        return

    def _dispose(self):
        self.__app = None
        self.__nameToLoadingItem.clear()
        self.__eManager.clear()
        super(LoaderManager, self)._dispose()
        return

    def __doLoadView(self, alias, name, *args, **kwargs):
        viewTutorialID = self.__app.tutorialManager.getViewTutorialID(name)
        if name in self.__nameToLoadingItem:
            item = self.__nameToLoadingItem[name]
            item.isCancelled = False
            pyEntity = item.pyEntity
        else:
            pyEntity = None
        if pyEntity is not None:
            viewDict = {'config': pyEntity.settings.getDAAPIObject(),
             'alias': alias,
             'name': name,
             'viewTutorialId': viewTutorialID}
            self.as_loadViewS(viewDict)
        else:
            pyEntity, factoryIdx = g_entitiesFactories.factory(alias, *args, **kwargs)
            if pyEntity is not None:
                pyEntity.setUniqueName(name)
                pyEntity.setEnvironment(self.__app)
                self.__nameToLoadingItem[name] = _LoadingItem(name, pyEntity, factoryIdx, args, kwargs)
                self.onViewLoadInit(pyEntity)
                viewDict = {'config': pyEntity.settings.getDAAPIObject(),
                 'alias': alias,
                 'name': name,
                 'viewTutorialId': viewTutorialID}
                self.as_loadViewS(viewDict)
            else:
                LOG_WARNING('PyEntity for alias %s is None' % alias)
        return pyEntity


class SequenceIDLoader(EventSystemEntity):
    __counter = SequenceIDGenerator()

    def __init__(self):
        super(SequenceIDLoader, self).__init__()

    @sf_lobby
    def app(self):
        return None

    def _loadView(self, alias, *args, **kwargs):
        self.app.loadView(alias, 'deprecated_rw{0}'.format(self.__counter.next()), *args, **kwargs)
