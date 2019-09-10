# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.impl import backport
from gui.ranked_battles.constants import AWARDS_ORDER, DEFAULT_REWARDS_COUNT
from gui.server_events.awards_formatters import AWARDS_SIZES, getRankedAwardsPacker
from gui.shared.formatters import text_styles
_MAX_VISIBLE_AWARDS = 6
_awardsFormatter = CurtailingAwardsComposer(_MAX_VISIBLE_AWARDS)
_UNAVAILABLE_VALUE = -1
_UNAVAILABLE_SYMBOL = '--'
_PERCENT_SYMBOL = '%'

class _RankedAwardsComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount):
        super(_RankedAwardsComposer, self).__init__(displayedAwardsCount, awardsFormatter=getRankedAwardsPacker())

    def setMaxRewardsCount(self, maxRewardsCount):
        self._displayedRewardsCount = maxRewardsCount

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, compareMethod=None):
        bonuses = sorted(bonuses, cmp=compareMethod if compareMethod else _sortBonusesFunc, reverse=True)
        return super(_RankedAwardsComposer, self).getFormattedBonuses(bonuses, size)


def getFloatPercentStrStat(value):
    if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE:
        return _UNAVAILABLE_SYMBOL
    value = value * 100
    return text_styles.concatStylesToSingleLine(backport.getNiceNumberFormat(value), _PERCENT_SYMBOL)


def getIntegerStrStat(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else backport.getNiceNumberFormat(value)


def getTimeLongStr(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else backport.getLongTimeFormat(value)


def getRankedAwardsFormatter(maxRewardsCount=DEFAULT_REWARDS_COUNT):
    return _RankedAwardsComposer(maxRewardsCount)


def _getOrderByBonusType(bonusName):
    return AWARDS_ORDER.index(bonusName) if bonusName in AWARDS_ORDER else -1


def _getValueOrUnavailable(targetValue):
    return targetValue if targetValue is not None else _UNAVAILABLE_VALUE


def _sortBonusesFunc(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName()), _getOrderByBonusType(b2.getName()))
