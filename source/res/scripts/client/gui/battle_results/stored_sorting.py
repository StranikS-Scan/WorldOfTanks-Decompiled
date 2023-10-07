# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/stored_sorting.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from account_helpers.AccountSettings import STATS_SORTIE_SORTING
from account_helpers.AccountSettings import STATS_COMP7_SORTING
from account_helpers.AccountSettings import STATS_EVENT_SORTING
from soft_exception import SoftException
from constants import ARENA_BONUS_TYPE
__all__ = ('STATS_REGULAR_SORTING', 'STATS_SORTIE_SORTING', 'STATS_COMP7_SORTING', 'STATS_EVENT_SORTING', 'writeStatsSorting', 'readStatsSorting')
AVAILABLE_STATS_SORTINGS = [STATS_REGULAR_SORTING,
 STATS_SORTIE_SORTING,
 STATS_COMP7_SORTING,
 STATS_EVENT_SORTING]

def writeStatsSorting(bonusType, iconType, sortDirection):
    key = STATS_REGULAR_SORTING
    if bonusType == ARENA_BONUS_TYPE.COMP7:
        key = STATS_COMP7_SORTING
    value = {'iconType': iconType,
     'sortDirection': sortDirection}
    AccountSettings.setSettings(key, value)


def readStatsSorting(key):
    if key not in AVAILABLE_STATS_SORTINGS:
        raise SoftException('Sorting key {} is invalid'.format(key))
    settings = AccountSettings.getSettings(key)
    return (settings.get('iconType'), settings.get('sortDirection'))
