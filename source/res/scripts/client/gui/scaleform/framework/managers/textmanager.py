# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TextManager.py
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.locale.MENU import MENU
from helpers import time_utils
from web_stubs import i18n

class TextManager:
    __reference = None

    @classmethod
    def setReference(cls, app):
        cls.__reference = app

    @classmethod
    def clearReference(cls):
        cls.__reference = None
        return

    @classmethod
    def reference(cls):
        return cls.__reference

    @classmethod
    def getText(self, style = 'mainText', message = ''):
        text = makeHtmlString('html_templates:lobby/textStyle', style, {'message': str(message)})
        return text

    @classmethod
    def getIcon(cls, style = None):
        if style is None or style not in TextIcons.ICONS:
            return
        else:
            iconRes = makeHtmlString('html_templates:lobby/iconText', style, {})
            return iconRes

    def getTimeDurationStr(self, seconds):
        if seconds >= 60:
            return time_utils.getTillTimeString(seconds, MENU.TIME_TIMEVALUE)
        else:
            return i18n.makeString(MENU.TIME_TIMEVALUE_LESSMIN)

    def concatStyles(self, messages = None):
        result = ''
        style = ''
        if messages is None:
            return result
        else:
            for messageItem in messages:
                length = len(messageItem)
                if length == 1:
                    item = messageItem[0]
                    if item is not None and item in TextIcons.ICONS:
                        style = self.getIcon(messageItem[0])
                    else:
                        LOG_ERROR('not found icon source. ', messageItem)
                elif length > 1:
                    key, value = messageItem
                    style = self.getText(key, value)
                result += style

            return result


class TextType:
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
    DEFRES_TEXT = 'defresText'
    GOLD_TEXT = 'goldText'
    CREDITS_TEXT = 'creditsText'
    EXP_TEXT = 'expText'
    STATS_TEXT = 'statsText'
    PLAYER_ONLINE_TEXT = 'playerOnline'
    PLAYER_OFFLINE_TEXT = 'playerOffline'


class TextIcons:
    CHECKMARK_ICON = 'checkmark'
    NUT_ICON = 'nut'
    PERCENT_ICON = 'percent'
    ALERT_ICON = 'alert'
    INFO_ICON = 'info'
    PREMIUM_IGR_SMALL = 'premiumIgrSmall'
    PREMIUM_IGR_BIG = 'premiumIgrBig'
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
     PREMIUM_IGR_SMALL,
     PREMIUM_IGR_BIG,
     ORDER_IN_PROGRESS_ICON,
     CLOCK_ICON,
     CHECKMARK_ICON,
     NOT_AVAILABLE,
     LEVEL_5,
     LEVEL_10,
     SWORDS,
     HUMANS)
