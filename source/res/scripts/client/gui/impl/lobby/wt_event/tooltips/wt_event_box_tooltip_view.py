# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/tooltips/wt_event_box_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.tooltips.wt_event_box_tooltip_view_model import WtEventBoxTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.wt_event.wt_event_helpers import fillLootBoxRewards
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class WtEventBoxTooltipView(ViewImpl):
    __slots__ = ('__boxType',)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, boxType):
        settings = ViewSettings(R.views.lobby.wt_event.tooltips.WtEventBoxTooltipView())
        settings.model = WtEventBoxTooltipViewModel()
        self.__boxType = boxType
        super(WtEventBoxTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventBoxTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventBoxTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillLootBoxRewards(model, self.__boxType, True)
