# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_year_reward_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS as _RBC
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter, rankedYearAwardsSortFunction
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 412
_AWARD_STEP = 63
_AWARDS_RIGHT_PADDING = 25

class RankedYearReward(BlocksTooltipData):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedYearReward, self).__init__(context, TOOLTIP_TYPE.RANKED_YEAR_REWARD)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        self.__points = None
        return

    def _packBlocks(self, boxType, status, *args, **kwargs):
        items = super(RankedYearReward, self)._packBlocks()
        self.__points, _ = self.__rankedController.getYearAwardsPointsMap()[boxType]
        items.append(self.__packTitleBlock(boxType))
        items.append(self.__packPointsBlock())
        bonuses = self.__rankedController.getYearRewards(self.__points)
        listData = getRankedAwardsFormatter().getFormattedBonuses(bonuses, compareMethod=rankedYearAwardsSortFunction)
        if listData:
            items.append(self.__packAwardBlock(listData))
        expectedSeasons = self.__rankedController.getExpectedSeasons()
        items.append(self.__packDescriptionBlock(expectedSeasons))
        items.append(self.__packStatusBlock(status))
        return items

    def __packAwardBlock(self, formattedBonuses):
        items = formatters.packGroupBlockData(formattedBonuses, padding=formatters.packPadding(top=15))
        awardsWidth = len(formattedBonuses) * _AWARD_STEP + _AWARDS_RIGHT_PADDING
        if awardsWidth > _TOOLTIP_MIN_WIDTH:
            self._setWidth(awardsWidth)
        title = formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.reward.title())))
        return formatters.packBuildUpBlockData([title, items], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE)

    def __packTitleBlock(self, boxType):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.dyn(boxType).title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.subTitle())))

    def __packPointsBlock(self):
        valueBlock = formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.needPoints())), value=text_styles.stats(str(self.__points) if self.__points else ''), icon=ICON_TEXT_FRAMES.RANKED_POINTS, padding=formatters.packPadding(left=76, top=-5, bottom=-6), valueWidth=20, iconYOffset=2, gap=5)
        return formatters.packBuildUpBlockData([valueBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT)

    def __packDescriptionBlock(self, expectedSeasons):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.description.title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.description.note.num(expectedSeasons)())), txtPadding=formatters.packPadding(left=0), padding=formatters.packPadding(top=-7, bottom=3), txtGap=4)

    def __packStatusBlock(self, status):
        statusBlock = []
        statusStr = backport.text(R.strings.ranked_battles.yearRewards.tooltip.status.dyn(status).title())
        if status in (_RBC.YEAR_REWARD_STATUS_PASSED, _RBC.YEAR_REWARD_STATUS_PASSED_FINAL):
            statusStr = text_styles.warning(statusStr)
        elif status in (_RBC.YEAR_REWARD_STATUS_CURRENT, _RBC.YEAR_REWARD_STATUS_CURRENT_FINAL):
            statusStr = text_styles.statInfo(statusStr)
        else:
            statusStr = text_styles.critical(statusStr)
        statusBlock.append(formatters.packAlignedTextBlockData(statusStr, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4)))
        statusBlock.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.status.dyn(status).description())), padding=formatters.packPadding(top=2, bottom=-2)))
        return formatters.packBuildUpBlockData(statusBlock)
