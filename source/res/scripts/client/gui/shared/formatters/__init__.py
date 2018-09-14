# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import BigWorld
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
__all__ = ('icons', 'text_styles', 'time_formatters')

def getClanAbbrevString(clanAbbrev):
    return '[{0:>s}]'.format(clanAbbrev)


def getGlobalRatingFmt(globalRating):
    if globalRating >= 0:
        return BigWorld.wg_getIntegralFormat(globalRating)
    return '--'
