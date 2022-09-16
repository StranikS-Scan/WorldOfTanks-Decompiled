# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/seventh_rank_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.seventh_rank_tooltip_model import SeventhRankTooltipModel
from gui.impl.lobby.comp7 import comp7_model_helpers
from gui.impl.pub import ViewImpl

class SeventhRankTooltip(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID=R.views.lobby.comp7.tooltips.SeventhRankTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = SeventhRankTooltipModel()
        super(SeventhRankTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SeventhRankTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SeventhRankTooltip, self)._initialize(*args, **kwargs)
        comp7_model_helpers.setElitePercentage(self.viewModel)
