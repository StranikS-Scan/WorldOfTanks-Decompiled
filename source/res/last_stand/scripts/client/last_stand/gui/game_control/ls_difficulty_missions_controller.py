# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_difficulty_missions_controller.py
import typing
from collections import namedtuple
import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from constants import EVENT_CLIENT_DATA
from last_stand.gui.game_control.ls_artefacts_controller import compareBonusesByPriority
from last_stand.skeletons.ls_controller import ILSController
from last_stand.skeletons.ls_difficulty_missions_controller import ILSDifficultyMissionsController
from last_stand_common.last_stand_constants import DifficultyMissionsSettings
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
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
    eventsCache = dependency.descriptor(IEventsCache)
    lsCtrl = dependency.descriptor(ILSController)

    def __init__(self):
        super(LSDifficultyMissionsController, self).__init__()
        self.onDifficultyMissionsStatusUpdated = Event.Event()
        self._missions = {}
        self._arenaIDCacheForReopenBPS = set()

    def fini(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.eventsCache.onSyncCompleted -= self.__onSyncQuestCompleted
        self.onDifficultyMissionsStatusUpdated.clear()
        self._missions = {}
        self._arenaIDCacheForReopenBPS.clear()
        super(LSDifficultyMissionsController, self).fini()

    def onDisconnected(self):
        self._arenaIDCacheForReopenBPS.clear()

    def isEnabled(self):
        return self.__getConfig().isEnabled

    def onLobbyStarted(self, ctx):
        super(LSDifficultyMissionsController, self).onLobbyStarted(ctx)
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self.__onQuestsUpdated})
        self.eventsCache.onSyncCompleted += self.__onSyncQuestCompleted
        self._initMissions()

    def missionsSorted(self, difficulty):
        return sorted(self._missions.get(difficulty, {}).itervalues(), key=lambda item: item.index)

    def getMission(self, missionID):
        difficulty, index = self.getIndexes(missionID)
        return self._missions.get(difficulty, {}).get(index)

    def getMissionsCount(self, difficulty):
        return len(self._missions.get(difficulty, {}))

    def getCompletedMissionsIndexByDifficulty(self, difficulty):
        completedMissions = sorted((item.index for item in self._missions.get(difficulty, {}).itervalues() if item.isCompleted))
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
        for mission in self._missions.get(difficulty, {}).values():
            rewards.extend(mission.bonusRewards)

        return sorted(mergeBonuses(rewards), cmp=compareBonusesByPriority)

    def addArenaIDToCache(self, arenaID):
        self._arenaIDCacheForReopenBPS.add(arenaID)

    def isArenaIDInCache(self, arenaID):
        return arenaID in self._arenaIDCacheForReopenBPS

    def _initMissions(self):
        quests = self.eventsCache.getAllQuests(lambda q: isDifficultyMissionQuest(q.getID()))
        self._missions.clear()
        for questID, quest in quests.iteritems():
            difficulty, index = self.getIndexes(questID)
            mission = DifficultyMission(missionID=questID, bonusRewards=self.__getMissionBonuses(quest), difficulty=difficulty, index=index, isCompleted=quest.isCompleted())
            self._missions.setdefault(difficulty, {})[index] = mission

    def __getMissionBonuses(self, quest):
        return sorted(quest.getBonuses(), cmp=compareBonusesByPriority) if quest else []

    def __getConfig(self):
        return self.lsCtrl.getModeSettings()

    def __onQuestsUpdated(self, _):
        self._initMissions()
        self.onDifficultyMissionsStatusUpdated()

    def __onSyncQuestCompleted(self):
        self._initMissions()
        self.onDifficultyMissionsStatusUpdated()
