# Embedded file name: scripts/client/gui/shared/formatters/__init__.py
import BigWorld

def getClanAbbrevString(clanAbbrev):
    return '[{0:>s}]'.format(clanAbbrev)


def getGlobalRatingFmt(globalRating):
    if globalRating >= 0:
        return BigWorld.wg_getIntegralFormat(globalRating)
    return '--'
