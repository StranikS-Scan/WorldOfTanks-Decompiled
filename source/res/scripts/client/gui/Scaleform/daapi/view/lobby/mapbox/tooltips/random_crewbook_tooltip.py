# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/mapbox/tooltips/random_crewbook_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from shared_utils import first

class RandomCrewBookTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(RandomCrewBookTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.RANDOM_CREWBOOK)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, item, **kwargs):
        items = super(RandomCrewBookTooltipDataBlock, self)._packBlocks()
        crewbook, _ = first(item.options.getItems())
        block = [formatters.packTextBlockData(text=text_styles.highTitle(backport.text(R.strings.tooltips.randomCrewbook.dyn(item.name).header()))), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.randomCrewbook.body(), exp=crewbook.getXP())))]
        items.append(formatters.packBuildUpBlockData(block))
        return items
