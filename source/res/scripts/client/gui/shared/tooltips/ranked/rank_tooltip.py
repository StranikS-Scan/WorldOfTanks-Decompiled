# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/rank_tooltip.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.constants import ZERO_RANK_ID
from gui.ranked_battles.ranked_formatters import getRankedAwardsFormatter
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
        items.append(formatters.packBuildUpBlockData([formatters.packRankBlockData(rank=self.item, padding=formatters.packPadding(top=10, bottom=15))]))
        if self.item.isQualification():
            quest = self.__getQualificationQuest()
        else:
            quest = self.item.getQuest()
        if quest is not None:
            items.append(formatters.packBuildUpBlockData(self.__packAwardsBlock(quest), 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, topPaddingText))
        bottomBlocks = self.__packStatusBlock()
        items.append(formatters.packBuildUpBlockData(bottomBlocks))
        return items

    def __getQualificationQuest(self):
        divisionID = self.item.getDivision().getID()
        stats = self.rankedController.getStatsComposer()
        currentBattlesCount = stats.divisionsStats.get(divisionID, {}).get('battles', 0)
        totalBattlesCount = self.rankedController.getTotalQualificationBattles()
        quests = self.rankedController.getQualificationQuests()
        quests[totalBattlesCount] = self.rankedController.getRank(ZERO_RANK_ID + 1).getQuest()
        battles = quests.keys()
        fitBattles = [ x for x in battles if x > currentBattlesCount ]
        return quests[min(fitBattles) if fitBattles else max(battles)] if battles else None

    def __packTitle(self):
        divisionUserName = self.item.getDivisionUserName()
        if self.item.isQualification():
            text = text_styles.highTitle(divisionUserName)
        else:
            divisionName = text_styles.main(divisionUserName)
            name = text_styles.highTitle(backport.text(R.strings.tooltips.battleTypes.ranked.rank.name(), rank=self.item.getUserName()))
            text = text_styles.concatStylesToMultiLine(name, divisionName)
        return formatters.packTextBlockData(text)

    def __packComment(self):
        comment = self.__getDivisionComment() or self.__getShieldComment() or self.__getUnburnableComment()
        return formatters.packTextBlockData(comment) if comment is not None else None

    def __getDivisionComment(self):
        comment = None
        item = self.item
        division = item.getDivision()
        if not division.isCompleted() and item.isLastInDivision():
            if not item.isFinal():
                nextDivisionIdx = division.getID() + 1
                divisions = self.rankedController.getDivisions()
                if nextDivisionIdx < len(divisions):
                    nextDivision = self.rankedController.getDivisions()[nextDivisionIdx]
                    comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isLastInDivision(), division=text_styles.stats(nextDivision.getUserName())))
            else:
                comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isLastInDivision.league()))
        elif item.isFirstInDivision() and division.getUserID() != RANKEDBATTLES_ALIASES.DIVISIONS_CLASSIFICATION:
            comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isFirstInDivision()))
        return comment

    def __getShieldComment(self):
        comment = None
        shieldMaxHp = 0
        hp = 0
        if self.__shieldStatus is not None:
            _, hp, shieldMaxHp, _, _ = self.__shieldStatus
        if shieldMaxHp > 0:
            if hp > 0:
                comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.haveShield(), hp=text_styles.stats(shieldMaxHp)))
            elif self.item.isCurrent():
                comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.shieldBreaked()))
            else:
                comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.shieldBreakedRankLost()))
        elif shieldMaxHp == 0 and hp > 0:
            comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.haveDisposableShield(), hp=text_styles.stats(hp)))
        return comment

    def __getUnburnableComment(self):
        comment = None
        if self.item.isVisualUnburnable():
            comment = text_styles.standard(backport.text(R.strings.tooltips.battleTypes.ranked.rank.isUnburnable()))
        return comment

    def __packStepsBlock(self):
        stepsNumber = self.item.getStepsCountToAchieve()
        stepsNumberStr = text_styles.gold(stepsNumber)
        if self.item.isFirstInDivision():
            locKey = R.strings.tooltips.battleTypes.ranked.rank.conditions.first()
        else:
            locKey = R.strings.tooltips.battleTypes.ranked.rank.conditions()
        return text_styles.main(backport.text(locKey, stepsNumber=stepsNumberStr))

    def __packStatusBlock(self):
        result = []
        if self.item.isQualification():
            if self.item.isCurrent():
                status = text_styles.warning(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.qualificationNotEarned()))
            else:
                status = text_styles.statInfo(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.receivedQualification()))
        elif self.item.isAcquired():
            status = text_styles.statInfo(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.received()))
        elif self.item.isLost():
            status = text_styles.statusAlert(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.lost()))
        else:
            status = text_styles.warning(backport.text(R.strings.tooltips.battleTypes.ranked.rank.status.notearned()))
        result.append(formatters.packAlignedTextBlockData(status, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4)))
        division = self.item.getDivision()
        if not division.isCurrent() and not division.isCompleted():
            result.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.battleTypes.ranked.rank.anotherDivision(), division=division.getUserName()))))
        if self.item.isQualification() and self.item.isCurrent():
            result.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.battleTypes.ranked.rank.conditions.qualification(), count=self.rankedController.getTotalQualificationBattles()))))
        if not self.item.isAcquired():
            result.append(formatters.packTextBlockData(self.__packStepsBlock()))
        return result

    def __packAwardsBlock(self, quest):
        subBlocks = []
        if quest.isCompleted():
            middleTitle = formatters.packImageTextBlockData(title=text_styles.statInfo(backport.text(R.strings.tooltips.battleTypes.ranked.rank.award.received())), img=backport.image(R.images.gui.maps.icons.buttons.checkmark()), imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20)
        else:
            if quest.isQualificationQuest():
                middleTitleText = backport.text(R.strings.tooltips.battleTypes.ranked.rank.qualificationReward(), count=quest.getQualificationBattlesCount())
            else:
                middleTitleText = backport.text(R.strings.tooltips.battleTypes.ranked.rank.reward())
            middleTitle = formatters.packTextBlockData(text_styles.middleTitle(middleTitleText))
        listData = getRankedAwardsFormatter().getFormattedBonuses(quest.getBonuses())
        awardsWidth = len(listData) * _AWARD_STEP
        if awardsWidth < _TOOLTIP_MIN_WIDTH:
            awardsWidth = _TOOLTIP_MIN_WIDTH
        else:
            awardsWidth += _AWARDS_RIGHT_PADDING
        self._setWidth(awardsWidth)
        subBlocks.append(middleTitle)
        subBlocks.append(formatters.packGroupBlockData(listData, padding=formatters.packPadding(top=15)))
        return subBlocks
