# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/stored_sorting.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import STATS_REGULAR_SORTING
from gui.shared.system_factory import collectBattleResultsStatsSorting
from soft_exception import SoftException
__all__ = ('STATS_REGULAR_SORTING', 'writeStatsSorting', 'readStatsSorting')
_DEFAULT_SORTING_KEY = STATS_REGULAR_SORTING

def writeStatsSorting(bonusType, iconType, sortDirection):
    key = collectBattleResultsStatsSorting().get(bonusType, _DEFAULT_SORTING_KEY)
    value = {'iconType': iconType,
     'sortDirection': sortDirection}
    AccountSettings.setSettings(key, value)


def readStatsSorting(key):
    if key not in (_DEFAULT_SORTING_KEY,) + tuple(collectBattleResultsStatsSorting().values()):
        raise SoftException('Sorting key {} is invalid'.format(key))
    settings = AccountSettings.getSettings(key)
    return (settings.get('iconType'), settings.get('sortDirection'))
