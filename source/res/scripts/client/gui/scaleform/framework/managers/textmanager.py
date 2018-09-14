# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TextManager.py
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.entities.abstract.TextManagerMeta import TextManagerMeta
from gui.Scaleform.genConsts.TEXT_MANAGER_STYLES import TEXT_MANAGER_STYLES as _TMS
from gui.shared.formatters import text_styles

class TextManager(TextManagerMeta):

    def __init__(self):
        super(TextManager, self).__init__()
        self.__styles = text_styles.getRawStyles([ v for k, v in _TMS.__dict__.iteritems() if not k.startswith('_') ])

    def getTextStyle(self, style):
        if style in self.__styles:
            result = self.__styles[style]
        else:
            LOG_ERROR('Style is not found', style)
            result = ''
        return result

    def _dispose(self):
        self.__styles.clear()
        super(TextManager, self)._dispose()


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
