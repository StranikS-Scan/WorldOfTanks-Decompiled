# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/ranked/ranked_calendar_day_tooltip.py
from datetime import datetime
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from helpers import dependency, time_utils
from skeletons.gui.game_control import IRankedBattlesController
from gui.Scaleform.daapi.view.lobby.formatters.tooltips import packCalendarBlock
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
_TOOLTIP_MIN_WIDTH = 200

class RankedCalendarDayTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx):
        super(RankedCalendarDayTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_CALENDAR_DAY)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self, selectedTime):
        items = super(RankedCalendarDayTooltip, self)._packBlocks()
        if self._isSeasonEnded(selectedTime):
            return items
        blocks = [self._packHeaderBlock()] + self._packCalendarBlock(selectedTime)
        items.append(formatters.packBuildUpBlockData(blocks, 13))
        return items

    def _isSeasonEnded(self, selectedTime):
        if selectedTime is None:
            selectedTime = time_utils.getCurrentLocalServerTimestamp()
        seasonEnd = None
        if self.rankedController.getCurrentSeason():
            seasonEnd = self.rankedController.getCurrentSeason().getEndDate()
            seasonEnd = datetime.fromtimestamp(seasonEnd).date()
        return datetime.fromtimestamp(selectedTime).date() > seasonEnd

    def _packCalendarBlock(self, selectedTime):
        return packCalendarBlock(self.rankedController, selectedTime, SELECTOR_BATTLE_TYPES.RANKED)

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.highTitle(backport.text(R.strings.ranked_battles.calendarDay.title())), img=backport.image(R.images.gui.maps.icons.buttons.calendar()), imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))

    def __packServerTimeBlock(self, serverStr, timeStr):
        return formatters.packTextParameterBlockData(value=serverStr, name=timeStr, valueWidth=55, padding=formatters.packPadding(left=10))
