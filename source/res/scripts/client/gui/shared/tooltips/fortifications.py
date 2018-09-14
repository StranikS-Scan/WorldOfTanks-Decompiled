# Embedded file name: scripts/client/gui/shared/tooltips/fortifications.py
from gui.shared.formatters import icons, text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers import i18n

def _packTimeLimitsBlock(block, limits):
    textOffset = 30
    for limit in limits:
        text = i18n.makeString(TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_TIMELIMITFORMAT, startTime=limit.startTime, endTime=limit.endTime)
        block.append(formatters.packImageTextBlockData(title=text_styles.error(text), txtOffset=textOffset))


class FortPopoverDefResTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(FortPopoverDefResTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(380)
        self._descr = TOOLTIPS.FORTIFICATION_POPOVER_DEFRESPROGRESS_BODY

    def _packBlocks(self, compensationValue):
        title = TOOLTIPS.FORTIFICATION_POPOVER_DEFRESPROGRESS_HEADER
        items = super(FortPopoverDefResTooltipData, self)._packBlocks()
        items.append(formatters.packTitleDescBlock(text_styles.highTitle(title), desc=text_styles.main(self._descr)))
        if compensationValue is not None:
            blocksGap = 12
            compensationHeader = text_styles.main(TOOLTIPS.FORTIFICATION_POPOVER_DEFRESPROGRESS_COMPENSATION_HEADER) + text_styles.alert('+' + compensationValue) + icons.nut()
            compensationBody = text_styles.standard(TOOLTIPS.FORTIFICATION_POPOVER_DEFRESPROGRESS_COMPENSATION_BODY)
            items.append(formatters.packBuildUpBlockData([formatters.packTextBlockData(text_styles.concatStylesToMultiLine(compensationHeader, compensationBody))], blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        return items


class FortListViewTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(FortListViewTooltipData, self).__init__(context, TOOLTIP_TYPE.FORTIFICATIONS)
        self._setContentMargin(top=15, left=19, bottom=21, right=22)
        self._setMargins(afterBlock=14)
        self._setWidth(380)
        self._descr = None
        return

    def _packBlocks(self, isCurfewEnabled, timeLimits, serverName = None):
        title = TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_HEADER_CURFEW if isCurfewEnabled else TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_HEADER_INFO
        items = super(FortListViewTooltipData, self)._packBlocks()
        items.append(formatters.packTitleDescBlock(text_styles.highTitle(title), desc=text_styles.main(self._descr) if self._descr else None))
        blocksGap = 2
        mainBlock = self._packMainBlock(serverName, timeLimits)
        limits = timeLimits
        timeBlock = []
        _packTimeLimitsBlock(timeBlock, limits)
        if len(timeBlock) > 0:
            mainBlock.append(formatters.packBuildUpBlockData(timeBlock, 0))
        items.append(formatters.packBuildUpBlockData(mainBlock, blocksGap, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE))
        items.append(formatters.packBuildUpBlockData([formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_FOOTER))], blocksGap))
        return items

    def _packMainBlock(self, serverName, timeLimits):
        pass


class SortiesTimeLimitPacker(FortListViewTooltipData):

    def __init__(self, context):
        super(SortiesTimeLimitPacker, self).__init__(context)

    def _packMainBlock(self, serverName, timeLimits):
        if serverName or timeLimits:
            key = TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_TIMEDESCR
        else:
            key = TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_NONE
        return [formatters.packImageTextBlockData(title=text_styles.main(key))]


class SortiesServerLimitPacker(FortListViewTooltipData):

    def __init__(self, context):
        super(SortiesServerLimitPacker, self).__init__(context)

    def _packMainBlock(self, serverName, timeLimits):
        blocksGap = 20
        blocksList = [formatters.packImageTextBlockData(title=text_styles.main(i18n.makeString(TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_SERVERLIMIT, server=text_styles.error(serverName))))]
        if timeLimits:
            blocksList.append(formatters.packImageTextBlockData(title=text_styles.main(TOOLTIPS.FORTIFICATION_SORTIE_LISTROOM_REGULATION_SERVERLIMITTIMEDESCR)))
        mainBlock = [formatters.packBuildUpBlockData(blocksList, blocksGap)]
        return mainBlock
