# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TextManager.py
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.framework.entities.abstract.TextManagerMeta import TextManagerMeta
from gui.Scaleform.locale.MENU import MENU
from helpers import time_utils, i18n

class TextManager(TextManagerMeta):
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
        return time_utils.getTillTimeString(seconds, MENU.TIME_TIMEVALUE)

    @classmethod
    def concatStyles(cls, messages = None):
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
                        style = cls.getIcon(messageItem[0])
                    else:
                        LOG_ERROR('not found icon source. ', messageItem)
                elif length > 1:
                    key, value = messageItem
                    style = cls.getText(key, value)
                result += style

            return result

    def getTextStyle(self, style):
        return makeHtmlString('html_templates:lobby/textStyle', style)


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
    CREDITS = 'credits'
    GOLD = 'gold'
    XP = 'xp'
    FREE_XP = 'freeXP'
    ARROW_BUTTON = 'arrowButton'
    NO_SEASON = 'noSeason'
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
     HUMANS,
     CREDITS,
     GOLD,
     XP,
     FREE_XP,
     ARROW_BUTTON,
     NO_SEASON)
