# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/view/submodel_presenter.py
import typing
from helpers.events_handler import EventsHandler
if typing.TYPE_CHECKING:
    from typing import Optional
    from frameworks.wulf import View, ViewEvent, Window

class SubModelPresenter(EventsHandler):
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
        self._subscribe()
        self.__isLoaded = True

    def finalize(self):
        self.__isLoaded = False
        self._unsubscribe()

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
