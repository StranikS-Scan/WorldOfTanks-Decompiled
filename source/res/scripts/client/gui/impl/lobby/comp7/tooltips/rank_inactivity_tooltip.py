# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/rank_inactivity_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.rank_inactivity_tooltip_model import RankInactivityTooltipModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class RankInactivityTooltip(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.lobby.comp7.tooltips.RankInactivityTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = RankInactivityTooltipModel()
        super(RankInactivityTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankInactivityTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(RankInactivityTooltip, self)._initialize(*args, **kwargs)
        self.viewModel.setRankInactivityCount(self.__comp7Controller.activityPoints)
