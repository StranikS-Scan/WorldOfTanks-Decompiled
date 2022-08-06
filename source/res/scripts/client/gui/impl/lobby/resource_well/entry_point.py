# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/entry_point.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.entry_point_model import EntryPointModel, EventState
from gui.impl.lobby.resource_well.tooltips.entry_point_tooltip import EntryPointTooltip
from gui.impl.pub import ViewImpl
from gui.resource_well.resource_well_constants import RESOURCE_WELL_PDATA_KEY
from gui.resource_well.resource_well_helpers import isForbiddenAccount, getForbiddenAccountToken
from gui.shared.event_dispatcher import showResourceWellProgressionWindow
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IResourceWellController
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
    __slots__ = ()
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.resource_well.EntryPoint())
        settings.flags = ViewFlags.COMPONENT
        settings.model = EntryPointModel()
        super(EntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPoint, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return EntryPointTooltip() if contentID == R.views.lobby.resource_well.tooltips.EntryPointTooltip() else super(EntryPoint, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(EntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _finalize(self):
        self.__setLastState()
        super(EntryPoint, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.showProgression, self.__showProgressionWindow), (g_playerEvents.onClientUpdated, self.__onClientUpdated), (self.__resourceWell.onSettingsChanged, self.__onSettingsChanged))

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
        if isForbiddenAccount(resourceWell=self.__resourceWell):
            return EventState.FORBIDDEN
        if self.__resourceWell.isPaused():
            return EventState.PAUSED
        return EventState.COMPLETED if self.__resourceWell.isCompleted() else EventState.ACTIVE

    def __getProgress(self):
        maxPoints = self.__resourceWell.getMaxPoints()
        currentPoints = self.__resourceWell.getCurrentPoints() if not self.__resourceWell.isCompleted() else maxPoints
        return _FULL_PROGRESS / (maxPoints or _FULL_PROGRESS) * currentPoints

    def __setLastState(self):
        _g_lastEntryPointState.update(self.__getProgress(), self.__getEventState())

    def __showProgressionWindow(self):
        showResourceWellProgressionWindow()

    def __onClientUpdated(self, diff, _):
        if RESOURCE_WELL_PDATA_KEY in diff:
            self.__updateModel()
        tokens = diff.get('tokens', {})
        if getForbiddenAccountToken(resourceWell=self.__resourceWell) in tokens:
            self.__updateModel()

    def __onSettingsChanged(self):
        self.__updateModel()
