# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/Scaleform/daapi/view/tooltips/common_blocks.py
from advent_calendar.gui.feature.constants import ADVENT_CALENDAR_TOKEN
from advent_calendar.gui.impl.lobby.feature.advent_helper import getAccountTokensAmount, getQuestNeededTokensCount
from advent_calendar.skeletons import IAdventCalendarController
from gui.Scaleform.genConsts.BLOCKS_TOOLTIP_TYPES import BLOCKS_TOOLTIP_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles, icons
from gui.shared.tooltips import formatters
from helpers import dependency

class AdventCalendarProgressionRewardTooltipData(object):
    __adventController = dependency.descriptor(IAdventCalendarController)

    @classmethod
    def packProgressionBlock(cls, questID):
        blocks = []
        lock = backport.image(R.images.advent_calendar.gui.maps.icons.tooltips.lock())
        checkMark = backport.image(R.images.advent_calendar.gui.maps.icons.tooltips.check())
        prevQuest = None
        quest = None
        for q in cls.__adventController.progressionRewardQuestsOrdered:
            if q.getID() == questID:
                quest = q
                break
            prevQuest = q

        if quest.isCompleted():
            blocks.append(formatters.packAlignedTextBlockData(text=text_styles.lightBlue(backport.text(R.strings.advent_calendar.progressionRewards.tooltip.rewardReceived.title(), img=icons.makeImageTag(checkMark, width=24, height=24, vSpace=-6))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        elif cls.__adventController.isInActivePhase():
            if prevQuest is not None and not prevQuest.isCompleted():
                blocks.append(formatters.packAlignedTextBlockData(text=text_styles.cream(backport.text(R.strings.advent_calendar.progressionRewards.tooltip.rewardLocked.title(), img=icons.makeImageTag(lock, width=24, height=24, vSpace=-8))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            else:
                accountTokensAmount = getAccountTokensAmount(ADVENT_CALENDAR_TOKEN)
                requiredTokensAmount = getQuestNeededTokensCount(quest)
                doorsToOpenAmount = requiredTokensAmount - accountTokensAmount
                blocks.append(formatters.packAlignedTextBlockData(text=text_styles.lightGray(text_styles.formatStyledText(backport.ntext(R.strings.advent_calendar.progressionRewards.tooltip.rewardInProgress.title(), doorsToOpenAmount, count=doorsToOpenAmount))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        else:
            blocks.append(formatters.packAlignedTextBlockData(text=text_styles.creamBold(backport.text(R.strings.advent_calendar.progressionRewards.tooltip.rewardExpired.title(), img=icons.makeImageTag(lock, width=24, height=24, vSpace=-8))), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
            blocks.append(formatters.packAlignedTextBlockData(text=text_styles.main(backport.text(R.strings.advent_calendar.progressionRewards.tooltip.rewardExpired.description())), align=BLOCKS_TOOLTIP_TYPES.ALIGN_CENTER))
        return formatters.packBuildUpBlockData(blocks)
