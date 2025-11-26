# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenters/battle_results_sub_presenter.py
import typing
from frameworks.wulf.view.submodel_presenter import SubModelPresenter
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Union, Type, Optional, Any
    from frameworks.wulf import View, ViewEvent, Window, ViewModel, Array
    BattleResultsComponentModelType = typing.TypeVar('BattleResultsComponentModelType', bound=ViewModel)
    TooltipModelType = typing.TypeVar('TooltipModelType', bound=ViewModel)

class UnexpectedViewModelException(SoftException):
    pass


class BattleResultsSubPresenter(SubModelPresenter):
    _battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, viewModel, parentView):
        viewModelType = self.getViewModelType()
        if hasattr(viewModelType, '__origin__'):
            viewModelType = viewModelType.__origin__
        if not isinstance(viewModel, viewModelType):
            raise UnexpectedViewModelException('Expected an instance of {}, got {}'.format(self.getViewModelType(), viewModel.__class__))
        super(BattleResultsSubPresenter, self).__init__(viewModel, parentView)
        self._subPresenters = []

    @classmethod
    def getViewModelType(cls):
        raise NotImplementedError

    def initialize(self, *args, **kwargs):
        for subPresenter in self._subPresenters:
            subPresenter.initialize(*args, **kwargs)

        super(BattleResultsSubPresenter, self).initialize(*args, **kwargs)

    def finalize(self):
        for subPresenter in self._subPresenters:
            subPresenter.finalize()

        self._subPresenters = []
        super(BattleResultsSubPresenter, self).finalize()

    def addSubPresenter(self, subPacker):
        self._subPresenters.append(subPacker)

    def removeSubPacker(self, subPacker):
        self._subPresenters.remove(subPacker)

    def getBattleResults(self):
        statsController = self._battleResults.getStatsCtrl(self.parentView.arenaUniqueID)
        return statsController.getResults()

    def packBattleResults(self, battleResults):
        for subPresenter in self._subPresenters:
            subPresenter.packBattleResults(battleResults)

    def createToolTipContent(self, event, contentID):
        for subPresenter in self._subPresenters:
            content = subPresenter.createToolTipContent(event, contentID)
            if content is not None:
                return content

        return super(BattleResultsSubPresenter, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        for subPresenter in self._subPresenters:
            window = subPresenter.createContextMenu(event)
            if window is not None:
                return window

        return super(BattleResultsSubPresenter, self).createContextMenu(event)
