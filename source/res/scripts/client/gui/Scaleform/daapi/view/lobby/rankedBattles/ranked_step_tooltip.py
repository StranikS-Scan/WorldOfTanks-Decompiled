# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_step_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers.i18n import makeString as _ms
_TOOLTIP_MIN_WIDTH = 280

class RankedStepTooltip(BlocksTooltipData):

    def __init__(self, ctx):
        super(RankedStepTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_STEP)
        self._setContentMargin(top=20, left=20, bottom=20, right=20)
        self._setMargins(afterBlock=14)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, *args):
        items = super(RankedStepTooltip, self)._packBlocks()
        items.append(self._packHeaderBlock())
        items.append(self._packCondutionsBlock())
        items.append(formatters.packTextBlockData('{}\n{}'.format(text_styles.highTitle(RANKED_BATTLES.TOOLTIP_STEP_NOTCHARGED_HEADER), text_styles.standard(RANKED_BATTLES.TOOLTIP_STEP_NOTCHARGED_DESCRIPTION))))
        items.append(formatters.packTextBlockData('{}\n{}'.format(text_styles.highTitle(RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_HEADER), text_styles.standard(RANKED_BATTLES.TOOLTIP_STEP_DECOMMISSION_DESCRIPTION))))
        return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(RANKED_BATTLES.TOOLTIP_STEP_HEADER), desc=text_styles.standard(RANKED_BATTLES.TOOLTIP_STEP_DESCRIPTION), img=RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_ICON_RANKS_STAGE_98X120, imgPadding=formatters.packPadding(left=-18, top=-28), txtGap=-4, txtOffset=70, padding=formatters.packPadding(bottom=-60))

    def _packCondutionsBlock(self, *args, **kwargs):
        block = []
        block.append(formatters.packTextBlockData(text_styles.middleTitle(RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS_HEADER), padding=formatters.packPadding(bottom=7)))
        block.append(formatters.packImageTextBlockData(desc=text_styles.main(_ms(RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS, battlesNum=12, team=text_styles.statInfo(RANKED_BATTLES.TOOLTIP_STEP_WINNERS))), img=RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_TOP12_53X49, txtPadding=formatters.packPadding(left=17)))
        block.append(formatters.packTextBlockData(text_styles.hightlight(RANKED_BATTLES.TOOLTIP_STEP_OR), padding=formatters.packPadding(left=70, bottom=10)))
        block.append(formatters.packImageTextBlockData(desc=text_styles.main(_ms(RANKED_BATTLES.TOOLTIP_STEP_CONDITIONS, battlesNum=3, team=text_styles.critical(RANKED_BATTLES.TOOLTIP_STEP_LOSERS))), img=RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKEDBATTESVIEW_ICON_TOP3_53X49, txtPadding=formatters.packPadding(left=17)))
        return formatters.packBuildUpBlockData(block, 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)
