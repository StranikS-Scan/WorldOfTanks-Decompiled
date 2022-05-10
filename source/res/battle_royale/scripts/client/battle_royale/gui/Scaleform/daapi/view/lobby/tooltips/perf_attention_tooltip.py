# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/tooltips/perf_attention_tooltip.py
from battle_royale.gui.constants import BattleRoyalePerfProblems
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.shared.formatters import text_styles, icons

class PerfAttentionSimpleTooltip(BlocksTooltipData):

    def __init__(self, context=None):
        super(PerfAttentionSimpleTooltip, self).__init__(context, None)
        self._setWidth(370)
        self._setContentMargin(top=20, left=20, bottom=20, right=25)
        return

    def _packBlocks(self, perfType, *args, **kwargs):
        items = super(PerfAttentionSimpleTooltip, self)._packBlocks(*args, **kwargs)
        message = backport.text(R.strings.tooltips.battle_royale.hangar.perf.dyn(perfType).header())
        problemIcon = None
        if perfType == BattleRoyalePerfProblems.HIGH_RISK:
            problemIcon = icons.notAvailableRed()
            formattedMessage = text_styles.critical(message)
        elif perfType == BattleRoyalePerfProblems.MEDIUM_RISK:
            problemIcon = icons.alert()
            formattedMessage = text_styles.alert(message)
        else:
            formattedMessage = ''
        title = text_styles.concatStylesWithSpace(problemIcon, formattedMessage)
        description = text_styles.main(backport.text(R.strings.tooltips.battle_royale.hangar.perf.dyn(perfType).description()))
        items.append(formatters.packTitleDescBlock(title=title, desc=description))
        return items


class PerfAttentionAdvancedTooltip(BlocksTooltipData):

    def __init__(self, context=None):
        super(PerfAttentionAdvancedTooltip, self).__init__(context, None)
        self._setWidth(370)
        self._setContentMargin(top=20, left=20, bottom=25, right=25)
        return

    def _packBlocks(self, *args, **kwargs):
        items = super(PerfAttentionAdvancedTooltip, self)._packBlocks(*args, **kwargs)
        header = formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(R.strings.tooltips.battle_royale.hangar.mainBtn.perf.header())), desc=text_styles.main(backport.text(R.strings.tooltips.battle_royale.hangar.mainBtn.perf.eventDescription())))
        items.append(formatters.packBuildUpBlockData(blocks=[header], padding=formatters.packPadding(bottom=-10)))
        items.append(formatters.packTextBlockData(text_styles.concatStylesWithSpace(icons.info(), text_styles.main(backport.text(R.strings.tooltips.battle_royale.hangar.mainBtn.perf.problemDescription())))))
        return items
