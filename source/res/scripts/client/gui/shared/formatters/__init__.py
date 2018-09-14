# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import BigWorld
from gui.shared.formatters import icons
from gui.shared.formatters import text_styles
from gui.shared.formatters import time_formatters
from helpers.i18n import makeString
__all__ = ('icons', 'text_styles', 'time_formatters')

def getGlobalRatingFmt(globalRating):
    if globalRating >= 0:
        return BigWorld.wg_getIntegralFormat(globalRating)
    return '--'


def formatPrice(price, reverse = False):
    outPrice = []
    credits, gold = price[:2]
    if credits != 0 or gold == 0:
        cname = makeString('#menu:price/credits') + ': '
        cformatted = BigWorld.wg_getIntegralFormat(credits)
        outPrice.extend([cformatted, ' ', cname] if reverse else [cname, ' ', cformatted])
        if gold != 0:
            outPrice.append(', ')
    if gold != 0:
        gname = makeString('#menu:price/gold') + ': '
        gformatted = BigWorld.wg_getGoldFormat(gold)
        outPrice.extend([gformatted, ' ', gname] if reverse else [gname, ' ', gformatted])
    return ''.join(outPrice)


def formatGoldPrice(gold, reverse = False):
    outPrice = []
    gname = makeString('#menu:price/gold') + ': '
    gformatted = BigWorld.wg_getGoldFormat(gold)
    outPrice.extend([gformatted, ' ', gname] if reverse else [gname, ' ', gformatted])
    return ''.join(outPrice)
