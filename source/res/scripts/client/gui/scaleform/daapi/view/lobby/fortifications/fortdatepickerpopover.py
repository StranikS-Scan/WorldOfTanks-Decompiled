# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortDatePickerPopover.py
import fortified_regions
from helpers import i18n, time_utils
from ClientFortifiedRegion import ATTACK_PLAN_RESULT
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.daapi.view.meta.FortDatePickerPopoverMeta import FortDatePickerPopoverMeta
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class FortDatePickerPopover(FortDatePickerPopoverMeta, FortViewHelper):

    class TIME_LIMITS:
        LOW = FORTIFICATION_ALIASES.ACTIVE_EVENTS_PAST_LIMIT * time_utils.ONE_DAY
        HIGH = FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT * time_utils.ONE_DAY

    def __init__(self, ctx):
        super(FortDatePickerPopover, self).__init__()
        self.__selectedDate = ctx['data'].timestamp
        self.__lowerTimeBound = time_utils.getCurrentLocalServerTimestamp() + fortified_regions.g_cache.attackPreorderTime
        self.__higherTimeBound = self.__lowerTimeBound + (FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT - 1) * time_utils.ONE_DAY

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

    def onFortBattleChanged(self, cache, item, battleItem):
        self._populateDays()

    def onFortBattleRemoved(self, cache, battleID):
        self._populateDays()

    def _populateDays(self):
        calendar = self.getCalendar()
        if calendar is not None:
            _ms = i18n.makeString
            dayStartTimestamp, _ = time_utils.getDayTimeBoundsForLocal(self.__lowerTimeBound)
            daysData = []
            publicCache = self.fortCtrl.getPublicInfoCache()
            clanCard = publicCache.getSelectedClanCard()
            if clanCard:
                fort = self.fortCtrl.getFort()
                for dayIdx in xrange(FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT):
                    dayTimestamp = dayStartTimestamp + dayIdx * time_utils.ONE_DAY
                    result = fort.canPlanAttackOn(dayTimestamp, clanCard)
                    if result == ATTACK_PLAN_RESULT.OK:
                        dayData = {'tooltipHeader': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_AVAILABLE_HEADER),
                         'tooltipBody': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_AVAILABLE_BODY)}
                    elif result == ATTACK_PLAN_RESULT.OPP_BUSY:
                        dayData = {'tooltipHeader': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_BUSY_HEADER),
                         'tooltipBody': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_BUSY_BODY),
                         'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_NOTAVAILABLEBG}
                    else:
                        dayData = {'tooltipHeader': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_NOTAVAILABLE_HEADER),
                         'tooltipBody': _ms(FORTIFICATIONS.FORTDATEPICKERPOPOVER_CALENDAR_DAYTOOLTIP_NOTAVAILABLE_BODY),
                         'available': False}
                    dayData.update({'rawDate': dayTimestamp})
                    daysData.append(dayData)

            calendar.as_updateMonthEventsS(daysData)
        return

    @classmethod
    def _isValidTime(cls, timestampToCheck, rootTimestamp = None):
        rootTimestamp = rootTimestamp or time_utils.getCurrentTimestamp()
        minLimit = rootTimestamp - cls.TIME_LIMITS.LOW
        dayStart, _ = time_utils.getDayTimeBoundsForLocal(minLimit)
        minLimit = dayStart
        maxLimit = rootTimestamp + cls.TIME_LIMITS.HIGH
        _, dayEnd = time_utils.getDayTimeBoundsForLocal(maxLimit)
        maxLimit = dayEnd
        return minLimit < timestampToCheck < maxLimit

    def _populate(self):
        super(FortDatePickerPopover, self)._populate()
        self.startCalendarListening()
        self.startFortListening()
        calendar = self.getCalendar()
        if calendar is not None:
            calendar.as_setMinAvailableDateS(self.__lowerTimeBound)
            calendar.as_setMaxAvailableDateS(self.__higherTimeBound)
            calendar.as_openMonthS(self.__selectedDate)
            calendar.as_selectDateS(self.__selectedDate)
        self._populateDays()
        return

    def _dispose(self):
        self.stopFortListening()
        self.stopCalendarListening()
        super(FortDatePickerPopover, self)._dispose()
