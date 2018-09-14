# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/stored_sorting.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from account_helpers.AccountSettings import STATS_SORTIE_SORTING
from constants import ARENA_BONUS_TYPE
__all__ = ('STATS_REGULAR_SORTING', 'STATS_SORTIE_SORTING', 'writeStatsSorting', 'readStatsSorting')

def writeStatsSorting(bonusType, iconType, sortDirection):
    key = STATS_REGULAR_SORTING
    value = {'iconType': iconType,
     'sortDirection': sortDirection}
    AccountSettings.setSettings(key, value)


def readStatsSorting(key):
    assert key in (STATS_REGULAR_SORTING, STATS_SORTIE_SORTING), 'Key is invalid'
    settings = AccountSettings.getSettings(key)
    return (settings.get('iconType'), settings.get('sortDirection'))
