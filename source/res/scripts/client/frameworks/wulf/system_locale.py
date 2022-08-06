# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/system_locale.py
import typing
from .gui_constants import NumberFormatType, RealFormatType
from .gui_constants import TimeFormatType, DateFormatType
from .py_object_binder import PyObjectEntity

class SystemLocale(PyObjectEntity):

    @classmethod
    def create(cls, proxy):
        locale_ = SystemLocale()
        locale_.bind(proxy)
        return locale_

    def destroy(self):
        self.unbind()

    def getNumberFormat(self, value, formatType=NumberFormatType.INTEGRAL):
        return self.proxy.getNumberFormat(int(value), formatType)

    def getRealFormat(self, value, formatType=RealFormatType.FRACTIONAL):
        return self.proxy.getRealFormat(value, formatType)

    def getTimeFormat(self, value, formatType=TimeFormatType.SHORT_FORMAT):
        return self.proxy.getTimeFormat(value, formatType)

    def getDateFormat(self, value, formatType=DateFormatType.SHORT_FORMAT):
        return self.proxy.getDateFormat(value, formatType)

    def caseMap(self, value, caseType):
        return self.proxy.caseMap(value, caseType)
