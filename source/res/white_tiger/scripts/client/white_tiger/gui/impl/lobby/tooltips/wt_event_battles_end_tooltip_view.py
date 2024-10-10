# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_battles_end_tooltip_view.py
from frameworks.wulf import ViewSettings
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_battles_end_tooltip_view_model import WtEventBattlesEndTooltipViewModel
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController

class WtEventBattlesEndTooltipView(ViewImpl):
    __slots__ = ()
    __eventController = dependency.descriptor(IWhiteTigerController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.white_tiger.lobby.tooltips.BattlesEndTooltipView(), model=WtEventBattlesEndTooltipViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WtEventBattlesEndTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventBattlesEndTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setEndDate(self.__getEndDate())

    def __getEndDate(self):
        season = self.__eventController.getCurrentSeason() or self.__eventController.getNextSeason() or self.__eventController.getPreviousSeason()
        return -1 if not season else season.getEndDate()
