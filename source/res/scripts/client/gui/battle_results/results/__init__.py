# Embedded file name: scripts/client/gui/battle_results/results/__init__.py
from constants import ARENA_BONUS_TYPE
from gui.battle_results.results.club import ClubResults
from gui.battle_results.results.regular import RegularResults
_RESULTS_MAP = {ARENA_BONUS_TYPE.RATED_CYBERSPORT: ClubResults}
_DEFAULT_RESULTS = RegularResults

def createResults(results, dp):
    raise 'common' in results or AssertionError
    raise 'guiType' in results['common'] or AssertionError
    bonusType = results['common']['bonusType']
    resultsClass = _RESULTS_MAP.get(bonusType, _DEFAULT_RESULTS)
    return resultsClass(results, dp)
