# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/entry_point.py
from frameworks.wulf import ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from resource_well.gui.feature.resource_well_helpers import getRewardVehiclesInInventory
from resource_well.gui.impl.gen.view_models.views.lobby.entry_point_model import EntryPointModel, EventState
from resource_well.gui.impl.lobby.feature.tooltips.entry_point_tooltip import EntryPointTooltip
from resource_well.gui.shared.event_dispatcher import showResourceWellProgressionWindow
from shared_utils import nextTick, first, findFirst
from skeletons.gui.resource_well import IResourceWellController
_FULL_PROGRESS = 100.0

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

class ResourceWellEntryPointComponent(InjectComponentAdaptor):

    def _onPopulate(self):
        self.__createInject()

    def _makeInjectView(self, *args):
        return EntryPoint()

    @nextTick
    def __createInject(self):
        self._createInjectView()


class EntryPoint(ViewImpl):
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.resource_well.lobby.feature.EntryPoint(), model=EntryPointModel())
        super(EntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPoint, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.resource_well.lobby.feature.tooltips.EntryPointTooltip() else super(EntryPoint, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.viewModel.showProgression, self.__showProgressionWindow), (self.__resourceWell.onSettingsChanged, self.__onSettingsChanged), (self.__resourceWell.onEventUpdated, self.__onEventUpdated))

    def _onLoading(self, *args, **kwargs):
        super(EntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def __updateModel(self, *_):
        with self.viewModel.transaction() as model:
            isFirstShow = _g_lastEntryPointState.isFirstShow
            progress = self.__getProgress()
            state = self.__getEventState()
            model.setProgress(progress)
            model.setEventState(state)
            model.setPrevEventState(state if isFirstShow else _g_lastEntryPointState.state)
            model.setPrevProgress(progress if isFirstShow else _g_lastEntryPointState.progress)
        self.__setLastState()

    def __getEventState(self):
        if self.__resourceWell.isNotStarted():
            return EventState.NOTSTARTED
        if self.__resourceWell.isPaused():
            return EventState.PAUSED
        if self.__resourceWell.isForbiddenAccount():
            return EventState.FORBIDDEN
        if self.__resourceWell.isRewardsOver():
            if self.__resourceWell.getReceivedRewardIDs() or getRewardVehiclesInInventory():
                return EventState.COMPLETED
            return EventState.SOLDOUT
        return EventState.ACTIVE

    def __getProgress(self):
        rewardsConfig = self.__resourceWell.config.rewards
        rewardID = self.__resourceWell.getCurrentRewardID() or findFirst(self.__resourceWell.isRewardAvailable, rewardsConfig)
        if not rewardID:
            rewardID = first(self.__resourceWell.getReceivedRewardIDs()) or first(rewardsConfig)
        maxPoints = self.__resourceWell.config.getRewardConfig(rewardID).points
        currentPoints = self.__resourceWell.getCurrentPoints()
        if self.__resourceWell.isRewardReceived(rewardID):
            currentPoints = maxPoints
        return _FULL_PROGRESS / (maxPoints or _FULL_PROGRESS) * currentPoints

    def __setLastState(self):
        _g_lastEntryPointState.update(self.__getProgress(), self.__getEventState())

    @staticmethod
    def __showProgressionWindow():
        showResourceWellProgressionWindow()

    def __onSettingsChanged(self):
        if self.__resourceWell.isFinished():
            return
        self.__updateModel()

    def __onEventUpdated(self):
        self.__updateModel()
