# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/backport/backport_time_utils.py
import time
from gui.impl.backport import text
from helpers import time_utils

def getTillTimeStringByRClass(timeValue, stringRClass, isRoundUp=False):
    gmtime = time.gmtime(timeValue)
    if isRoundUp and gmtime.tm_sec > 0:
        timeValue += time_utils.ONE_MINUTE
        gmtime = time.gmtime(timeValue)
    if timeValue >= time_utils.ONE_DAY:
        fmtKey = 'days'
        gmtime = time.gmtime(timeValue - time_utils.ONE_DAY)
    elif timeValue >= time_utils.ONE_HOUR:
        fmtKey = 'hours'
    elif timeValue >= time_utils.ONE_MINUTE:
        fmtKey = 'min'
    else:
        fmtKey = 'lessMin'
    fmtValues = {'day': str(time.struct_time(gmtime).tm_yday),
     'hour': time.strftime('%H', gmtime),
     'min': time.strftime('%M', gmtime),
     'sec': time.strftime('%S', gmtime)}
    return text(stringRClass.dyn(fmtKey)(), **fmtValues)
