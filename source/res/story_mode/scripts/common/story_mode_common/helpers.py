# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/helpers.py
from story_mode_common.configs.story_mode_missions import MissionModel
from story_mode_common.story_mode_constants import LONG_INT_HALF_SHIFT

def isTaskCompleted(progress, missionId, taskId):
    return bool(progress.get(missionId, 0) & taskBitMask(taskId))


def isMissionCompleted(progress, missionModel):
    missionProgress = progress.get(missionModel.missionId, 0)
    return missionProgress and all((missionProgress & taskBitMask(task.id) for task in missionModel.tasks))


def taskBitMask(taskId):
    return 1 << taskId - 1


def getRewardActionSetId(missionId, taskId=0):
    return missionId << LONG_INT_HALF_SHIFT | taskId
