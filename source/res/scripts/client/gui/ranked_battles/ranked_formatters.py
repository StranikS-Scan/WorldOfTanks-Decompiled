# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_formatters.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.ranked_battles.constants import AWARDS_ORDER, DEFAULT_REWARDS_COUNT
from gui.server_events.awards_formatters import AWARDS_SIZES, getRankedAwardsPacker
from gui.shared.formatters import text_styles
_MAX_VISIBLE_AWARDS = 6
_awardsFormatter = CurtailingAwardsComposer(_MAX_VISIBLE_AWARDS)
_UNAVAILABLE_VALUE = -1
_UNAVAILABLE_SYMBOL = '--'
_PERCENT_SYMBOL = '%'

class _RanksColumnRewardsComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount):
        super(_RanksColumnRewardsComposer, self).__init__(displayedAwardsCount, awardsFormatter=getRankedAwardsPacker())

    def setMaxRewardsCount(self, maxRewardsCount):
        self._displayedRewardsCount = maxRewardsCount

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL):
        bonuses = sorted(bonuses, cmp=_sortBonusesFunc, reverse=True)
        return super(_RanksColumnRewardsComposer, self).getFormattedBonuses(bonuses, size)


def getFloatPercentStrStat(value):
    if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE:
        return _UNAVAILABLE_SYMBOL
    value = value * 100
    return text_styles.concatStylesToSingleLine(BigWorld.wg_getNiceNumberFormat(value), _PERCENT_SYMBOL)


def getIntegerStrStat(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else BigWorld.wg_getNiceNumberFormat(value)


def getTimeLongStr(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else BigWorld.wg_getLongTimeFormat(value)


def getRanksColumnRewardsFormatter(maxRewardsCount=DEFAULT_REWARDS_COUNT):
    return _RanksColumnRewardsComposer(maxRewardsCount)


def _getOrderByBonusType(bonusName):
    return AWARDS_ORDER.index(bonusName) if bonusName in AWARDS_ORDER else -1


def _getValueOrUnavailable(targetValue):
    return targetValue if targetValue is not None else _UNAVAILABLE_VALUE


def _sortBonusesFunc(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName()), _getOrderByBonusType(b2.getName()))
