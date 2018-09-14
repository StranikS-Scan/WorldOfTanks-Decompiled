# Embedded file name: scripts/client/helpers/tips.py
import random
import re
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import i18n

def _readNumberOfTips():
    result = 0
    tipsPattern = re.compile('^tip(\\d+)$')
    try:
        translator = i18n.g_translators['tips']
    except IOError:
        LOG_CURRENT_EXCEPTION()
        return result

    for key in translator._catalog.iterkeys():
        if len(key) > 0:
            sreMatch = tipsPattern.match(key)
            if sreMatch is not None and len(sreMatch.groups()) > 0:
                number = int(sreMatch.groups()[0])
                result = max(number, result)

    return result


def getNextNumberOfTip():
    return random.randint(0, g_totalNumberOfTips)


def getTip():
    return i18n.makeString('#tips:tip{0:d}'.format(getNextNumberOfTip()))


g_totalNumberOfTips = _readNumberOfTips()
