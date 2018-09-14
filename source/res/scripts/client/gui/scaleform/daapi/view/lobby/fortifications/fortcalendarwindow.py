# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/FortCalendarWindow.py
import BigWorld
from collections import defaultdict
from helpers import time_utils
from helpers.i18n import makeString as _ms
from gui import makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortCalendarWindowMeta import FortCalendarWindowMeta
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.utils import toLower
from gui.shared.fortifications.fort_seqs import BATTLE_ITEM_TYPE
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.fort_formatters import getDivisionIcon

class FortCalendarWindow(FortViewHelper, FortCalendarWindowMeta):

    class TIME_LIMITS:
        LOW = FORTIFICATION_ALIASES.ACTIVE_EVENTS_PAST_LIMIT * time_utils.ONE_DAY
        HIGH = FORTIFICATION_ALIASES.ACTIVE_EVENTS_FUTURE_LIMIT * time_utils.ONE_DAY

    def __init__(self, ctx):
        super(FortCalendarWindow, self).__init__()
        self.__selectedDate = ctx.get('dateSelected') or time_utils.getCurrentTimestamp()

    def getCalendar(self):
        return self.components.get(VIEW_ALIAS.CALENDAR)

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
        self.__selectedDate = timestamp
        self._populateMonthEvents()
        self._populateCalendarMessage()

    def onDateSelected(self, timestamp):
        self.__selectedDate = timestamp
        self._populatePreviewBlock()

    def onWindowClose(self):
        self.destroy()

    def onFortBattleChanged(self, cache, item, battleItem):
        self._update()

    def onFortBattleRemoved(self, cache, battleID):
        self._update()

    def _populateMonthEvents(self):
        calendar = self.getCalendar()
        if calendar is not None:
            result = []
            for dayStartTimestamp, battles in self._getBattlesByDay().iteritems():
                if time_utils.isFuture(dayStartTimestamp):
                    tooltipHead = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_FUTURE_HEADER, count=len(battles))
                    tooltipBody = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_FUTURE_BODY)
                    iconSource = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTUREBG
                elif time_utils.isToday(dayStartTimestamp):
                    finishedBattles = [ b for b in battles if b.isEnded() ]
                    upcomingBattles = [ b for b in battles if b.isPlanned() ]
                    if not upcomingBattles:
                        tooltipHead = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_PAST_HEADER, count=len(finishedBattles))
                        tooltipBody = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_PAST_BODY)
                        iconSource = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEPASTBG
                    else:
                        tooltipHead = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_FUTURE_HEADER, count=len(upcomingBattles))
                        tooltipBody = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_FUTURE_BODY)
                        iconSource = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTUREBG
                else:
                    tooltipHead = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_PAST_HEADER, count=len(battles))
                    tooltipBody = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_CALENDAR_DAYTOOLTIP_PAST_BODY)
                    iconSource = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEPASTBG
                result.append({'tooltipHeader': tooltipHead,
                 'tooltipBody': tooltipBody,
                 'iconSource': iconSource,
                 'rawDate': dayStartTimestamp})

            calendar.as_updateMonthEventsS(result)
        return

    def _populatePreviewBlock(self):
        fort = self.fortCtrl.getFort()
        localDateTime = time_utils.getDateTimeInLocal(self.__selectedDate)
        targetDayStartTimestamp, _ = time_utils.getDayTimeBoundsForLocal(self.__selectedDate)
        eventItems, dateInfo, noEventsText = [], None, None
        dateString = _ms(MENU.DATETIME_SHORTDATEFORMATWITHOUTYEAR, weekDay=_ms('#menu:dateTime/weekDays/full/%d' % localDateTime.isoweekday()), monthDay=localDateTime.day, month=toLower(_ms('#menu:dateTime/months/full/%d' % localDateTime.month)))
        if fort.isOnVacationAt(self.__selectedDate):
            noEventsText = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_EMPTY_VACATION, date=fort.getVacationDateStr())
        elif not self._isValidTime(self.__selectedDate):
            noEventsText = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_EMPTY_NOTAVAILABLE)
        else:
            for dayStartTimestamp, battles in self._getBattlesByDay().iteritems():
                if dayStartTimestamp == targetDayStartTimestamp:
                    for battle in sorted(battles):
                        startTimestamp = battle.getStartTime()
                        battleHasEnded = battle.isEnded()
                        opponentsClanInfo = battle.getOpponentClanInfo()
                        if battle.getType() == BATTLE_ITEM_TYPE.ATTACK:
                            if battleHasEnded:
                                icon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCEPAST
                            else:
                                icon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_OFFENCEFUTURE
                            titleTpl = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_ITEM_TITLE_OFFENCE)
                        else:
                            if battleHasEnded:
                                icon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEPAST
                            else:
                                icon = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_DEFENCEFUTURE
                            titleTpl = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_ITEM_TITLE_DEFENCE)
                        tankIconVO = getDivisionIcon(battle.defenderFortLevel, battle.attackerFortLevel, determineAlert=battle.getType() == BATTLE_ITEM_TYPE.ATTACK)
                        if battle.isWin():
                            background = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_BATTLEFORTVICTORY
                            resultLabel = 'win'
                        elif battle.isLose():
                            background = RES_ICONS.MAPS_ICONS_LIBRARY_FORTIFICATION_BATTLEFORTDEFEAT
                            resultLabel = 'lose'
                        else:
                            background, resultLabel = (None, None)
                        eventItem = {'icon': icon,
                         'title': titleTpl % {'clanName': '[%s]' % opponentsClanInfo[1]},
                         'clanID': opponentsClanInfo[0],
                         'direction': _ms(FORTIFICATIONS.GENERAL_DIRECTION, value=_ms('#fortifications:General/directionName%d' % battle.getDirection())),
                         'timeInfo': _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_ITEM_TIMEINFO) % {'startTime': BigWorld.wg_getShortTimeFormat(startTimestamp),
                                      'endTime': BigWorld.wg_getShortTimeFormat(startTimestamp + time_utils.ONE_HOUR)},
                         'background': background,
                         'tankIconVO': tankIconVO,
                         'showTankIcon': not battleHasEnded}
                        if battleHasEnded and resultLabel:
                            resultText = makeHtmlString('html_templates:lobby/fortifications', 'battleResult', {'result': _ms(MENU.finalstatistic_commonstats_resultlabel(resultLabel))})
                            eventItem.update({'result': resultText})
                        eventItems.append(eventItem)

            if not len(eventItems):
                noEventsText = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_EMPTY_NOEVENTS)
        if len(eventItems) > 0:
            dateInfo = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_EVENTSLIST_INFO_BATTLESCOUNT, eventsCount=len(eventItems))
        self.as_updatePreviewDataS({'dateString': dateString,
         'dateInfo': dateInfo,
         'noEventsText': noEventsText,
         'events': eventItems})
        return

    def _populateCalendarMessage(self):
        calendar = self.getCalendar()
        if calendar is not None:
            fort, message = self.fortCtrl.getFort(), ''
            vacationStart, vacationEnd = fort.getVacationDate()
            if self._isValidTime(vacationStart, self.__selectedDate) or self._isValidTime(vacationEnd, self.__selectedDate):
                message = _ms(FORTIFICATIONS.FORTCALENDARWINDOW_MESSAGE_VACATION, date=fort.getVacationDateStr())
            calendar.as_setCalendarMessageS(message)
        return

    def _populate(self):
        super(FortCalendarWindow, self)._populate()
        self.startFortListening()
        self.startCalendarListening()
        self._update()

    def _dispose(self):
        self.stopFortListening()
        self.stopCalendarListening()
        super(FortCalendarWindow, self)._dispose()

    def _update(self):
        calendar = self.getCalendar()
        if calendar is not None:
            lowerTimeBound = time_utils.getCurrentLocalServerTimestamp() - self.TIME_LIMITS.LOW
            higherTimeBound = time_utils.getCurrentLocalServerTimestamp() + self.TIME_LIMITS.HIGH
            calendar.as_setMinAvailableDateS(lowerTimeBound)
            calendar.as_setMaxAvailableDateS(higherTimeBound)
            calendar.as_openMonthS(self.__selectedDate)
            calendar.as_selectDateS(self.__selectedDate)
        self._populateMonthEvents()
        self._populatePreviewBlock()
        self._populateCalendarMessage()
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

    def _getBattlesByDay(self):
        result, fort = defaultdict(list), self.fortCtrl.getFort()
        for battle in fort.getAttacks() + fort.getDefences():
            startTimestamp = battle.getStartTime()
            if self._isValidTime(startTimestamp):
                dayStartTimestamp, _ = time_utils.getDayTimeBoundsForLocal(startTimestamp)
                result[dayStartTimestamp].append(battle)

        return result
