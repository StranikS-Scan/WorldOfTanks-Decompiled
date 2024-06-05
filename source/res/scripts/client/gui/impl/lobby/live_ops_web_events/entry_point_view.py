# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/live_ops_web_events/entry_point_view.py
import Event
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.LiveOpsWebEventsEntryPointInjectMeta import LiveOpsWebEventsEntryPointInjectMeta
from gui.game_control.live_ops_web_events_controller import EventState
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_base import State
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_view_model import EntryPointViewModel
from gui.impl.lobby.live_ops_web_events.entry_point_tooltip_view import EntryPointTooltipView
from gui.impl.pub import ViewImpl
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import ILiveOpsWebEventsController
EVENT_STATE_TO_UI_STATE_MAPPING = {EventState.PRE_EVENT: State.PRE_EVENT,
 EventState.EVENT_ACTIVE: State.EVENT_ACTIVE,
 EventState.POST_EVENT: State.POST_EVENT}

class LiveOpsWebEventsEntryPointComponent(LiveOpsWebEventsEntryPointInjectMeta):

    def _onPopulate(self):
        self.__createInject()

    def _addInjectContentListeners(self):
        self._injectView.onEntryPointSizeChanged += self.__onViewSizeChanged

    def _removeInjectContentListeners(self):
        self._injectView.onEntryPointSizeChanged -= self.__onViewSizeChanged

    def _makeInjectView(self, *args):
        return LiveOpsWebEventsEntryPointView()

    @nextTick
    def __createInject(self):
        self._createInjectView()

    def __onViewSizeChanged(self, isSmall):
        self.as_setIsSmallS(isSmall)


class LiveOpsWebEventsEntryPointView(ViewImpl):
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.live_ops_web_events.EntryPoint())
        settings.flags = flags
        settings.model = EntryPointViewModel()
        super(LiveOpsWebEventsEntryPointView, self).__init__(settings)
        self.onEntryPointSizeChanged = Event.Event()
        self.__isSmall = True

    @property
    def viewModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.live_ops_web_events.EntryPointTooltip():
            return EntryPointTooltipView(event.getArgument('state'))
        super(LiveOpsWebEventsEntryPointView, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self.__liveOpsWebEventsController.onSettingsChanged, self.__onSettingsChanged), (self.__liveOpsWebEventsController.onEventStateChanged, self.__updateViewModel), (self.viewModel.onClick, self.__onClick))

    def _onLoading(self, *args, **kwargs):
        super(LiveOpsWebEventsEntryPointView, self)._onLoading(*args, **kwargs)
        self.__isSmall = self.__liveOpsWebEventsController.isEntryPointSmall
        self.__updateViewModel(setIsSmall=True)

    def __updateViewModel(self, setIsSmall=False):
        if self.__liveOpsWebEventsController.canShowHangarEntryPoint():
            isFirstEntry = self.__liveOpsWebEventsController.getIsFirstEventEntry()
            state = self.__liveOpsWebEventsController.eventState
            previousState = self.__liveOpsWebEventsController.previousEventState
            with self.viewModel.transaction() as tx:
                tx.setState(EVENT_STATE_TO_UI_STATE_MAPPING[state])
                tx.setIsFirstEntry(isFirstEntry)
                tx.setIsVisited(not self.__liveOpsWebEventsController.getEventTabVisited())
                tx.setIsHighQualityPreset(self.__liveOpsWebEventsController.isHighQualityPreset)
                if previousState:
                    tx.setPreviousState(EVENT_STATE_TO_UI_STATE_MAPPING[previousState])
                if setIsSmall:
                    self.onEntryPointSizeChanged(self.__isSmall)
                    tx.setIsSmall(self.__isSmall)
                if isFirstEntry and state == EventState.EVENT_ACTIVE:
                    self.__liveOpsWebEventsController.markEventEntered()

    def __onSettingsChanged(self):
        isSmall = self.__liveOpsWebEventsController.isEntryPointSmall
        if self.__isSmall != isSmall:
            self.__isSmall = isSmall
            self.__updateViewModel(setIsSmall=True)
        else:
            self.__updateViewModel()

    @staticmethod
    def __onClick():
        from gui.server_events.events_dispatcher import showMissionsLiveOpsWebEvents
        showMissionsLiveOpsWebEvents()
