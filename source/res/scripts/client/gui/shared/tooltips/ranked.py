# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked.py
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.ranked_battles.constants import RANK_TYPES
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import TOOLTIP_TYPE, formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IRankedBattlesController
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
        self.__shieldStatus = self.rankedController.getShieldStatus(self.item)
        topPaddingText = formatters.packPadding(top=-5)
        items = super(RankedTooltipData, self)._packBlocks()
        isVehicleRank = self.__isForVehicleRank()
        if isVehicleRank:
            items.append(self.__packVehTitle())
        else:
            items.append(self.__packTitle())
            items.append(formatters.packBuildUpBlockData([formatters.packRankBlockData(rank=self.item, shieldStatus=self.__shieldStatus, padding=formatters.packPadding(top=10, bottom=15))]))
        quest = self.item.getQuest()
        if quest is not None:
            items.append(formatters.packBuildUpBlockData(self._packAwardsBlock(quest), 0, BLOCKS_TOOLTIP_TYPES.TOOLTIP_BUILDUP_BLOCK_WHITE_BG_LINKAGE, topPaddingText))
        bottomBlocks = [self.__buildStatusBlock()]
        if not isVehicleRank:
            bottomBlocks.append(formatters.packTextBlockData(self.__packStepsBlock()))
        items.append(formatters.packBuildUpBlockData(bottomBlocks))
        return items

    def __isForVehicleRank(self):
        return self.item.getType() == RANK_TYPES.VEHICLE

    def __packTitle(self):
        name = text_styles.highTitle(_ms(TOOLTIPS.BATTLETYPES_RANKED_RANK_NAME, rank=self.item.getUserName()))
        shieldMaxHp = 0
        if self.__shieldStatus is not None:
            _, _, shieldMaxHp, _, _ = self.__shieldStatus
        if shieldMaxHp > 0:
            comment = text_styles.standard(_ms(TOOLTIPS.BATTLETYPES_RANKED_HAVESHIELD, hp=text_styles.stats(shieldMaxHp)))
        elif self.item.canBeLost():
            comment = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON, vSpace=-3), text_styles.neutral(TOOLTIPS.BATTLETYPES_RANKED_RANK_CANBELOST))
        else:
            comment = text_styles.concatStylesWithSpace(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LOCKICON, width=9, height=13, vSpace=-2), text_styles.main(TOOLTIPS.BATTLETYPES_RANKED_RANK_CANTBELOST))
        return formatters.packTextBlockData(text_styles.concatStylesToMultiLine(name, comment))

    def __packVehTitle(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(self.item.getUserName()), desc=self.__packVehStepsBlock(), img=RES_ICONS.MAPS_ICONS_RANKEDBATTLES_ICON_FINAL_CUP_100X100, imgPadding=formatters.packPadding(left=-18, top=-12), txtGap=-4, txtOffset=70, padding=formatters.packPadding(bottom=-30))

    def __packStepsBlock(self):
        stepsNumber = self.item.getStepsCountToAchieve()
        stepsNumberStr = text_styles.gold(stepsNumber)
        if self.item.getID() == 1:
            locKey = TOOLTIPS.BATTLETYPES_RANKED_RANK_CONDITIONS_FIRST
        else:
            locKey = TOOLTIPS.BATTLETYPES_RANKED_RANK_CONDITIONS
        return text_styles.main(_ms(locKey, stepsNumber=stepsNumberStr))

    def __packVehStepsBlock(self):
        stepsNumber = self.item.getStepsCountToAchieve()
        stepsNumberStr = text_styles.gold(stepsNumber)
        return text_styles.main(_ms(TOOLTIPS.BATTLETYPES_RANKED_VEHRANK_CONDITIONS, stepsNumber=stepsNumberStr))

    def __buildStatusBlock(self):
        if self.__isForVehicleRank():
            maxRank = self.rankedController.getMaxRank(vehicle=self.item.getVehicle())
            achievedCount = '0'
            if maxRank and maxRank.getType() == RANK_TYPES.VEHICLE:
                achievedCount = maxRank.getSerialID()
            vehicleName = self.item.getVehicle().userName
            achievedStr = text_styles.middleTitle(achievedCount)
            descr = text_styles.main(_ms(TOOLTIPS.BATTLETYPES_RANKED_VEHRANK_ACHIEVEDCOUNT, vehName=vehicleName))
            descr = descr + achievedStr
            return formatters.packCounterTextBlockData(achievedCount, descr, padding=formatters.packPadding(left=3, bottom=-5))
        if self.item.isAcquired():
            status = text_styles.statInfo(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_RECEIVED)
        elif self.item.isLost():
            status = text_styles.statusAlert(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_LOST)
        else:
            status = text_styles.warning(TOOLTIPS.BATTLETYPES_RANKED_RANK_STATUS_NOTEARNED)
        return formatters.packAlignedTextBlockData(status, BLOCKS_TOOLTIP_TYPES.ALIGN_LEFT, padding=formatters.packPadding(top=-4))

    def _packAwardsBlock(self, quest):
        subBlocks = []
        if quest.isCompleted():
            middleTitle = formatters.packImageTextBlockData(title=text_styles.statInfo(TOOLTIPS.BATTLETYPES_RANKED_RANK_AWARD_RECEIVED), img=RES_ICONS.MAPS_ICONS_BUTTONS_CHECKMARK, imgPadding=formatters.packPadding(left=2, top=3), txtOffset=20)
        else:
            middleTitle = formatters.packTextBlockData(text_styles.middleTitle(TOOLTIPS.BATTLETYPES_RANKED_RANK_REWARD))
        listData = self.item.getAwardsVOs()
        awardsWidth = len(listData) * _AWARD_STEP
        if awardsWidth < _TOOLTIP_MIN_WIDTH:
            awardsWidth = _TOOLTIP_MIN_WIDTH
        else:
            awardsWidth += _AWARDS_RIGHT_PADDING
        self._setWidth(awardsWidth)
        subBlocks.append(middleTitle)
        subBlocks.append(formatters.packGroupBlockData(listData, padding=formatters.packPadding(top=15)))
        return subBlocks
