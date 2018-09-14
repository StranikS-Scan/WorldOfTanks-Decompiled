# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/RankedBattlesCalendarPopover.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.ranked_battles.ranked_models import CYCLE_STATUS
from helpers import i18n, dependency
from gui.Scaleform.daapi.view.meta.RankedBattlesCalendarPopoverMeta import RankedBattlesCalendarPopoverMeta
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.shared.formatters import text_styles
from helpers import time_utils
from skeletons.gui.game_control import IRankedBattlesController
ARROW_TOP = 0

class RankedBattlesCalendarPopover(RankedBattlesCalendarPopoverMeta):
    rankedController = dependency.descriptor(IRankedBattlesController)
    arrowDirection = ARROW_TOP

    def __init__(self, ctx=None):
        super(RankedBattlesCalendarPopover, self).__init__()
        self.__seasonInfo = self.rankedController.getCurrentSeason()
        self.__currentCycle = self.__seasonInfo.getCycleOrdinalNumber()
        self.__selectedDate = time_utils.getCurrentLocalServerTimestamp()
        data = ctx.get('data', None)
        if data is not None:
            self.arrowDirection = data.arrowDirection
        return

    def _populate(self):
        super(RankedBattlesCalendarPopover, self)._populate()
        self.as_setDataS({'attentionText': self.__getAttentionText(),
         'cycles': self.__getCyclesListString(),
         'currentCycle': self.__currentCycle - 1,
         'rawDate': self.__selectedDate,
         'arrowDirection': self.arrowDirection})
        calendar = self.__getCalendar()
        if calendar is not None:
            calendar.as_setMinAvailableDateS(self.__seasonInfo.getStartDate())
            calendar.as_setMaxAvailableDateS(self.__seasonInfo.getEndDate())
            calendar.as_openMonthS(self.__selectedDate)
            calendar.as_selectDateS(self.__selectedDate)
            calendar.as_setHighlightedDaysS([self.__seasonInfo.getCycleStartDate(), self.__seasonInfo.getCycleEndDate()])
            calendar.as_setDayTooltipTypeS(TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO)
        return

    def as_disposeS(self):
        super(RankedBattlesCalendarPopover, self).as_disposeS()

    def _dispose(self):
        super(RankedBattlesCalendarPopover, self)._dispose()

    def __getCyclesListString(self):
        key = RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARPOPOVER_CYCLEITEM
        cycles = self.__seasonInfo.getAllCycles()
        result = []
        for cycle in sorted(cycles.values()):
            formatter = text_styles.main if cycle.status == CYCLE_STATUS.CURRENT else text_styles.standard
            startDate = time_utils.getTimeStructInLocal(cycle.startDate)
            endDate = time_utils.getTimeStructInLocal(cycle.endDate)
            result.append(formatter(i18n.makeString(key, cycleNumber=cycle.ordinalNumber, day0='{:02d}'.format(startDate.tm_mday), month0='{:02d}'.format(startDate.tm_mon), day1='{:02d}'.format(endDate.tm_mday), month1='{:02d}'.format(endDate.tm_mon))))

        return '\n'.join(result)

    def __getAttentionText(self):
        key = RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARPOPOVER_ATTENTIONTEXT
        cycleNumber = self.__seasonInfo.getCycleOrdinalNumber()
        timeDelta = time_utils.getTimeDeltaFromNow(self.__seasonInfo.getCycleEndDate())
        endTimeStr = time_utils.getTillTimeString(timeDelta, RANKED_BATTLES.STATUS_TIMELEFT)
        if timeDelta <= time_utils.ONE_HOUR:
            formatter = text_styles.alert
        else:
            formatter = text_styles.neutral
        return formatter(i18n.makeString(key, cycleNumber=cycleNumber, timeLeft=endTimeStr))

    def __getCalendar(self):
        return self.components.get(VIEW_ALIAS.CALENDAR)
