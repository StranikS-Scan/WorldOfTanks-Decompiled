# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/lobby/difficulty_hint_checker.py
from helpers import dependency
from shared_utils import first
from story_mode.skeletons.story_mode_controller import IStoryModeController
from story_mode_common.story_mode_constants import MissionType

class DifficultyHintChecker(object):

    def check(self, _):
        storyModeCtrl = dependency.instance(IStoryModeController)
        for mission in storyModeCtrl.filterMissions(missionType=MissionType.EVENT):
            if mission.unlockMission:
                lockingMission = storyModeCtrl.missions.getMission(mission.unlockMission)
                firstTask = first(lockingMission.tasks) if lockingMission is not None else None
                if firstTask is not None and storyModeCtrl.isMissionTaskCompleted(mission.unlockMission, firstTask.id):
                    return True

        return False
