# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/marathon/marathon_header_tooltips.py
import time
import typing
from gui.Scaleform import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.marathon.marathon_constants import MarathonState
from gui.shared.formatters import text_styles
from helpers import i18n
from helpers.time_utils import ONE_DAY, getTimeStructInLocal, ONE_HOUR

class BaseTooltip(object):

    def __init__(self, dataContainer):
        self._data = dataContainer

    def create(self):
        pass


class SimpleTextHeaderTooltip(BaseTooltip):

    def create(self):
        startDate, finishDate = self._data.getGroupStartFinishTime()
        startDateStruct = getTimeStructInLocal(startDate)
        finishDateStruct = getTimeStructInLocal(finishDate)
        startDateText = text_styles.main(backport.text(TOOLTIPS.MARATHON_DATE, day=startDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(startDateStruct.tm_mon)), hour=startDateStruct.tm_hour, minutes=i18n.makeString('%02d', startDateStruct.tm_min)))
        finishDateText = text_styles.main(backport.text(TOOLTIPS.MARATHON_DATE, day=finishDateStruct.tm_mday, month=i18n.makeString(MENU.datetime_months(finishDateStruct.tm_mon)), hour=finishDateStruct.tm_hour, minutes=i18n.makeString('%02d', finishDateStruct.tm_min)))
        text = text_styles.main(backport.text(TOOLTIPS.MARATHON_SUBTITLE, startDate=startDateText, finishDate=finishDateText))
        return ('', text)


class ProgressHeaderTooltip(BaseTooltip):

    def create(self):
        icon = self._data.icons.iconFlag
        text = self.__getProgressInDays(self._data.getTimeFromGroupStart())
        return (icon, text)

    def __getProgressInDays(self, timeValue):
        gmtime = time.gmtime(timeValue)
        text = text_styles.stats(backport.text(self._data.tooltips.daysShort, value=str(time.struct_time(gmtime).tm_yday)))
        return text_styles.main(backport.text(self._data.tooltips.stateProgress, value=text))


class CountdownHeaderTooltip(BaseTooltip):

    def create(self):
        firstQuestStartTimeLeft, firstQuestFinishTimeLeft = self._data.getQuestTimeInterval()
        if self._data.state == MarathonState.NOT_STARTED:
            icon = self._data.icons.timeIconGlow
            text = self.__getTillTimeStart(firstQuestStartTimeLeft)
        elif self._data.state == MarathonState.IN_PROGRESS:
            text = self.__getTillTimeEnd(firstQuestFinishTimeLeft)
            if firstQuestFinishTimeLeft > ONE_DAY:
                icon = self._data.icons.iconFlag
            else:
                icon = self._data.icons.timeIconGlow
        else:
            icon = self._data.icons.iconFlag
            text = text_styles.main(backport.text(self._data.tooltips.stateComplete))
        return (icon, text)

    def __getFormattedTillTimeString(self, timeValue, keyNamespace, extraFmt=False):
        gmtime = time.gmtime(timeValue)
        if timeValue >= ONE_DAY:
            text = backport.text(self._data.tooltips.daysShort, value=str(gmtime.tm_yday))
        elif timeValue >= ONE_HOUR:
            text = backport.text(self._data.tooltips.hoursShort, value=str(gmtime.tm_hour + 1))
        else:
            text = backport.text(self._data.tooltips.minutesShort, value=str(gmtime.tm_min + 1))
        return text_styles.main(backport.text(keyNamespace, value=text_styles.stats(text))) if extraFmt or timeValue >= ONE_DAY else text_styles.tutorial(backport.text(keyNamespace, value=text))

    def __getTillTimeStart(self, value):
        return self.__getFormattedTillTimeString(value, self._data.tooltips.stateStart, extraFmt=True)

    def __getTillTimeEnd(self, value):
        return self.__getFormattedTillTimeString(value, self._data.tooltips.stateEnd)
