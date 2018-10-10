# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/view_lifecycle_watcher.py
import weakref

class IViewLifecycleHandler(object):

    @property
    def monitoredViewKeys(self):
        return tuple(self._monitoredViewKeys)

    def __init__(self, monitoredViewKeys):
        self._monitoredViewKeys = monitoredViewKeys

    def onViewLoading(self, view):
        pass

    def onViewLoaded(self, view):
        pass

    def onViewCreated(self, view):
        pass

    def onViewDestroyed(self, view):
        pass

    def onViewAlreadyLoaded(self, view):
        pass

    def onViewAlreadyCreated(self, view):
        pass


class ViewLifecycleWatcher(object):

    @property
    def monitoredViewKeys(self):
        return tuple(self._monitoredViewKeys)

    def __init__(self):
        super(ViewLifecycleWatcher, self).__init__()
        self._containerManager = None
        self.__loaderManager = None
        self.__handlers = []
        self.__monitoredViewKeys = []
        self.__subscribedViewsKeys = []
        return

    def start(self, containerManager, handlers):
        self._containerManager = weakref.proxy(containerManager)
        self._containerManager.onViewLoading += self.__onViewLoading
        self._containerManager.onViewLoaded += self.__onViewLoaded
        self.__handlers = handlers
        for handler in self.__handlers:
            for viewKey in handler.monitoredViewKeys:
                view = self._containerManager.getViewByKey(viewKey)
                if viewKey not in self.__monitoredViewKeys:
                    if view is not None:
                        self.__subscribeOnViewEvents(view)
                    self.__monitoredViewKeys.append(viewKey)
                if view is not None:
                    if self._containerManager.isViewInCache(viewKey):
                        handler.onViewAlreadyLoaded(view)
                    if self._containerManager.isViewCreated(viewKey):
                        handler.onViewAlreadyCreated(view)

        return

    def stop(self):
        for viewKey in self.__subscribedViewsKeys:
            self.__unsubscribeFromViewEvents(viewKey)

        if self.__loaderManager is not None:
            self.__loaderManager.onViewLoaded -= self.__onViewLoaded
            self.__loaderManager = None
        if self._containerManager is not None:
            self._containerManager.onViewLoaded -= self.__onViewLoaded
            self._containerManager.onViewLoading -= self.__onViewLoading
            self._containerManager = None
        del self.__subscribedViewsKeys[:]
        del self.__monitoredViewKeys[:]
        del self.__handlers[:]
        return

    def __subscribeOnViewEvents(self, view):
        if view.key not in self.__subscribedViewsKeys:
            view.onCreated += self.__onViewCreated
            view.onDisposed += self.__onViewDisposed
            self.__subscribedViewsKeys.append(view.key)

    def __unsubscribeFromViewEvents(self, viewKey):
        if viewKey in self.__subscribedViewsKeys:
            view = self._containerManager.getViewByKey(viewKey)
            if view:
                view.onCreated -= self.__onViewCreated
                view.onDisposed -= self.__onViewDisposed

    def __onViewLoading(self, view, *args, **kwargs):
        if view.key in self.__monitoredViewKeys:
            self.__subscribeOnViewEvents(view)
            for handler in self.__handlers:
                if view.key in handler.monitoredViewKeys:
                    handler.onViewLoading(view)

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.key in self.__monitoredViewKeys:
            for handler in self.__handlers:
                if view.key in handler.monitoredViewKeys:
                    handler.onViewLoaded(view)

    def __onViewCreated(self, view):
        if view.key in self.__monitoredViewKeys:
            for handler in self.__handlers:
                if view.key in handler.monitoredViewKeys:
                    handler.onViewCreated(view)

    def __onViewDisposed(self, view):
        if view.key in self.__monitoredViewKeys:
            for handler in self.__handlers:
                if view.key in handler.monitoredViewKeys:
                    handler.onViewDestroyed(view)

            self.__unsubscribeFromViewEvents(view.key)
            self.__subscribedViewsKeys.remove(view.key)
