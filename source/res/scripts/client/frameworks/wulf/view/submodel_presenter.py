# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/submodel_presenter.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared import g_eventBus
if typing.TYPE_CHECKING:
    from Event import Event
    from frameworks.wulf import View, ViewEvent, Window

class SubModelPresenter(object):
    __slots__ = ('__viewModel', '__isLoaded', '__parentView')

    def __init__(self, viewModel, parentView):
        self.__parentView = parentView
        self.__viewModel = viewModel
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
        self.__subscribe()
        self.__isLoaded = True

    def finalize(self):
        self.__isLoaded = False
        self.__unsubscribe()

    def clear(self):
        self.__viewModel = None
        return

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

    def _getEvents(self):
        pass

    def _getListeners(self):
        return tuple()

    def _getCallbacks(self):
        return tuple()

    def __subscribe(self):
        g_clientUpdateManager.addCallbacks(dict(self._getCallbacks()))
        for eventBusArgs in self._getListeners():
            g_eventBus.addListener(*eventBusArgs)

        for event, handler in self._getEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler

        for eventBusArgs in reversed(self._getListeners()):
            g_eventBus.removeListener(*eventBusArgs[:3])

        g_clientUpdateManager.removeObjectCallbacks(self)
