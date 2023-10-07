# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/crew_book.py
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData

class CrewBookTooltipDataBlock(BlocksTooltipData):

    def __init__(self, context):
        super(CrewBookTooltipDataBlock, self).__init__(context, TOOLTIP_TYPE.CREW_BOOK)
        self._setContentMargin(bottom=8)
        self._setWidth(320)

    def _packBlocks(self, *args, **kwargs):
        items = super(CrewBookTooltipDataBlock, self)._packBlocks()
        item = self.context.buildItem(*args, **kwargs)
        block = []
        block.append(formatters.packTextBlockData(text=text_styles.highTitle(item.userName)))
        block.append(formatters.packTextBlockData(text=text_styles.main(item.fullDescription)))
        items.append(formatters.packBuildUpBlockData(block))
        return items
