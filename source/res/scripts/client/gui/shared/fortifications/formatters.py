# Embedded file name: scripts/client/gui/shared/fortifications/formatters.py
import BigWorld
import constants
from helpers import time_utils, i18n
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS

def getDefencePeriodString(startTime):
    return '{0:>s} - {1:>s}'.format(BigWorld.wg_getShortTimeFormat(startTime), BigWorld.wg_getShortTimeFormat(startTime + time_utils.ONE_HOUR))


def getVacationPeriodString(startTime, endTime):
    return '{0:>s} - {1:>s}'.format(BigWorld.wg_getShortDateFormat(startTime), BigWorld.wg_getShortDateFormat(endTime))


def getDirectionString(dirIdx):
    return i18n.makeString(FORTIFICATIONS.GENERAL_DIRECTION, value=i18n.makeString('#fortifications:General/directionName%d' % dirIdx))


def getOrderUserString(orderTypeID):
    return i18n.makeString('#fortifications:orders/%s' % constants.FORT_ORDER_TYPE_NAMES[orderTypeID])


def getBuildingUserString(buildTypeID):
    return i18n.makeString('#fortifications:buildings/%s' % constants.FORT_BUILDING_TYPE_NAMES[buildTypeID])


def getDayOffString(offDay):
    return i18n.makeString('#menu:dateTime/weekDays/full/%d' % (offDay + 1))
