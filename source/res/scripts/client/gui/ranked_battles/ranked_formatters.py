# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import CurtailingAwardsComposer
from gui.impl import backport
from gui.ranked_battles.constants import AWARDS_ORDER, DEFAULT_REWARDS_COUNT, YEAR_AWARDS_BONUS_ORDER
from gui.server_events.awards_formatters import AWARDS_SIZES, getRankedAwardsPacker
from gui.server_events.bonuses import getNonQuestBonuses
from gui.shared.formatters import text_styles
_UNAVAILABLE_VALUE = -1
_UNAVAILABLE_SYMBOL = '---'
_PERCENT_SYMBOL = '%'

class _RankedAwardsComposer(CurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount, context=None):
        super(_RankedAwardsComposer, self).__init__(displayedAwardsCount, awardsFormatter=getRankedAwardsPacker(context))

    def setMaxRewardsCount(self, maxRewardsCount):
        self._displayedRewardsCount = maxRewardsCount

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, compareMethod=None):
        bonuses = sorted(bonuses, cmp=compareMethod if compareMethod else _sortBonusesFunc, reverse=True)
        return super(_RankedAwardsComposer, self).getFormattedBonuses(bonuses, size)


class _BonusNameRankedAwardsComposer(_RankedAwardsComposer):

    def _packBonus(self, bonus, size=AWARDS_SIZES.SMALL):
        packBonus = super(_BonusNameRankedAwardsComposer, self)._packBonus(bonus, size)
        packBonus['bonusName'] = bonus.bonusName
        return packBonus


def getFloatPercentStrStat(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else text_styles.concatStylesToSingleLine(backport.getNiceNumberFormat(value * 100), _PERCENT_SYMBOL)


def getIntegerStrStat(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else backport.getNiceNumberFormat(value)


def getTimeLongStr(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else backport.getLongTimeFormat(value)


def getRankedAwardsFormatter(maxRewardsCount=DEFAULT_REWARDS_COUNT):
    return _RankedAwardsComposer(maxRewardsCount)


def getFormattedBonusesForYearAwardsWindow(rawRewards, maxRewardsCount=DEFAULT_REWARDS_COUNT, selectionsLeft=None):
    bonuses = []
    context = {'selectionsLeft': selectionsLeft} if selectionsLeft is not None else None
    composer = _BonusNameRankedAwardsComposer(maxRewardsCount, context)
    for name, value in rawRewards.iteritems():
        bonuses.extend(getNonQuestBonuses(name, value))

    return composer.getFormattedBonuses(bonuses, AWARDS_SIZES.BIG, compareMethod=rankedYearAwardsSortFunction)


def rankedYearAwardsSortFunction(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName(), order=YEAR_AWARDS_BONUS_ORDER), _getOrderByBonusType(b2.getName(), order=YEAR_AWARDS_BONUS_ORDER))


def _getOrderByBonusType(bonusName, order=AWARDS_ORDER):
    return order.index(bonusName) if bonusName in order else -1


def _getValueOrUnavailable(targetValue):
    return targetValue if targetValue is not None else _UNAVAILABLE_VALUE


def _sortBonusesFunc(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName()), _getOrderByBonusType(b2.getName()))
