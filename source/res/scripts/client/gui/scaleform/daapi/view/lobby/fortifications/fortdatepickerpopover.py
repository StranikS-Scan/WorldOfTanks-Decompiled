# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortDatePickerPopover.py
import fortified_regions
from helpers import i18n, time_utils
from debug_utils import LOG_DEBUG
from ClientFortifiedRegion import ATTACK_PLAN_RESULT
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.daapi.view.meta.FortDatePickerPopoverMeta import FortDatePickerPopoverMeta
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE

class FortDatePickerPopover(View, FortDatePickerPopoverMeta, SmartPopOverView, FortViewHelper):

    def __init__(self, ctx = None):
        super(FortDatePickerPopover, self).__init__()
        data = ctx.get('data', None)
        self.__selectedDate = data.timestamp if data else None
        self.__lowerTimeBound, self.__higherTimeBound = (0, 0)
        return

    def getCalendar(self):
        return self.components.get(VIEW_ALIAS.CALENDAR)

    def onWindowClose(self):
        self.destroy()

    def startCalendarListening(self):
        calendar = self.getCalendar()
        if calendar is not None:
            calendar.onMonthChangedEvent += self.onMonthChanged
            calendar.onDateSelectedEvent += self.onDateSelected
        return

    def stopCalendarListening(self):
        calendar = self.getCalendar()
        if calendar is not None:
            calendar.onMonthChangedEvent -= self.onMonthChanged
            calendar.onDateSelectedEvent -= self.onDateSelected
        return

    def onMonthChanged(self, timestamp):
        pass

    def onDateSelected(self, timestamp):
        self.fireEvent(events.CalendarEvent(events.CalendarEvent.DATE_SELECTED, timestamp), scope=EVENT_BUS_SCOPE.LOBBY)
        self.onWindowClose()

    def _populateDays(self):
        calendar = self.getCalendar()
        if calendar is not None:
            _ms = i18n.makeString
            dayStartTimestamp, _ = time_utils.getDayTimeBounds(self.__lowerTimeBound)
            daysData = []
            publicCache = self.fortCtrl.getPublicInfoCache()
            selectedClanDBID = publicCache.getSelectedID()
            if selectedClanDBID:
                clanCache = publicCache.getItem(selectedClanDBID)
                if clanCache:
                    fort = self.fortCtrl.getFort()
                    for dayIdx in xrange(FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT):
                        dayTimestamp = dayStartTimestamp + dayIdx * time_utils.ONE_DAY
                        result = fort.canPlanAttackOn(dayTimestamp, clanCache)
                        if result == ATTACK_PLAN_RESULT.OK:
                            dayData = {'tooltipHeader': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_AVAILABLE_HEADER),
                             'tooltipBody': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_AVAILABLE_BODY)}
                        else:
                            dayData = {'tooltipHeader': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_NOTAVAILABLE_HEADER),
                             'tooltipBody': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_NOTAVAILABLE_BODY),
                             'available': False}
                        dayData.update({'rawDate': dayTimestamp})
                        daysData.append(dayData)

            calendar.as_updateMonthEventsS(daysData)
        return

    def _populate(self):
        super(FortDatePickerPopover, self)._populate()
        self.startCalendarListening()
        self.__lowerTimeBound = time_utils.getCurrentTimestamp() + fortified_regions.g_cache.attackPreorderTime
        self.__higherTimeBound = self.__lowerTimeBound + (FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT - 1) * time_utils.ONE_DAY
        calendar = self.getCalendar()
        if calendar is not None:
            calendar.as_setMinAvailableDateS(self.__lowerTimeBound)
            calendar.as_setMaxAvailableDateS(self.__higherTimeBound)
            calendar.as_openMonthS(self.__lowerTimeBound)
            if self.__selectedDate is not None:
                calendar.as_selectDateS(self.__selectedDate)
        self._populateDays()
        return

    def _dispose(self):
        self.stopCalendarListening()
        super(FortDatePickerPopover, self)._dispose()
