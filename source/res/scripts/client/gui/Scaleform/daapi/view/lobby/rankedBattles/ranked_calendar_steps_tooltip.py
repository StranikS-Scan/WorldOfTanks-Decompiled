# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_calendar_steps_tooltip.py
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.formatters import text_styles
from gui.shared.tooltips import TOOLTIP_TYPE
from gui.shared.tooltips import formatters
from gui.shared.tooltips.common import BlocksTooltipData
from gui.ranked_battles.ranked_models import CYCLE_STATUS
from helpers import dependency, i18n
from helpers import time_utils
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
_TOOLTIP_MIN_WIDTH = 200

class RankedCalendarStepsTooltip(BlocksTooltipData):
    rankedController = dependency.descriptor(IRankedBattlesController)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, ctx):
        super(RankedCalendarStepsTooltip, self).__init__(ctx, TOOLTIP_TYPE.RANKED_CALENDAR_DAY)
        self._setContentMargin(top=18, left=20, bottom=18, right=20)
        self._setMargins(afterBlock=13)
        self._setWidth(_TOOLTIP_MIN_WIDTH)

    def _packBlocks(self):
        items = super(RankedCalendarStepsTooltip, self)._packBlocks()
        blocks = [self._packHeaderBlock()]
        key = RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARPOPOVER_CYCLEITEM
        currentSeason = self.rankedController.getCurrentSeason()
        cycles = currentSeason.getAllCycles()
        seasonName = currentSeason.getNumber()
        for cycle in sorted(cycles.values()):
            currentCycle = False
            if cycle.status == CYCLE_STATUS.CURRENT:
                formatter = text_styles.main
                currentCycle = True
            else:
                formatter = text_styles.standard
            startDate = time_utils.getTimeStructInLocal(cycle.startDate)
            endDate = time_utils.getTimeStructInLocal(cycle.endDate)
            item = formatter(i18n.makeString(key, cycleNumber=seasonName, day0='{:02d}'.format(startDate.tm_mday), month0='{:02d}'.format(startDate.tm_mon), day1='{:02d}'.format(endDate.tm_mday), month1='{:02d}'.format(endDate.tm_mon)))
            if currentCycle:
                blocks.append(formatters.packImageTextBlockData(title=item, img=RES_ICONS.MAPS_ICONS_LIBRARY_INPROGRESSICON, imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=5)))
            blocks.append(formatters.packTextBlockData(text=item, padding=formatters.packPadding(left=20)))

        items.append(formatters.packBuildUpBlockData(blocks, 13))
        return items

    def _packHeaderBlock(self):
        return formatters.packImageTextBlockData(title=text_styles.middleTitle(RANKED_BATTLES.CALENDARSTEPSTOOLTIP_TITLE), img=RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR, imgPadding=formatters.packPadding(top=5), txtPadding=formatters.packPadding(left=10))
