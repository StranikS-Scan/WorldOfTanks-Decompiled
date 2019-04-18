# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/rank_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_formatters import getRanksColumnRewardsFormatter
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
_TOOLTIP_MIN_WIDTH = 364
_AWARD_STEP = 63
_AWARDS_RIGHT_PADDING = 25

class RankedTooltipData(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(RankedTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self.__shieldStatus = None
        self.item = None
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        self.__shieldStatus = self.item.getShieldStatus()
        topPaddingText = formatters.packPadding(top=-5)
        items = super(RankedTooltipData, self)._packBlocks()
        items.append(self.__packTitle())
        comment = self.__packComment()
        if comment is not None:
            items.append(comment)
        items.append(formatters.packBuildUpBlockData([formatters.packRankBlockData(rank=self.item, shieldStatus=self.__shieldStatus, padding=formatters.packPadding(top=10, bottom=15))]))
        quest = self.item.getQuest()
        if quest is not None:
            items.append(formatters.packBuildUpBlockData(self.__packAwardsBlock(quest), 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, topPaddingText))
        bottomBlocks = self.__buildStatusBlock()
        items.append(formatters.packBuildUpBlockData(bottomBlocks))
        return items

    def __packTitle(self):
        name = text_styles.highTitle(backport.text(R.strings.tooltips.battleTypes.ranked.rank.name(), rank=self.item.getUserName()))
        division = self.item.getDivision()
        divisionName = text_styles.main(division.getUserName())
        return formatters.packTextBlockData(text_styles.concatStylesToMultiLine(name, divisionName))

    def __packComment(self):
        shieldMaxHp = 0
        if self.__shieldStatus is not None:
            _, _, shieldMaxHp, _, _ = self.__shieldStatus
        item = self.item
        division = item.getDivision()
        comment = None
        if not division.isCompleted() and item.isLastInDivision():
            if not item.isFinal():
                nextDivisionIdx = division.getID() + 1
                divisions = self.rankedController.getDivisions()
                if nextDivisionIdx < len(divisions):
                    nextDivision = self.rankedController.getDivisions()[nextDivisionIdx]
                    comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isLastInDivision(), division=text_styles.stats(nextDivision.getUserName())))
            else:
                comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isLastInDivision.league()))
        elif shieldMaxHp > 0:
            comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.haveShield(), hp=text_styles.stats(shieldMaxHp)))
        elif item.isFirstInDivision() and division.getUserID() != RANKEDBATTLES_ALIASES.DIVISIONS_CLASSIFICATION:
            comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isFirstInDivision()))
        return formatters.packTextBlockData(comment) if comment is not None else None

    def __packStepsBlock(self):
        stepsNumber = self.item.getStepsCountToAchieve()
        stepsNumberStr = text_styles.gold(stepsNumber)
        if self.item.isFirstInDivision():
            locKey = R.strings.tooltips.battleTypes.ranked.rank.conditions.first()
        else:
            locKey = R.strings.tooltips.battleTypes.ranked.rank.conditions()
        return text_styles.main(backport.text(locKey, stepsNumber=stepsNumberStr))

    def __buildStatusBlock(self):
        result = []
        if self.item.isAcquired():
            status = text_styles.statInfo(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.received()))
        elif self.item.isLost():
            status = text_styles.statusAlert(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.lost()))
        else:
            status = text_styles.warning(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.notearned()))
        result.append(formatters.packAlignedTextBlockData(status, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4)))
        division = self.item.getDivision()
        if not division.isCurrent() and not division.isCompleted():
            result.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.battleTypes.ranked.rank.anotherDivision(), division=division.getUserName()))))
        if not self.item.isAcquired():
            result.append(formatters.packTextBlockData(self.__packStepsBlock()))
        return result

    def __packAwardsBlock(self, quest):
        subBlocks = []
        if quest.isCompleted():
            middleTitle = formatters.packImageTextBlockData(title=text_styles.statInfo(backport.text(R.strings.tooltips.battleTypes.ranked.rank.award.received())), img=backport.image(R.images.gui.maps.icons.buttons.checkmark()), imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20)
        else:
            middleTitle = formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.tooltips.battleTypes.ranked.rank.reward())))
        listData = getRanksColumnRewardsFormatter().getFormattedBonuses(quest.getBonuses())
        awardsWidth = len(listData) * _AWARD_STEP
        if awardsWidth < _TOOLTIP_MIN_WIDTH:
            awardsWidth = _TOOLTIP_MIN_WIDTH
        else:
            awardsWidth += _AWARDS_RIGHT_PADDING
        self._setWidth(awardsWidth)
        subBlocks.append(middleTitle)
        subBlocks.append(formatters.packGroupBlockData(listData, padding=formatters.packPadding(top=15)))
        return subBlocks
