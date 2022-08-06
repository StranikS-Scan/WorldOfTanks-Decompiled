# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_system_locale.py
from frameworks import wulf

def getIntegralFormat(value):
    return wulf.getNumberFormat(int(value), wulf.NumberFormatType.INTEGRAL)


def getGoldFormat(value):
    return wulf.getNumberFormat(int(value), wulf.NumberFormatType.GOLD)


def getFractionalFormat(value):
    return wulf.getRealFormat(value, wulf.RealFormatType.FRACTIONAL)


def getNiceNumberFormat(value):
    return wulf.getRealFormat(value, wulf.RealFormatType.WO_ZERO_DIGITS)


def getShortTimeFormat(value):
    return wulf.getTimeFormat(value, wulf.TimeFormatType.SHORT_FORMAT)


def getLongTimeFormat(value):
    return wulf.getTimeFormat(value, wulf.TimeFormatType.LONG_FORMAT)


def getShortDateFormat(value):
    return wulf.getDateFormat(value, wulf.DateFormatType.SHORT_FORMAT)


def getLongDateFormat(value):
    return wulf.getDateFormat(value, wulf.DateFormatType.LONG_FORMAT)


def getYearMonthFormat(value):
    return wulf.getDateFormat(value, wulf.DateFormatType.YEAR_MONTH)


def getDateTimeFormat(value):
    return u'{0:>s} {1:>s}'.format(wulf.getDateFormat(value, wulf.DateFormatType.LONG_FORMAT), wulf.getTimeFormat(value, wulf.TimeFormatType.SHORT_FORMAT))


def upper(value):
    return wulf.caseMap(value, wulf.CaseType.UPPERCASE)


def lower(value):
    return wulf.caseMap(value, wulf.CaseType.LOWERCASE)
