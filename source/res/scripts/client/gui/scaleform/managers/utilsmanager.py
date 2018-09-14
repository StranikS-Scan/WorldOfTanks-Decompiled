# Embedded file name: scripts/client/gui/Scaleform/managers/UtilsManager.py
import calendar
import string
from gui.Scaleform.framework.managers.TextManager import TextManager
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.functions import getAbsoluteUrl
from helpers import i18n
import nations
import BigWorld
from gui import GUI_NATIONS
from gui.shared import utils
from gui.Scaleform.framework.entities.abstract.UtilsManagerMeta import UtilsManagerMeta
from helpers import i18n, getClientLanguage
SECONDS_IN_MINUTE = 60
MINUTES_IN_HOUR = 60
HOURS_IN_DAY = 24

class UtilsManager(UtilsManagerMeta):

    def __init__(self):
        super(UtilsManager, self).__init__()
        self._textMgr = TextManager()
        TextManager.setReference(self._textMgr)

    @property
    def textManager(self):
        return self._textMgr

    def getGUINations(self):
        return GUI_NATIONS

    def getNationNames(self):
        return nations.NAMES

    def getNationIndices(self):
        return nations.INDICES

    def changeStringCasing(self, s, isUpper, _):
        return utils.changeStringCasing(str(s).decode('utf-8'), isUpper)

    @classmethod
    def getAbsoluteUrl(cls, value):
        return getAbsoluteUrl(value)

    @classmethod
    def getHtmlIconText(cls, properties):
        template = "<img src='{0}' width='{1}' height='{2}' vspace='{3}' hspace='{4}'/>"
        absoluteUrl = cls.getAbsoluteUrl(properties.imageAlias)
        return template.format(absoluteUrl, properties.width, properties.height, properties.vSpace, properties.hSpace)

    def getFirstDayOfWeek(self):
        return calendar.firstweekday() + 1

    def getWeekDayNames(self, full, isUpper, isLower):
        source = list(MENU.DATETIME_WEEKDAYS_FULL_ENUM if full else MENU.DATETIME_WEEKDAYS_SHORT_ENUM)
        result = []
        for day in calendar.Calendar().iterweekdays():
            name = i18n.makeString(source[day])
            if isUpper:
                name = self.changeStringCasing(name, True, None)
            elif isLower:
                name = self.changeStringCasing(name, False, None)
            result.append(name)

        return result

    def getMonthsNames(self, full, isUpper, isLower):
        source = list(MENU.DATETIME_MONTHS_FULL_ENUM if full else MENU.DATETIME_MONTHS_SHORT_ENUM)
        result = []
        for key in source:
            name = i18n.makeString(key)
            if isUpper:
                name = self.changeStringCasing(name, True, None)
            elif isLower:
                name = self.changeStringCasing(name, False, None)
            result.append(name)

        return result

    def getDateParams(self, timestamp):
        from helpers import time_utils
        date = time_utils.getDateTimeInLocal(int(timestamp))
        result = {'year': date.year,
         'month': date.month - 1,
         'date': date.day,
         'hour': date.hour,
         'minute': date.minute,
         'second': date.second,
         'millisecond': date.microsecond * 1000}
        return result

    def _dispose(self):
        if self._textMgr is not None:
            TextManager.clearReference()
            self._textMgr = None
        super(UtilsManager, self)._dispose()
        return

    def intToStringWithPrefixPatern(self, value, count, fill):
        return ('{0:' + str(fill) + '>' + str(count) + '}').format(value)

    def isTwelveHoursFormat(self):
        return getClientLanguage() == 'en'


class ImageUrlProperties(object):

    def __init__(self, imageAlias, width = 16, height = 16, vSpace = -4, hSpace = 0):
        super(ImageUrlProperties, self).__init__()
        self.imageAlias = imageAlias
        self.width = width
        self.height = height
        self.vSpace = vSpace
        self.hSpace = hSpace
