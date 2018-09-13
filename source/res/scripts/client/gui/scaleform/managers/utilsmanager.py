# Embedded file name: scripts/client/gui/Scaleform/managers/UtilsManager.py
import calendar
import string
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.functions import getAbsoluteUrl
from helpers import i18n
import nations
import BigWorld
from gui import GUI_NATIONS
from gui.shared import utils
from gui.Scaleform.framework.entities.abstract.UtilsManagerMeta import UtilsManagerMeta
from helpers import i18n, getClientLanguage

class UtilsManager(UtilsManagerMeta):

    def getGUINations(self):
        return GUI_NATIONS

    def getNationNames(self):
        return nations.NAMES

    def getNationIndices(self):
        return nations.INDICES

    def changeStringCasing(self, s, isUpper, _):
        return utils.changeStringCasing(str(s).decode('utf-8'), isUpper)

    def getAbsoluteUrl(self, value):
        return getAbsoluteUrl(value)

    def getHtmlIconText(self, properties):
        template = "<img src='{0}' width='{1}' height='{2}' vspace='{3}' hspace='{4}'/>"
        absoluteUrl = self.getAbsoluteUrl(properties.imageAlias)
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
