# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/tooltips/sixth_rank_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.tooltips.sixth_rank_tooltip_model import SixthRankTooltipModel
from gui.impl.lobby.comp7.meta_view.meta_view_helper import getRankDivisions
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class SixthRankTooltip(ViewImpl):
    __slots__ = ()
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID=R.views.lobby.comp7.tooltips.SixthRankTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = SixthRankTooltipModel()
        super(SixthRankTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SixthRankTooltip, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SixthRankTooltip, self)._initialize(*args, **kwargs)
        ranksConfig = self.__lobbyCtx.getServerSettings().comp7PrestigeRanksConfig
        divisions = getRankDivisions(6, ranksConfig)
        self.viewModel.setFrom(divisions[0].range.begin)
