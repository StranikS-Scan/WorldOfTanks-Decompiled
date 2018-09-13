# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/fort_utils/fort_text.py
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from helpers import time_utils, i18n
PROMO_TITLE = 'promoTitle'
PROMO_SUB_TITLE = 'promoSubTitle'
HIGH_TITLE = 'highTitle'
MIDDLE_TITLE = 'middleTitle'
STATUS_CRITICAL_TEXT = 'statusCriticalText'
STATUS_WARNING_TEXT = 'statusWarningText'
STATUS_INFO_TEXT = 'statusInfoText'
MAIN_TEXT = 'mainText'
STANDARD_TEXT = 'standardText'
DISABLE_TEXT = 'disabledText'
SUCCESS_TEXT = 'successText'
ALERT_TEXT = 'alertText'
ERROR_TEXT = 'errorText'
NEUTRAL_TEXT = 'neutralText'
PURPLE_TEXT = 'purpleText'
STATS_TEXT = 'statsText'
CHECKMARK_ICON = 'checkmark'
NUT_ICON = 'nut'
PERCENT_ICON = 'percent'
ALERT_ICON = 'alert'
INFO_ICON = 'info'
ORDER_IN_PROGRESS_ICON = 'order_in_progress'
CLOCK_ICON = 'clock'
NOT_AVAILABLE = 'notAvailable'
LEVEL_5 = 'level5'
LEVEL_10 = 'level10'
SWORDS = 'swords'
HUMANS = 'humans'
ICONS = (NUT_ICON,
 PERCENT_ICON,
 ALERT_ICON,
 INFO_ICON,
 ORDER_IN_PROGRESS_ICON,
 CLOCK_ICON,
 CHECKMARK_ICON,
 NOT_AVAILABLE,
 LEVEL_5,
 LEVEL_10,
 SWORDS,
 HUMANS)

def getText(style = 'mainText', message = ''):
    text = makeHtmlString('html_templates:lobby/textStyle', style, {'message': str(message)})
    return text


def getIcon(style = None):
    if style is None or style not in ICONS:
        return
    else:
        iconRes = makeHtmlString('html_templates:lobby/iconText', style, {})
        return iconRes


def getTimeDurationStr(seconds):
    if seconds >= 60:
        return time_utils.getTillTimeString(seconds, FORTIFICATIONS.TIME_TIMEVALUE)
    else:
        return i18n.makeString(FORTIFICATIONS.TIME_TIMEVALUE_LESSMIN)


def concatStyles(messages = None):
    result = ''
    style = ''
    if messages is None:
        return result
    else:
        for messageItem in messages:
            length = len(messageItem)
            if length == 1:
                item = messageItem[0]
                if item is not None and item in ICONS:
                    style = getIcon(messageItem[0])
                else:
                    LOG_ERROR('not found icon source. ', messageItem)
            elif length > 1:
                key, value = messageItem
                style = getText(key, value)
            result += style

        return result
