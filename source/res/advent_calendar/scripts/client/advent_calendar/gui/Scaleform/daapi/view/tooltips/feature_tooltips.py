# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/Scaleform/daapi/view/tooltips/feature_tooltips.py
from advent_calendar.gui.Scaleform.daapi.view.tooltips.common_blocks import AdventCalendarProgressionRewardTooltipData
from gui.Scaleform.daapi.view.lobby.customization.tooltips import ElementAwardTooltip
from gui.shared.tooltips.tankman import NotRecruitedTooltipData

class AdventCalendarNotRecruitedTooltipData(NotRecruitedTooltipData):

    def _packBlocks(self, *args, **kwargs):
        invID, questID = args
        items = super(AdventCalendarNotRecruitedTooltipData, self)._packBlocks(invID)
        items.append(AdventCalendarProgressionRewardTooltipData.packProgressionBlock(questID))
        return items


class AdventCalendarCustomizationTooltipData(ElementAwardTooltip):

    def _packBlocks(self, questID, *args, **kwargs):
        items = super(AdventCalendarCustomizationTooltipData, self)._packBlocks(*args)
        items.append(AdventCalendarProgressionRewardTooltipData.packProgressionBlock(questID))
        return items
