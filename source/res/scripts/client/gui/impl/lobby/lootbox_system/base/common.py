# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lootbox_system/base/common.py
import weakref
from typing import TYPE_CHECKING
from frameworks.wulf import View, ViewEvent, Window
from gui.impl.pub.view_component import ViewComponent
from helpers.events_handler import EventsHandler
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional
    from enum import IntEnum

class MainViewImpl(ViewComponent):

    def switchToSubView(self, subViewID=None, isBackground=False, *args, **kwargs):
        raise NotImplementedError

    def _getPresentersMap(self):
        raise NotImplementedError

    def _getDefaultSubViewID(self):
        raise NotImplementedError


class SubViewImpl(EventsHandler):

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
