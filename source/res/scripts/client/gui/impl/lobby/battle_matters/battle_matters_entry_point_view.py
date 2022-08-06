# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_entry_point_view.py
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_entry_point_view_model import BattleMattersEntryPointViewModel, State
from gui.impl.gen import R
from gui.impl.lobby.battle_matters.tooltips.battle_matters_entry_tooltip_view import BattleMattersEntryTooltipView
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showBattleMatters
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewEvent, View
    from typing import Sequence, Tuple, Callable, Optional
    from Event import Event

class BattleMattersEntryPointView(ViewImpl):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_matters.BattleMattersEntryPointView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = BattleMattersEntryPointViewModel()
        super(BattleMattersEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersEntryPointView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BattleMattersEntryTooltipView() if contentID == R.views.lobby.battle_matters.tooltips.BattleMattersEntryTooltipView() else super(BattleMattersEntryPointView, self).createToolTipContent(event, contentID)

    def _onLoading(self):
        super(BattleMattersEntryPointView, self)._onLoading()
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick), (self.__battleMattersController.onStateChanged, self.__update), (self.__eventsCache.onSyncCompleted, self.__update))

    def __update(self, *_):
        with self.viewModel.transaction() as tx:
            tx.setIsCompleted(self.__battleMattersController.isFinished())
            currentQuest = self.__battleMattersController.getCurrentQuest()
            state = State.NORMAL
            if self.__battleMattersController.isPaused():
                state = State.ERROR
            elif self.__battleMattersController.hasDelayedRewards():
                state = State.HASTOKEN
            tx.setState(state)
            if currentQuest is not None:
                currentProgress, maxProgress = self.__battleMattersController.getQuestProgress(currentQuest)
                tx.setQuestNumber(currentQuest.getOrder())
                tx.setCurrentProgress(currentProgress)
                tx.setMaxProgress(maxProgress)
        return

    @staticmethod
    def __onClick():
        showBattleMatters()
