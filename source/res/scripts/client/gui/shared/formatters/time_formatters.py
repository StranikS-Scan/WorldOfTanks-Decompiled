# Embedded file name: scripts/client/gui/shared/formatters/time_formatters.py
import math
from gui.Scaleform.framework.managers.TextManager import TextManager
from helpers import i18n, time_utils

def getRentLeftTimeStr(localization, rentLeftTime, timeStyle = None, ctx = None):
    if ctx is None:
        ctx = {}
    if rentLeftTime > 0:
        if rentLeftTime > time_utils.ONE_DAY:
            timeLeft = str(int(math.ceil(float(rentLeftTime) / time_utils.ONE_DAY)))
            if timeStyle:
                timeLeft = TextManager.getText(timeStyle, timeLeft)
            return i18n.makeString((localization % 'days'), days=timeLeft, **ctx)
        else:
            timeLeft = str(int(math.ceil(float(rentLeftTime) / time_utils.ONE_HOUR)))
            if timeStyle:
                timeLeft = TextManager.getText(timeStyle, timeLeft)
            return i18n.makeString((localization % 'hours'), hours=timeLeft, **ctx)
    return ''
