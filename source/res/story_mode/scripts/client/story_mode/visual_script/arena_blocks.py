# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/visual_script/arena_blocks.py
from story_mode_common.story_mode_constants import UNDEFINED_MISSION_ID, MissionsDifficulty
from visual_script import ASPECT
from visual_script.arena_blocks import ArenaMeta
from visual_script.block import Block
from visual_script.dependency import dependencyImporter
from visual_script.slot_types import SLOT_TYPE
story_mode_missions = dependencyImporter('story_mode_common.configs.story_mode_missions')

class GetStoryModeDifficulty(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetStoryModeDifficulty, self).__init__(*args, **kwargs)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._result = self._makeDataOutputSlot('result', SLOT_TYPE.STR, self._getResult)

    def _getResult(self):
        difficulty = MissionsDifficulty.UNDEFINED.value
        missionId = self._arena.getValue().extraData.get('missionId', UNDEFINED_MISSION_ID)
        if missionId != UNDEFINED_MISSION_ID:
            missionSettings = story_mode_missions.missionsSchema.getModel()
            if missionSettings is not None:
                mission = missionSettings.getMission(missionId)
                if mission is not None:
                    difficulty = mission.difficulty.value
        self._result.setValue(difficulty)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]
