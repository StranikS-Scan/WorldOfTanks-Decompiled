# Embedded file name: scripts/client/gui/Scaleform/managers/UtilsManager.py
import calendar
from gui.Scaleform.framework.managers.TextManager import TextManager
from gui.Scaleform.locale.MENU import MENU
from gui.shared.utils.functions import getAbsoluteUrl
import nations
import BigWorld
from gui import GUI_NATIONS, GUI_SETTINGS
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

    def registerTextManager(self, flashObject):
        self._textMgr.setFlashObject(flashObject)

    def _populate(self):
        super(UtilsManager, self)._populate()
        settings = GUI_SETTINGS.imageCache
        self.as_setImageCacheSettingsS(settings['maxSize'], settings['minSize'])

    def destroy(self):
        self.__unregisterMrgs()
        super(UtilsManagerMeta, self).destroy()

    def __unregisterMrgs(self):
        self._textMgr.destroy()
        self._textMgr = None
        return

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
        return template.format(properties.imageAlias, properties.width, properties.height, properties.vSpace, properties.hSpace)

    def getFirstDayOfWeek(self):
        return BigWorld.wg_firstDayOfWeek() + 1

    def getWeekDayNames(self, full, isUpper, isLower):
        source = list(MENU.DATETIME_WEEKDAYS_FULL_ENUM if full else MENU.DATETIME_WEEKDAYS_SHORT_ENUM)
        result = []
        for day in calendar.Calendar(firstweekday=BigWorld.wg_firstDayOfWeek()).iterweekdays():
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

    def _dispose(self):
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
