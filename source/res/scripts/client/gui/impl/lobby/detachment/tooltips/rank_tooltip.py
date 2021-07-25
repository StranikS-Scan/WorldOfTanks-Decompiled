# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/tooltips/rank_tooltip.py
import typing
from frameworks.wulf import View, ViewSettings
from gui.impl.backport import textRes
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.rank_tooltip_model import RankTooltipModel
from uilogging.detachment.loggers import DynamicGroupTooltipLogger
if typing.TYPE_CHECKING:
    from crew2.commander.ranks import RankRecord

class RankTooltip(View):
    __slots__ = ('__rankRecord',)
    uiLogger = DynamicGroupTooltipLogger()

    def __init__(self, rankRecord):
        settings = ViewSettings(R.views.lobby.detachment.tooltips.RankTooltip())
        settings.model = RankTooltipModel()
        super(RankTooltip, self).__init__(settings)
        self.__rankRecord = rankRecord

    def _onLoading(self, *args, **kwargs):
        vm = self.getViewModel()
        rankIcon = self.__rankRecord.icon.split('.')[0].replace('-', '_')
        vm.setIcon(R.images.gui.maps.icons.detachment.ranks.c_80x80.dyn(rankIcon)())
        vm.setRank(textRes(self.__rankRecord.name.replace('-', '_'))())

    def _initialize(self, *args, **kwargs):
        super(RankTooltip, self)._initialize()
        self.uiLogger.tooltipOpened()

    def _finalize(self):
        self.uiLogger.tooltipClosed(self.__class__.__name__)
        self.uiLogger.reset()
        super(RankTooltip, self)._finalize()
