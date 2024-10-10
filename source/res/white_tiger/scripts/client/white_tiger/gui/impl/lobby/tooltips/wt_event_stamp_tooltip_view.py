# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/wt_event_stamp_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from white_tiger.gui.impl.gen.view_models.views.lobby.tooltips.wt_event_stamp_tooltip_view_model import WtEventStampTooltipViewModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController

class WtEventStampTooltipView(ViewImpl):
    __slots__ = ()
    __eventController = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        settings = ViewSettings(R.views.white_tiger.lobby.tooltips.StampTooltipView())
        settings.model = WtEventStampTooltipViewModel()
        super(WtEventStampTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventStampTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WtEventStampTooltipView, self)._onLoading()
        self.viewModel.setStampsPerProgressionStage(self.__eventController.getStampsCountPerLevel())
