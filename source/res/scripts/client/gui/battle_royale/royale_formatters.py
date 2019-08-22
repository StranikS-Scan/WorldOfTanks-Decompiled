# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_formatters.py
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import RoyaleCurtailingAwardsComposer
from gui.battle_royale.constants import ROYALE_AWARDS_ORDER, DEFAULT_REWARDS_COUNT
from gui.impl.backport.backport_system_locale import getNiceNumberFormat
from gui.server_events.awards_formatters import AWARDS_SIZES, getRoyaleAwardsPacker
_UNAVAILABLE_VALUE = 0
_UNAVAILABLE_SYMBOL = '--'

def getTitleColumnRewardsFormatter(maxRewardsCount=DEFAULT_REWARDS_COUNT):
    return _TitleColumnRewardsComposer(maxRewardsCount)


class _TitleColumnRewardsComposer(RoyaleCurtailingAwardsComposer):

    def __init__(self, displayedAwardsCount):
        super(_TitleColumnRewardsComposer, self).__init__(displayedAwardsCount, awardsFormatter=getRoyaleAwardsPacker())

    def setMaxRewardsCount(self, maxRewardsCount):
        self._displayedRewardsCount = maxRewardsCount

    def getFormattedBonuses(self, bonuses, size=AWARDS_SIZES.SMALL, compareMethod=None):
        bonuses = sorted(bonuses, cmp=_sortBonusesFunc, reverse=True)
        return super(_TitleColumnRewardsComposer, self).getFormattedBonuses(bonuses, size)


def _getOrderByBonusType(bonusName):
    return ROYALE_AWARDS_ORDER.index(bonusName) if bonusName in ROYALE_AWARDS_ORDER else -1


def _sortBonusesFunc(b1, b2):
    return cmp(_getOrderByBonusType(b1.getName()), _getOrderByBonusType(b2.getName()))


def _getValueOrUnavailable(targetValue):
    return targetValue if targetValue is not None else _UNAVAILABLE_VALUE


def getIntegerStrStat(value):
    return _UNAVAILABLE_SYMBOL if _getValueOrUnavailable(value) == _UNAVAILABLE_VALUE else getNiceNumberFormat(value)
