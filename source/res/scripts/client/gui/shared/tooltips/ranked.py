# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers.i18n import makeString as _ms
from gui.ranked_battles.ranked_models import VehicleRank
_TOOLTIP_MIN_WIDTH = 364
_AWARD_STEP = 63
_AWARDS_RIGHT_PADDING = 25

class RankedTooltipData(BlocksTooltipData):

    def __init__(self, context):
        super(RankedTooltipData, self).__init__(context, TOOLTIP_TYPE.RANKED_RANK)
        self.item = None
        self._setContentMargin(bottom=14)
        self._setMargins(14, 20)
        self._setWidth(_TOOLTIP_MIN_WIDTH)
        return

    def _packBlocks(self, *args, **kwargs):
        self.item = self.context.buildItem(*args, **kwargs)
        topPaddingText = formatters.packPadding(top=-5)
        items = super(RankedTooltipData, self)._packBlocks()
        items.append(formatters.packTextBlockData(self.__packTitle()))
        items.append(formatters.packBuildUpBlockData([formatters.packRankBlockData(rank=self.item, isMaster=self.__isForVehicleRank(), rankCount=self.item.getSerialID() if self.__isForCurrentVehicleRank() else '', padding=formatters.packPadding(top=10, bottom=15)), formatters.packTextBlockData(self.__packStepsBlock(), padding=formatters.packPadding(top=5))]))
        quest = self.item.getQuest()
        if quest is not None:
            items.append(formatters.packBuildUpBlockData(self._packAwardsBlock(quest), 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, topPaddingText))
        items.append(self.__buildStatusBlock())
        return items

    def __isForVehicleRank(self):
        return isinstance(self.item, VehicleRank)

    def __isForCurrentVehicleRank(self):
        return self.__isForVehicleRank() and self.item.isAcquired()

    def __packTitle(self):
        if self.__isForVehicleRank():
            name = self.item.getUserName()
        else:
            name = _ms(TOOLTIPS.BATTLETYPES_RANKED_RANK_NAME, rank=self.item.getUserName())
        if self.item.canBeLost():
            comment = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON, vSpace=-3), text_styles.neutral(TOOLTIPS.BATTLETYPES_RANKED_RANK_CANBELOST))
        else:
            comment = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LOCKICON, width=9, height=13, vSpace=-2), text_styles.main(TOOLTIPS.BATTLETYPES_RANKED_RANK_CANTBELOST))
        return text_styles.concatStylesToMultiLine(text_styles.highTitle(name), comment)

    def __packStepsBlock(self):
        stepsNumber = self.item.getStepsCountToAchieve()
        stepsNumberStr = text_styles.gold(stepsNumber)
        if self.item.getID() == 1:
            locKey = TOOLTIPS.BATTLETYPES_RANKED_RANK_CONDITIONS_FIRST
        else:
            locKey = TOOLTIPS.BATTLETYPES_RANKED_RANK_CONDITIONS
        return text_styles.main(_ms(locKey, stepsNumber=stepsNumberStr))

    def __buildStatusBlock(self):
        if self.__isForCurrentVehicleRank():
            achievedCount = self.item.getSerialID()
            vehicleName = self.item.getVehicle().userName
            achievedStr = text_styles.middleTitle(achievedCount)
            descr = text_styles.main(_ms(TOOLTIPS.BATTLETYPES_RANKED_VEHRANK_ACHIEVEDCOUNT, vehName=vehicleName))
            descr = descr + achievedStr
            return formatters.packCounterTextBlockData(achievedCount, descr, padding=formatters.packPadding(left=3))
        if self.item.isAcquired():
            status = text_styles.statInfo(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_RECEIVED)
        elif self.item.isLost():
            status = text_styles.statusAlert(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_LOST)
        else:
            status = text_styles.warning(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_NOTEARNED)
        return formatters.packAlignedTextBlockData(status, BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER, padding=formatters.packPadding(top=-4))

    def _packAwardsBlock(self, quest):
        subBlocks = []
        if quest.isCompleted():
            subBlocks.append(formatters.packAlignedTextBlockData(text_styles.middleTitle(TOOLTIPS.BATTLETYPES_RANKED_RANK_AWARD_RECEIVED), BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        else:
            listData = self.item.getAwardsVOs()
            awardsWidth = len(listData) * _AWARD_STEP
            if awardsWidth > _TOOLTIP_MIN_WIDTH:
                self._setWidth(awardsWidth + _AWARDS_RIGHT_PADDING)
            subBlocks.append(formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.BATTLETYPES_RANKED_RANK_REWARD)))
            subBlocks.append(formatters.packGroupBlockData(listData, padding=formatters.packPadding(bottom=5)))
        return subBlocks
