# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/UtilsManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class UtilsManagerMeta(BaseDAAPIModule):

    def getNationNames(self):
        self._printOverrideError('getNationNames')

    def getNationIndices(self):
        self._printOverrideError('getNationIndices')

    def getGUINations(self):
        self._printOverrideError('getGUINations')

    def changeStringCasing(self, string, isUpper, properties):
        self._printOverrideError('changeStringCasing')

    def getAbsoluteUrl(self, relativeUrl):
        self._printOverrideError('getAbsoluteUrl')

    def getHtmlIconText(self, properties):
        self._printOverrideError('getHtmlIconText')

    def getFirstDayOfWeek(self):
        self._printOverrideError('getFirstDayOfWeek')

    def getWeekDayNames(self, full, isUpper, isLower):
        self._printOverrideError('getWeekDayNames')

    def getMonthsNames(self, full, isUpper, isLower):
        self._printOverrideError('getMonthsNames')

    def intToStringWithPrefixPatern(self, value, count, fill):
        self._printOverrideError('intToStringWithPrefixPatern')

    def isTwelveHoursFormat(self):
        self._printOverrideError('isTwelveHoursFormat')

    def as_setImageCacheSettingsS(self, maxSize, minSize):
        if self._isDAAPIInited():
            return self.flashObject.as_setImageCacheSettings(maxSize, minSize)
