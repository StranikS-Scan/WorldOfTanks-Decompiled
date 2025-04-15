# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/event.py
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData

class EventSelectorWarningTooltip(BlocksTooltipData):

    def __init__(self, context):
        super(EventSelectorWarningTooltip, self).__init__(context, None)
        self._setWidth(width=400)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(EventSelectorWarningTooltip, self)._packBlocks(*args, **kwargs)
        items.append(self._getHeaderBlock())
        items.append(self._getInfoBlock())
        return items

    def _getHeaderBlock(self):
        return formatters.packBuildUpBlockData([formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.tooltips.battleTypes.event.header()))), formatters.packTextBlockData(text=text_styles.main(backport.text(R.strings.tooltips.battleTypes.event.body())))])

    def _getInfoBlock(self):
        return formatters.packTextBlockData(text=text_styles.concatStylesWithSpace(icons.info(), text_styles.stats(backport.text(R.strings.tooltips.battleTypes.event.description()))))
