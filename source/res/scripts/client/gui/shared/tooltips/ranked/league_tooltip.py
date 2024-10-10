# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/league_tooltip.py
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency
from gui.ranked_battles import ranked_formatters
from skeletons.gui.game_control import IRankedBattlesController
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES

class BonusTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(BonusTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(380)

    def _packBlocks(self, *args, **kwargs):
        items = super(BonusTooltipData, self)._packBlocks()
        headerBlocks = [formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.tooltips.battleTypes.ranked.bonusBattle.title())), img=backport.image(R.images.gui.maps.icons.rankedBattles.bonusIcons.c_48x48()), txtPadding=formatters.packPadding(left=20), titleAtMiddle=True, padding=formatters.packPadding(left=30, top=14))]
        items.append(formatters.packBuildUpBlockData(headerBlocks, stretchBg=False, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_NORMAL_VEHICLE_BG_LINKAGE, padding=formatters.packPadding(left=-20, top=-12, bottom=-6)))
        descriptionBlock = [formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.battleTypes.ranked.bonusBattle.description())), padding=formatters.packPadding(top=-6))]
        items.append(formatters.packBuildUpBlockData(descriptionBlock))
        return items


class LeagueTooltipData(BlocksTooltipData):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(LeagueTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        items = super(LeagueTooltipData, self)._packBlocks()
        if self.__rankedController.hasAnyRewardToTake():
            resShortCut = R.strings.ranked_battles.rankedSeasonCompleted.headerReward
        else:
            resShortCut = R.strings.ranked_battles.rankedSeasonCompleted.header
        items.append(formatters.packTitleDescBlock(title=text_styles.highTitle(backport.text(resShortCut.text())), desc=text_styles.main(backport.text(resShortCut.description()))))
        return items


class EfficiencyTooltipData(BlocksTooltipData):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(EfficiencyTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        items = super(EfficiencyTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(text_styles.highTitle(backport.text(R.strings.tooltips.ranked.widget.efficiency.title()))))
        efficiencyBlocks = []
        statsComposer = self.__rankedController.getStatsComposer()
        currEff, currUpdateTime = statsComposer.currentSeasonEfficiency
        efficiencyBlocks.append(self.__getEfficiencyBlock(currEff, currUpdateTime, R.strings.tooltips.ranked.widget.efficiency.currentUpdate()))
        prevEff, prevUpdateTime = statsComposer.cachedSeasonEfficiency
        efficiencyBlocks.append(self.__getEfficiencyBlock(prevEff, prevUpdateTime, R.strings.tooltips.ranked.widget.efficiency.previousUpdate()))
        items.append(formatters.packBuildUpBlockData(efficiencyBlocks, linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, padding=formatters.packPadding(left=60, top=-8, bottom=-8)))
        items.append(formatters.packTextBlockData(text_styles.main(backport.text(R.strings.tooltips.ranked.widget.efficiency.description()))))
        return items

    def __getEfficiencyBlock(self, efficiency, updateTime, resID):
        text = text_styles.main(backport.text(resID)).format(value=text_styles.stats(ranked_formatters.getFloatPercentStrStat(efficiency)), date=text_styles.standard(backport.getShortDateFormat(updateTime)), time=text_styles.standard(backport.getShortTimeFormat(updateTime)))
        return formatters.packTextBlockData(text)


class PositionTooltipData(BlocksTooltipData):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, context):
        super(PositionTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(330)

    def _packBlocks(self, *args, **kwargs):
        items = super(PositionTooltipData, self)._packBlocks()
        title = text_styles.highTitle(backport.text(R.strings.tooltips.ranked.widget.position.title()))
        updateTime = self.__rankedController.getWebSeasonProvider().lastUpdateTime
        updateTime = updateTime or self.__rankedController.getClientSeasonInfoUpdateTime()
        items.append(formatters.packTitleDescBlock(title=title, desc=text_styles.main(backport.text(R.strings.tooltips.ranked.widget.position.description()).format(date=text_styles.neutral(ranked_formatters.getTimeLongStr(updateTime))))))
        posComment = R.strings.tooltips.ranked.widget.position
        items.append(formatters.packTextBlockData(text_styles.standard(backport.text(posComment.updateLabel() if updateTime is not None else posComment.unavailableLabel()))))
        return items
