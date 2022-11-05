# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/tooltips/epic_battle_widget_tooltip.py
from gui.Scaleform.daapi.view.lobby.epicBattle.after_battle_reward_view_helpers import getProgressionIconVODict
from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import getTimeToEndStr
from gui.Scaleform.daapi.view.lobby.epicBattle.tooltips.common_blocks import packEpicBattleInfoBlock, packEpicBattleSeasonBlock
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.game_control.epic_meta_game_ctrl import EPIC_PERF_GROUP
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicBattleWidgetTooltip(BlocksTooltipData):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, context):
        super(EpicBattleWidgetTooltip, self).__init__(context, None)
        self._setContentMargin(top=0, left=0, bottom=12, right=0)
        self._setWidth(width=320)
        return

    def _packBlocks(self):
        blocks = super(EpicBattleWidgetTooltip, self)._packBlocks()
        season = self.__epicController.getCurrentSeason() or self.__epicController.getNextSeason()
        if season is None:
            return blocks
        else:
            if self.__epicController.isCurrentCycleActive():
                blocks.extend([self.__getCycleStatusTooltipPack(season), self.__packPerformanceWarningBlock()])
            else:
                blocks.append(packEpicBattleInfoBlock())
                seasonBlock = packEpicBattleSeasonBlock()
                if seasonBlock is not None:
                    blocks.append(seasonBlock)
                if season.getNextByTimeCycle(time_utils.getCurrentLocalServerTimestamp()) is not None:
                    blocks.append(self.__packPerformanceWarningBlock())
            numRewards = self.__epicController.getNotChosenRewardCount()
            if numRewards:
                blocks.append(self.__packRewardsToChooseBlock(numRewards, text_styles.counter))
            return blocks

    def __getCycleStatusTooltipPack(self, season):
        items = []
        currentLevel, levelProgress = self.__epicController.getPlayerLevelInfo()
        cycleNumber = self.__epicController.getCurrentOrNextActiveCycleNumber(season)
        items.append(formatters.packTextBlockData(text=text_styles.middleTitle(backport.text(R.strings.epic_battle.tooltips.common.title())), padding=formatters.packPadding(left=20, right=20)))
        currentCycle = season.getCycleInfo()
        tDiff = currentCycle.endDate - time_utils.getCurrentLocalServerTimestamp() if currentCycle is not None else 0
        timeLeft = text_styles.main(getTimeToEndStr(tDiff))
        items.append(formatters.packTextBlockData(text=timeLeft, padding=formatters.packPadding(left=20, right=20)))
        items.append(formatters.packBuildUpBlockData(blocks=[formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_EPIC_BATTLE_META_LEVEL_BLOCK_LINKAGE, data=getProgressionIconVODict(cycleNumber=cycleNumber, playerLevel=currentLevel), padding=formatters.packPadding(left=-20))], layout=BLOCKS_TOOLTIP_TYPES.LAYOUT_HORIZONTAL, align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        items.append(self.__packLevelBlock(currentLevel))
        if currentLevel < self.__epicController.getMaxPlayerLevel():
            famePtsToProgress = self.__epicController.getPointsProgressForLevel(currentLevel)
            items.append(self.__getCurrentMaxProgressBlock(levelProgress, famePtsToProgress))
            items.append(self.__getPlayerProgressToLevelBlock(levelProgress, famePtsToProgress))
        else:
            unlockedStr = backport.text(R.strings.epic_battle.tooltips.widget.reachedMaxLevel())
            items.append(formatters.packTextBlockData(text=text_styles.main(unlockedStr), padding=formatters.packPadding(left=20, right=20, top=-7)))
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(top=20, bottom=10))

    @staticmethod
    def __packLevelBlock(playerLevel):
        items = []
        levelMsgStr = text_styles.stats(backport.text(R.strings.epic_battle.tooltips.widget.level(), level=playerLevel))
        items.append(formatters.packTextBlockData(text=levelMsgStr, padding=formatters.packPadding(left=20, right=20, top=-10)))
        return formatters.packBuildUpBlockData(items)

    @staticmethod
    def __getPlayerProgressToLevelBlock(playerFamePts, famePtsToProgress):
        res = formatters.packBlockDataItem(linkage=BLOCKS_TOOLTIP_TYPES.TOOLTIP_META_LEVEL_PROGRESS_BLOCK_LINKAGE, data={'progressBarData': {'value': playerFamePts,
                             'maxValue': famePtsToProgress}}, padding=formatters.packPadding(left=20), blockWidth=280)
        return res

    @staticmethod
    def __getCurrentMaxProgressBlock(playerFamePts, famePtsToProgress):
        items = []
        currentPoint = text_styles.stats(str(playerFamePts))
        fameTo = text_styles.main(str(famePtsToProgress))
        currentPointMaxPoint = text_styles.concatStylesWithSpace(currentPoint, text_styles.main('/'), fameTo)
        marginTop = 0
        iconSrc = backport.image(R.images.gui.maps.icons.epicBattles.fame_point_tiny())
        text = text_styles.concatStylesWithSpace(text_styles.main(currentPointMaxPoint), icons.makeImageTag(source=iconSrc, width=24, height=24))
        items.append(formatters.packAlignedTextBlockData(text=text, align=BLOCKS_TOOLTIP_TYPES.ALIGN_RIGHT, padding=formatters.packPadding(left=20, right=20, top=-35)))
        return formatters.packBuildUpBlockData(items, padding=formatters.packPadding(top=marginTop, right=20))

    def __packPerformanceWarningBlock(self):
        performanceGroup = self.__epicController.getPerformanceGroup()
        attention = R.strings.epic_battle.selectorTooltip.epicBattle.attention
        if performanceGroup == EPIC_PERF_GROUP.HIGH_RISK:
            icon = icons.markerBlocked()
            titleStyle = text_styles.error
            attention = attention.assuredLowPerformance
        elif performanceGroup == EPIC_PERF_GROUP.MEDIUM_RISK:
            icon = icons.alert()
            titleStyle = text_styles.alert
            attention = attention.possibleLowPerformance
        else:
            icon = icons.attention()
            titleStyle = text_styles.stats
            attention = attention.informativeLowPerformance
        return formatters.packTitleDescBlock(title=text_styles.concatStylesWithSpace(icon, titleStyle(backport.text(attention.title()))), desc=text_styles.main(backport.text(attention.description())), padding=formatters.packPadding(left=20, right=40))

    def __packRewardsToChooseBlock(self, numRewards, style):
        iconSrc = backport.image(R.images.gui.maps.icons.epicBattles.rewards_to_choose())
        icon = icons.makeImageTag(source=iconSrc, width=24, height=24, vSpace=-10)
        items = []
        numRewardsText = text_styles.concatStylesWithSpace(icon, style(backport.text(R.strings.epic_battle.tooltips.chooseRewards.desc(), number=numRewards)))
        items.append(formatters.packTextBlockData(text=numRewardsText, padding=formatters.packPadding(left=20, right=20)))
        return formatters.packBuildUpBlockData(items)
