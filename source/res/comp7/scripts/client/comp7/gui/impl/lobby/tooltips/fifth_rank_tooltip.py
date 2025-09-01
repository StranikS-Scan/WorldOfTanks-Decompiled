# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/fifth_rank_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.fifth_rank_tooltip_model import FifthRankTooltipModel
from comp7.gui.impl.lobby.meta_view.meta_view_helper import getRankDivisions
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class FifthRankTooltip(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.comp7.mono.lobby.tooltips.fifth_rank_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = FifthRankTooltipModel()
        super(FifthRankTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(FifthRankTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(FifthRankTooltip, self)._initialize(*args, **kwargs)
        ranksConfig = self.__comp7Controller.getRanksConfig()
        divisions = getRankDivisions(2, ranksConfig)
        self.viewModel.setFrom(divisions[0].range.begin)
