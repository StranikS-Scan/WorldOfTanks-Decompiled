# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/rank_compatibility_tooltip.py
from typing import Optional
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.rank_compatibility_tooltip_model import RankCompatibilityTooltipModel
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import getSeasonNameEnum
from gui.impl.pub import ViewImpl

class RankCompatibilityTooltip(ViewImpl):
    __slots__ = ('__rankRangeRestriction', '__squadSize')

    def __init__(self, squadSize, rankRngRestr, layoutID=R.views.comp7.lobby.tooltips.RankCompatibilityTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = RankCompatibilityTooltipModel()
        self.__squadSize = squadSize
        self.__rankRangeRestriction = rankRngRestr
        super(RankCompatibilityTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankCompatibilityTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(RankCompatibilityTooltip, self)
        with self.viewModel.transaction() as tx:
            tx.setSeasonName(getSeasonNameEnum())
            tx.setRankRangeRestriction(self.__rankRangeRestriction)
            tx.setSquadSize(self.__squadSize)
