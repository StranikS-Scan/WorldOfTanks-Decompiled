# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_difficulty_missions_controller.py
from __future__ import absolute_import
import typing
from collections import namedtuple
from future.utils import viewitems, viewvalues
import Event
from last_stand.gui.game_control.ls_artefacts_controller import getBonusPriority
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
from last_stand.skeletons.ls_quests_ui_cache import ILSQuestsUICache
from last_stand_common.last_stand_constants import DifficultyMissionsSettings
from helpers import dependency
from gui.server_events.bonuses import mergeBonuses
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import Quest
    from gui.server_events.bonuses import SimpleBonus

class DifficultyMission(namedtuple('DifficultyMission', ('missionID', 'bonusRewards', 'difficulty', 'index', 'isCompleted'))):

    def getCtx(self):
        return dict(self._asdict())


def isDifficultyMissionQuest(qID):
    return qID.startswith(DifficultyMissionsSettings.DIFFICULTY_MISSISONS_QUEST_PREFFIX)


def getFormattedMissionsList(missionsIdx):
    return '|'.join((str(idx - 1) for idx in missionsIdx))


class LSDifficultyMissionsController(ILSDifficultyMissionsController):
    lsCtrl = dependency.descriptor(ILSController)
    questsCache = dependency.descriptor(ILSQuestsUICache)

    def __init__(self):
        super(LSDifficultyMissionsController, self).__init__()
        self.onDifficultyMissionsStatusUpdated = Event.Event()
        self._missions = {}
        self._arenaIDCacheForReopenBPS = set()

    def init(self):
        super(LSDifficultyMissionsController, self).init()
        self.questsCache.onCacheUpdated += self.__onQuestsUpdated
        self.questsCache.onSyncCompleted += self.__onSyncQuestCompleted

    def fini(self):
        self.questsCache.onCacheUpdated -= self.__onQuestsUpdated
        self.questsCache.onSyncCompleted -= self.__onSyncQuestCompleted
        self.onDifficultyMissionsStatusUpdated.clear()
        self._missions = {}
        self._arenaIDCacheForReopenBPS.clear()
        super(LSDifficultyMissionsController, self).fini()

    def onDisconnected(self):
        self._arenaIDCacheForReopenBPS.clear()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def missionsSorted(self, difficulty):
        return sorted(viewvalues(self._missions.get(difficulty, {})), key=lambda item: item.index)

    def isProgressCompleted(self):
        return all((mission.isCompleted for difficultyMissions in viewvalues(self._missions) for mission in viewvalues(difficultyMissions)))

    def getMission(self, missionID):
        difficulty, index = self.getIndexes(missionID)
        return self._missions.get(difficulty, {}).get(index)

    def getMissionsCount(self, difficulty):
        return len(self._missions.get(difficulty, {}))

    def getCompletedMissionsIndexByDifficulty(self, difficulty):
        completedMissions = sorted((item.index for item in viewvalues(self._missions.get(difficulty, {})) if item.isCompleted))
        return completedMissions

    def getMissionByIndex(self, difficulty, index):
        return self._missions.get(difficulty, {}).get(index)

    def getMissionIDByIndex(self, difficulty, index):
        return DifficultyMissionsSettings.DIFFICULTY_MISSISONS_QUEST_TPL.format(difficulty=difficulty, index=index)

    def getIndexes(self, missionID):
        _, difficulty, index = missionID.split(':')
        return (int(difficulty), int(index))

    def getAggregatedMissionRewards(self, difficulty):
        rewards = []
        for mission in viewvalues(self._missions.get(difficulty, {})):
            rewards.extend(mission.bonusRewards)

        return sorted(mergeBonuses(rewards), key=getBonusPriority)

    def addArenaIDToCache(self, arenaID):
        self._arenaIDCacheForReopenBPS.add(arenaID)

    def isArenaIDInCache(self, arenaID):
        return arenaID in self._arenaIDCacheForReopenBPS

    def _initMissions(self):
        quests = self.questsCache.getQuests(lambda q: isDifficultyMissionQuest(q.getID()))
        self._missions.clear()
        for questID, quest in viewitems(quests):
            difficulty, index = self.getIndexes(questID)
            mission = DifficultyMission(missionID=questID, bonusRewards=self.__getMissionBonuses(quest), difficulty=difficulty, index=index, isCompleted=quest.isCompleted())
            self._missions.setdefault(difficulty, {})[index] = mission

    def __getMissionBonuses(self, quest):
        return sorted(quest.getBonuses(), key=getBonusPriority) if quest else []

    def __getConfig(self):
        return self.lsCtrl.getModeSettings()

    def __onQuestsUpdated(self):
        self._initMissions()
        self.onDifficultyMissionsStatusUpdated()

    def __onSyncQuestCompleted(self):
        self._initMissions()
        self.onDifficultyMissionsStatusUpdated()
