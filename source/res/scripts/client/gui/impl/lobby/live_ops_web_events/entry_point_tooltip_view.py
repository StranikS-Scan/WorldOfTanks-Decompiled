# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/live_ops_web_events/entry_point_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_tooltip_view_model import EntryPointTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import ILiveOpsWebEventsController
from gui.impl.gen.view_models.views.lobby.live_ops_web_events.entry_point_base import State

class EntryPointTooltipView(ViewImpl):
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)
    __slots__ = ('__state',)

    def __init__(self, state):
        settings = ViewSettings(R.views.lobby.live_ops_web_events.EntryPointTooltip())
        settings.model = EntryPointTooltipViewModel()
        self.__state = state
        super(EntryPointTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EntryPointTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            tx.setState(State(self.__state))
            tx.setEventStartDate(self.__liveOpsWebEventsController.eventStart)
            tx.setEventEndDate(self.__liveOpsWebEventsController.eventEnd)
        super(EntryPointTooltipView, self)._onLoading(*args, **kwargs)
