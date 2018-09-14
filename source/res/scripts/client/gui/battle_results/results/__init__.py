# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/results/__init__.py
from constants import ARENA_BONUS_TYPE
from gui.battle_results.results.club import ClubResults
from gui.battle_results.results.regular import RegularResults
_RESULTS_MAP = {ARENA_BONUS_TYPE.RATED_CYBERSPORT: ClubResults}
_DEFAULT_RESULTS = RegularResults

def createResults(results, dp):
    assert 'common' in results
    assert 'guiType' in results['common']
    bonusType = results['common']['bonusType']
    resultsClass = _RESULTS_MAP.get(bonusType, _DEFAULT_RESULTS)
    return resultsClass(results, dp)
