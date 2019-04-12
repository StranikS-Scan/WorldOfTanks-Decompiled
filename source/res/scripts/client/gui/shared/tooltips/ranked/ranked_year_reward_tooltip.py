# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_year_reward_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import YearAwardsNames, YEAR_AWARDS_POINTS_MAP
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
YEAR_AWARDS_MAP = {YearAwardsNames.SMALL: ('crystals', 'credits', 'consumables', 'equipments'),
 YearAwardsNames.MEDIUM: ('crystals', 'credits', 'consumables', 'equipments'),
 YearAwardsNames.BIG: ('crystals', 'credits', 'consumables', 'equipments', 'vehicle'),
 YearAwardsNames.LARGE: ('crystals', 'credits', 'consumables', 'equipments', 'vehicle')}

class RankedYearReward(BlocksTooltipData):

    def __init__(self, context):
        super(RankedYearReward, self).__init__(context, TOOLTIP_TYPE.RANKED_YEAR_REWARD)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(412)

    def _packBlocks(self, boxType, status, *args, **kwargs):
        items = super(RankedYearReward, self)._packBlocks()
        items.append(formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.dyn(boxType).title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.subTitle()))))
        minPoints, _ = YEAR_AWARDS_POINTS_MAP[boxType]
        valueBlock = formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.needPoints())), value=text_styles.stats(str(minPoints)), icon=ICON_TEXT_FRAMES.RANKED_POINTS, padding=formatters.packPadding(left=76, top=-5, bottom=-6), valueWidth=20, iconYOffset=2, gap=5)
        items.append(formatters.packBuildUpBlockData([valueBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT))
        awards = YEAR_AWARDS_MAP.get(boxType)
        rewardRKey = R.strings.ranked_battles.yearRewards.tooltip.reward
        names = {rewardID:text_styles.neutral(backport.text(rewardRKey.dyn(rewardID)())) for rewardID in awards}
        items.append(formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.description.title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.dyn(boxType).description.note(), **names)), txtPadding=formatters.packPadding(left=0), padding=formatters.packPadding(top=-7, bottom=3), txtGap=4))
        statusBlock = []
        statusStr = backport.text(R.strings.ranked_battles.yearRewards.tooltip.status.dyn(status).title())
        if status == RANKEDBATTLES_CONSTS.YEAR_REWARD_STATUS_PASSED:
            statusStr = text_styles.warning(statusStr)
        elif status == RANKEDBATTLES_CONSTS.YEAR_REWARD_STATUS_CURRENT:
            statusStr = text_styles.statInfo(statusStr)
        else:
            statusStr = text_styles.critical(statusStr)
        statusBlock.append(formatters.packAlignedTextBlockData(statusStr, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4)))
        statusBlock.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.status.dyn(status).description())), padding=formatters.packPadding(top=2, bottom=-2)))
        items.append(formatters.packBuildUpBlockData(statusBlock))
        return items
