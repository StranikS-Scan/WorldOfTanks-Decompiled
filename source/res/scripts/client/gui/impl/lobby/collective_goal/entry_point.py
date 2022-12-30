# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collective_goal/entry_point.py
import bisect
import logging
import math
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collective_goal.collective_goal_entry_point_model import CollectiveGoalEntryPointModel, EventState
from gui.impl.lobby.collective_goal.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showMissionsMarathon
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import ICollectiveGoalEntryPointController, IMarathonEventsController
_FULL_PROGRESS = 100.0
_logger = logging.getLogger(__name__)

class _LastEntryPointState(object):

    def __init__(self):
        self.progress = 0.0
        self.state = EventState.ACTIVE
        self.isFirstShow = True

    def update(self, progress=0.0, state=None, isFirstShow=False):
        self.progress = progress
        self.state = state
        self.isFirstShow = isFirstShow


_g_lastEntryPointState = _LastEntryPointState()

class CollectiveGoalEntryPointComponent(InjectComponentAdaptor):

    def _onPopulate(self):
        self.__createInject()

    def _makeInjectView(self, *args):
        return EntryPoint()

    @nextTick
    def __createInject(self):
        self._createInjectView()


class EntryPoint(ViewImpl):
    __slots__ = ()
    __collectiveGoalEntryPointController = dependency.descriptor(ICollectiveGoalEntryPointController)
    __marathonController = dependency.descriptor(IMarathonEventsController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.collective_goal.CollectiveGoalEntryPointView())
        settings.flags = ViewFlags.COMPONENT
        settings.model = CollectiveGoalEntryPointModel()
        super(EntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPoint, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _finalize(self):
        if self.__collectiveGoalEntryPointController.isEnabled():
            self.__setLastState()
        super(EntryPoint, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.showProgression, self.__showEventsTab), (self.__collectiveGoalEntryPointController.onDataUpdated, self.__onDataUpdated), (self.__collectiveGoalEntryPointController.onEventUpdated, self.__onEventUpdated))

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.lobby.collective_goal.tooltips.EntryPointTooltip() else super(EntryPoint, self).createToolTipContent(event, contentID)

    def __updateModel(self, *_):
        with self.viewModel.transaction() as model:
            progress = self.__getProgress()
            state = self.__getEventState()
            stage, _ = self.__collectiveGoalEntryPointController.getCurrentDiscount()
            model.setProgress(progress)
            model.setCurrentGoal(stage)
            model.setEventState(state)
            isFirstShow = _g_lastEntryPointState.isFirstShow
            prevState = state if isFirstShow or state == EventState.FORBIDDEN else _g_lastEntryPointState.state
            model.setPrevEventState(prevState)
            model.setPrevProgress(progress if isFirstShow else _g_lastEntryPointState.progress)
            model.setStartDate(self.__collectiveGoalEntryPointController.getActivePhaseStartTime())
        self.__setLastState()

    def __getEventState(self):
        if self.__collectiveGoalEntryPointController.isForbidden():
            return EventState.FORBIDDEN
        if not self.__collectiveGoalEntryPointController.isStarted():
            return EventState.NOTSTARTED
        return EventState.FINISHED if self.__collectiveGoalEntryPointController.isCompleted() or self.__collectiveGoalEntryPointController.isFinished() else EventState.ACTIVE

    def __getProgress(self):
        currentPoints = self.__collectiveGoalEntryPointController.getCurrentPoints()
        discounts = self.__collectiveGoalEntryPointController.getDiscounts()
        if not discounts:
            return 0
        points = sorted(discounts.keys())
        ind = bisect.bisect_right(points, currentPoints, 0, len(points) - 1)
        left = points[ind - 1] if ind > 0 else 0
        right = points[ind]
        percentage = _FULL_PROGRESS * (min(currentPoints, right) - left) / (right - left)
        return math.ceil(percentage) if percentage < 1 else math.floor(percentage)

    def __setLastState(self):
        state = self.__getEventState()
        if state != EventState.FORBIDDEN:
            _g_lastEntryPointState.update(self.__getProgress(), state)

    def __showEventsTab(self):
        marathonPrefix = self.__collectiveGoalEntryPointController.getMarathonPrefix()
        if self.__marathonController.getMarathon(marathonPrefix) is not None:
            showMissionsMarathon(marathonPrefix)
        else:
            _logger.error("Marathon %s isn't found. Check collective goal config", marathonPrefix)
        return

    def __onDataUpdated(self):
        self.__updateModel()

    def __onEventUpdated(self):
        self.__updateModel()
