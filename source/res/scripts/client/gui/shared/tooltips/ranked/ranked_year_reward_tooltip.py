# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_year_reward_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import YearAwardsNames
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController

class RankedYearReward(BlocksTooltipData):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedYearReward, self).__init__(context, TOOLTIP_TYPE.RANKED_YEAR_REWARD)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(412)

    def _packBlocks(self, boxType, status, *args, **kwargs):
        items = super(RankedYearReward, self)._packBlocks()
        items.append(self.__getTitleBlock(boxType))
        minPoints, _ = self.__rankedController.getYearAwardsPointsMap()[boxType]
        items.append(self.__getPointsBlock(minPoints))
        expectedSeasons = self.__rankedController.getExpectedSeasons()
        items.append(self.__getDescriptionBlock(boxType, expectedSeasons))
        items.append(self.__getStatusBlock(status))
        return items

    @staticmethod
    def __getTitleBlock(boxType):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.dyn(boxType).title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.subTitle())))

    @staticmethod
    def __getPointsBlock(minPoints):
        valueBlock = formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.needPoints())), value=text_styles.stats(str(minPoints)), icon=ICON_TEXT_FRAMES.RANKED_POINTS, padding=formatters.packPadding(left=76, top=-5, bottom=-6), valueWidth=20, iconYOffset=2, gap=5)
        return formatters.packBuildUpBlockData([valueBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT)

    @staticmethod
    def __getDescriptionBlock(boxType, expectedSeasons):
        rewardNames = {}
        if boxType in (YearAwardsNames.BIG, YearAwardsNames.LARGE):
            rewardNames.update({'vehicle': text_styles.neutral(backport.text(R.strings.ranked_battles.yearRewards.tooltip.reward.vehicle()))})
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.description.title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.dyn(boxType).description.note.num(expectedSeasons)(), **rewardNames)), txtPadding=formatters.packPadding(left=0), padding=formatters.packPadding(top=-7, bottom=3), txtGap=4)

    @staticmethod
    def __getStatusBlock(status):
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
        return formatters.packBuildUpBlockData(statusBlock)
