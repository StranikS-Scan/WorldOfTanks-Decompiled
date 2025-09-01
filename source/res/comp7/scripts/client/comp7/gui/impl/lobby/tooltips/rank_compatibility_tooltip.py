# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/rank_compatibility_tooltip.py
from typing import Optional
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.rank_compatibility_tooltip_model import RankCompatibilityTooltipModel
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class RankCompatibilityTooltip(ViewImpl):
    __slots__ = ('__rankRangeRestriction', '__squadSize')
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, squadSize, rankRngRestr, layoutID=R.views.comp7.mono.lobby.tooltips.rank_compatibility_tooltip()):
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
            tx.setSeasonName(getSeasonNameEnum(self.__comp7Controller, SeasonName))
            tx.setRankRangeRestriction(self.__rankRangeRestriction)
            tx.setSquadSize(self.__squadSize)
