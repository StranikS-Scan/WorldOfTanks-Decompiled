# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_difficulty_missions_controller.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_difficulty_missions_controller import DifficultyMission
    from gui.server_events.bonuses import SimpleBonus

class ILSDifficultyMissionsController(IGameController):
    onDifficultyMissionsStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def missionsSorted(self, difficulty):
        raise NotImplementedError

    def getMission(self, missionID):
        raise NotImplementedError

    def getMissionsCount(self, difficulty):
        raise NotImplementedError

    def getCompletedMissionsIndexByDifficulty(self, difficulty):
        raise NotImplementedError

    def getIndexes(self, missionID):
        raise NotImplementedError

    def getMissionByIndex(self, difficulty, index):
        raise NotImplementedError

    def getMissionIDByIndex(self, difficulty, index):
        raise NotImplementedError

    def getAggregatedMissionRewards(self, difficulty):
        raise NotImplementedError

    def addArenaIDToCache(self, arenaID):
        raise NotImplementedError

    def isArenaIDInCache(self, arenaID):
        raise NotImplementedError
