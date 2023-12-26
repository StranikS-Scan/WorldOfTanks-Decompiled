# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/history_presenter.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from gui.impl.gen import R
from gui.impl.new_year.history_manager.history_manager import HistoryManager
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict, Optional

class HistoryPresenter(SubModelPresenter, EventsHandler):
    __slots__ = ('__isPreLoaded',)
    _itemsCache = dependency.descriptor(IItemsCache)
    _historyManager = HistoryManager.getInstance()
    _navigationAlias = None

    def __init__(self, viewModel, parentView):
        super(HistoryPresenter, self).__init__(viewModel, parentView)
        self.__isPreLoaded = False

    def preLoad(self, *args, **kwargs):
        self.__isPreLoaded = True

    def initialize(self, *args, **kwargs):
        if not self.__isPreLoaded:
            self.preLoad()
        super(HistoryPresenter, self).initialize(*args, **kwargs)
        if kwargs.get('clearHistoryNavigation', False):
            self._historyManager.clear()

    def finalize(self):
        self.__isPreLoaded = False
        super(HistoryPresenter, self).finalize()

    @classmethod
    def clearHistory(cls):
        cls._historyManager.clear()

    def addToHistoryForced(self):
        raise NotImplementedError

    def _goBack(self):
        if self._historyManager.hasPrevViews():
            self._historyManager.goBack()

    def _getInfoForHistory(self):
        return None

    def _getBackPageName(self):
        backPageName = self._historyManager.getBackButtonText()
        return backPageName if backPageName else R.invalid()

    def _updateBackButton(self):
        raise NotImplementedError

    def getNavigationAlias(self):
        return self._navigationAlias or self.__class__.__name__

    def _createBackButtonText(self):
        raise NotImplementedError

    def __preserveHistory(self):
        raise NotImplementedError
