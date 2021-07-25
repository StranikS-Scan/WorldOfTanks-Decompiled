# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_year_reward_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.genConsts.ICON_TEXT_FRAMES import ICON_TEXT_FRAMES
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS as _RBC
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import YEAR_AWARD_SELECTABLE_OPT_DEVICE
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter, rankedYearAwardsSortFunction
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IRankedBattlesController
from gui.server_events.awards_formatters import AWARDS_SIZES
_TOOLTIP_MIN_WIDTH = 442
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
        listData = getRankedAwardsFormatter().getFormattedBonuses(bonuses, size=AWARDS_SIZES.BIG, compareMethod=rankedYearAwardsSortFunction)
        if listData:
            items.append(self.__packAwardBlock(listData))
        selectableDevice = findFirst(lambda b: YEAR_AWARD_SELECTABLE_OPT_DEVICE in getattr(b, 'getTokens', lambda : {})(), bonuses)
        if selectableDevice is not None:
            items.append(self.__packEquipmentChoiceBlock(selectableDevice.getTokens()[YEAR_AWARD_SELECTABLE_OPT_DEVICE].count))
        items.append(self.__packStatusBlock(status))
        return items

    def __packAwardBlock(self, formattedBonuses):
        items = formatters.packGroupBlockData(formattedBonuses, align=BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, rendererWidth=80, padding=formatters.packPadding(top=10))
        awardsWidth = len(formattedBonuses) * _AWARD_STEP + _AWARDS_RIGHT_PADDING
        if awardsWidth > _TOOLTIP_MIN_WIDTH:
            self._setWidth(awardsWidth)
        title = formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.any.reward.title())))
        return formatters.packBuildUpBlockData([title, items])

    def __packTitleBlock(self, boxType):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.dyn(boxType).title())), desc=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.box.subTitle())))

    def __packPointsBlock(self):
        valueBlock = formatters.packTextParameterWithIconBlockData(name=text_styles.main(backport.text(R.strings.ranked_battles.yearRewards.tooltip.needPoints())), value=text_styles.stats(str(self.__points) if self.__points else ''), icon=ICON_TEXT_FRAMES.RANKED_POINTS, padding=formatters.packPadding(left=76, top=-5, bottom=-6), valueWidth=20, nameOffset=15, iconYOffset=2, gap=5)
        return formatters.packBuildUpBlockData([valueBlock], linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT)

    def __packEquipmentChoiceBlock(self, equipmentCount):
        equipmentChoiceDyn = R.strings.ranked_battles.yearRewards.tooltip.equipmentChoice
        header = formatters.packImageTextBlockData(title=text_styles.middleTitle(backport.text(equipmentChoiceDyn.title())), desc=text_styles.main(backport.text(equipmentChoiceDyn.description.num(equipmentCount)())), padding=formatters.packPadding(top=-20))
        descr = formatters.packItemTitleDescBlockData(desc=text_styles.main(backport.text(equipmentChoiceDyn.list())), img=backport.image(R.images.gui.maps.icons.rankedBattles.delux_gift()), imgAtLeft=False, imgPadding=formatters.packPadding(top=20, right=-10), padding=formatters.packPadding(top=5))
        return formatters.packBuildUpBlockData([header, descr])

    def __packStatusBlock(self, status):
        statusBlock = []
        statusDyn = R.strings.ranked_battles.yearRewards.tooltip.status.dyn(status)
        statusStr = backport.text(statusDyn.title())
        if status in (_RBC.YEAR_REWARD_STATUS_PASSED, _RBC.YEAR_REWARD_STATUS_PASSED_FINAL):
            statusStr = text_styles.warning(statusStr)
        elif status in (_RBC.YEAR_REWARD_STATUS_CURRENT, _RBC.YEAR_REWARD_STATUS_CURRENT_FINAL):
            statusStr = text_styles.statInfo(statusStr)
        else:
            statusStr = text_styles.critical(statusStr)
        statusBlock.append(formatters.packAlignedTextBlockData(statusStr, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-4)))
        statusBlock.append(formatters.packAlignedTextBlockData(text_styles.main(backport.text(statusDyn.description())), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=2, bottom=-2)))
        return formatters.packBuildUpBlockData(statusBlock, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER)
