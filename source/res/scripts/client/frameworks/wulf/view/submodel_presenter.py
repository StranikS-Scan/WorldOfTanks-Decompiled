# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/submodel_presenter.py
import typing
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

    def __subscribe(self):
        for event, handler in self._getEvents():
            event += handler

    def __unsubscribe(self):
        for event, handler in self._getEvents():
            event -= handler
