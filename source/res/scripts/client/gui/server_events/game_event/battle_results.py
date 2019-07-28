# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/battle_results.py
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from wotdecorators import condition
from gui.server_events import conditions
_QUEST_BATTLE_RESULTS_WIN_PREFIX = 'se1_general_battle_progress_win_'
_QUEST_BATTLE_RESULTS_LOSE_PREFIX = 'se1_general_battle_progress_lose_'
_GENERAL_PROGRESS_POINTS = 'se1_2019_general_event_points'
_DEFAULT_BATTLE_RESULTS_KEY = 'damageDealt'

class BattleResults(object):
    eventsCache = dependency.descriptor(IEventsCache)
    ifStarted = condition('_started')

    def __init__(self):
        super(BattleResults, self).__init__()
        self._started = False

    def start(self):
        self._started = True

    @ifStarted
    def stop(self):
        self._started = False

    def getWinPoints(self):
        points = self._getPointsFrom(self._getWinBattleResultQuest())
        return points

    def getLosePoints(self):
        points = self._getPointsFrom(self._getLoseBattleResultQuest())
        return points

    def getBattleResultsKey(self):
        return self._getBattleResultsKeyrom(self._getWinBattleResultQuest())

    def _getBattleResultsKeyrom(self, quests):
        if quests:
            q = quests[0]
            for item in q.postBattleCond.getConditions().items:
                if isinstance(item, conditions.BattleResults):
                    return item.keyName

        return _DEFAULT_BATTLE_RESULTS_KEY

    def _getPointsFrom(self, quests):
        return [ self._getEventPointsFromQuest(q, 0) for q in quests ]

    def _getEventPointsFromQuest(self, q, default=None):
        for tokenBonus in q.getBonuses('tokens'):
            tokens = tokenBonus.getTokens()
            if _GENERAL_PROGRESS_POINTS in tokens:
                return tokens[_GENERAL_PROGRESS_POINTS].count

        return default

    def _getWinBattleResultQuest(self):
        return self._getBattleResultsQuest(_QUEST_BATTLE_RESULTS_WIN_PREFIX)

    def _getLoseBattleResultQuest(self):
        return self._getBattleResultsQuest(_QUEST_BATTLE_RESULTS_LOSE_PREFIX)

    def _getBattleResultsQuest(self, prefix):
        return sorted(self.eventsCache.getHiddenQuests(lambda q: q.getID().startswith(prefix)).itervalues(), key=lambda q: int(q.getID().split('_')[-1]))
