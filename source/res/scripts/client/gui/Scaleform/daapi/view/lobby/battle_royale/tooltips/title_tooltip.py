# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/battle_royale/tooltips/title_tooltip.py
from gui.impl import backport
from gui.impl.gen import R
from gui.battle_royale.royale_formatters import getTitleColumnRewardsFormatter
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController
_TOOLTIP_MIN_WIDTH = 364
_AWARD_STEP = 63
_AWARDS_RIGHT_PADDING = 25
_AWARDS_MAX_COUNT = 5

class TitleTooltip(BlocksTooltipData):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self, context):
        super(TitleTooltip, self).__init__(context, TOOLTIP_TYPE.BATTLE_ROYALE_TITLE)
        self.item = None
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        topPaddingText = formatters.packPadding(top=-5)
        items = super(TitleTooltip, self)._packBlocks()
        headerBlocks = self.__packHeader()
        items.append(formatters.packBuildUpBlockData(headerBlocks))
        titleBlock = formatters.packBuildUpBlockData([formatters.packTitleBlockData(title=self.item, padding=formatters.packPadding(top=10, bottom=15))])
        items.append(titleBlock)
        quest = self.item.getQuest()
        if quest is not None:
            questBlock = formatters.packBuildUpBlockData(self.__packAwardsBlock(quest), 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, topPaddingText)
            items.append(questBlock)
        statusBlocks = self.__buildStatusBlock()
        items.append(formatters.packBuildUpBlockData(statusBlocks))
        return items

    def __packHeader(self):
        subBlocks = []
        header = text_styles.highTitle(backport.text(R.strings.battle_royale.tooltips.title.name(), titleID=str(self.item.getID())))
        subBlocks.append(formatters.packTextBlockData(header))
        headerComment = self.__packComment()
        if headerComment is not None:
            subBlocks.append(headerComment)
        return subBlocks

    def __packComment(self):
        comment = None
        if self.item.getID() in self.__battleRoyaleController.getUnburnableTitles():
            comment = text_styles.main(backport.text(R.strings.battle_royale.tooltips.title.unburnable(), titleID=str(self.item.getID())))
        return formatters.packTextBlockData(comment) if comment is not None else None

    def __packTitle(self):
        name = text_styles.highTitle(backport.text(R.strings.tooltips.battleTypes.ranked.rank.name(), rank=self.item.getUserName()))
        division = self.item.getDivision()
        divisionName = text_styles.main(division.getUserName())
        return formatters.packTextBlockData(text_styles.concatStylesToMultiLine(name, divisionName))

    def __packAwardsBlock(self, quest):
        subBlocks = []
        if quest.isCompleted():
            awardsHeader = formatters.packImageTextBlockData(title=text_styles.statInfo(backport.text(R.strings.battle_royale.tooltips.title.reward.received())), img=backport.image(R.images.gui.maps.icons.buttons.checkmark()), imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20)
        else:
            awardsHeader = formatters.packTextBlockData(text_styles.middleTitle(backport.text(R.strings.battle_royale.tooltips.title.reward())))
        subBlocks.append(awardsHeader)
        awardsList = getTitleColumnRewardsFormatter(_AWARDS_MAX_COUNT).getFormattedBonuses(quest.getBonuses())
        awardsWidth = len(awardsList) * _AWARD_STEP
        if awardsWidth < _TOOLTIP_MIN_WIDTH:
            awardsWidth = _TOOLTIP_MIN_WIDTH
        else:
            awardsWidth += _AWARDS_RIGHT_PADDING
        self._setWidth(awardsWidth)
        subBlocks.append(formatters.packGroupBlockData(awardsList, padding=formatters.packPadding(top=15)))
        return subBlocks

    def __buildStatusBlock(self):
        result = []
        if self.item.isAcquired():
            status = text_styles.statInfo(backport.text(R.strings.battle_royale.tooltips.title.status.received()))
        elif self.item.isLost():
            status = text_styles.statusAttention(backport.text(R.strings.battle_royale.tooltips.title.status.lost()))
        else:
            status = text_styles.warning(backport.text(R.strings.battle_royale.tooltips.title.status.notearned()))
        result.append(formatters.packAlignedTextBlockData(status, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4)))
        if not self.item.isAcquired():
            result.append(formatters.packTextBlockData(self.__packStepsBlock()))
        return result

    def __packStepsBlock(self):
        stepsNumber = len(self.item.getProgress().getSteps())
        stepsNumberStr = text_styles.neutral(stepsNumber)
        if self.item.getID() == self.__battleRoyaleController.getMinPossibleTitle():
            locKey = R.strings.battle_royale.tooltips.title.conditions.first()
        else:
            locKey = R.strings.battle_royale.tooltips.title.conditions()
        return text_styles.main(backport.text(locKey, stepsNumber=stepsNumberStr))
