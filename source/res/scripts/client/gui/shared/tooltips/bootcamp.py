# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/bootcamp.py
from gui.shared.formatters import text_styles
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.tooltips import formatters
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

class StatsTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(StatsTooltipData, self).__init__(context, None)
        self._setWidth(330)
        return

    def _packBlocks(self, label, description, icon):
        items = super(StatsTooltipData, self)._packBlocks()
        items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.highTitle(label)), formatters.packImageBlockData(img=icon, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER), formatters.packTextBlockData(text_styles.main(description))]))
        return items
