# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/common.py
import weakref
from typing import TYPE_CHECKING
import BigWorld
from frameworks.wulf import View, ViewEvent, Window, WindowLayer
from gui.impl.pub import ViewImpl
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.app_loader import IAppLoader
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional
    from enum import IntEnum
    from gui.Scaleform.framework.managers import ContainerManager

class MainViewImpl(ViewImpl):
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, settings):
        super(MainViewImpl, self).__init__(settings)
        self.__previouslyVisibleLayers = None
        self.__app = None
        return

    def switchToSubView(self, subViewID=None, isBackground=False, *args, **kwargs):
        raise NotImplementedError

    def _initialize(self, *args, **kwargs):
        super(MainViewImpl, self)._initialize(*args, **kwargs)
        self._hideBack()

    def _finalize(self):
        self._showBack()
        super(MainViewImpl, self)._finalize()

    def _getPresentersMap(self):
        raise NotImplementedError

    def _getDefaultSubViewID(self):
        raise NotImplementedError

    def _getVisibleLayers(self):
        return [WindowLayer.TOP_WINDOW,
         WindowLayer.FULLSCREEN_WINDOW,
         WindowLayer.TOOLTIP,
         WindowLayer.OVERLAY]

    def _hideBack(self):
        if self.__app is not None:
            containerManager = self.__app.containerManager
            self.__previouslyVisibleLayers = containerManager.getVisibleLayers()
            containerManager.setVisibleLayers(self._getVisibleLayers())
        BigWorld.worldDrawEnabled(False)
        return

    def _showBack(self):
        BigWorld.worldDrawEnabled(True)
        if self.__app is not None:
            self.__app.containerManager.setVisibleLayers(self.__previouslyVisibleLayers)
        return


class SubViewImpl(EventsHandler):
    __slots__ = ('__viewModel', '__isLoaded', '__parentView')

    def __init__(self, viewModel, parentView):
        self.__viewModel = viewModel
        self.__parentView = parentView
        self.__isLoaded = False

    @property
    def isLoaded(self):
        return self.__isLoaded

    @property
    def parentView(self):
        return self.__parentView

    def getParentWindow(self):
        return self.parentView.getParentWindow()

    def getViewModel(self):
        return self.__viewModel

    def initialize(self, *args, **kwargs):
        self._subscribe()
        self.__isLoaded = True

    def finalize(self):
        self.__isLoaded = False
        self._unsubscribe()

    def clear(self):
        self.__viewModel = None
        return

    def destroy(self):
        self.parentView.destroyWindow()

    def createToolTipContent(self, event, contentID):
        return None

    def createPopOverContent(self, event):
        return None

    def createContextMenuContent(self, event):
        return None

    def createToolTip(self, event):
        return None

    def createPopOver(self, event):
        return None

    def createContextMenu(self, event):
        return None


class PresentersMap(object):

    def __init__(self, mainView):
        self._mainView = weakref.proxy(mainView)
        self.__loaders = self._makeLoadersMap()
        self.__presenters = {}

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def itervalues(self):
        return self.__presenters.itervalues()

    def clear(self):
        for presenter in self.__presenters.itervalues():
            presenter.finalize()
            presenter.clear()

        self.__presenters = {}
        self.__loaders = {}
        self._mainView = None
        return

    def _makeLoadersMap(self):
        return {}

    def __getitem__(self, subViewID):
        if subViewID not in self.__presenters:
            self.__tryToLoadPresenter(subViewID)
        return self.__presenters.get(subViewID)

    def __tryToLoadPresenter(self, subViewID):
        if subViewID in self.__loaders:
            self.__presenters[subViewID] = self.__loaders[subViewID]()
