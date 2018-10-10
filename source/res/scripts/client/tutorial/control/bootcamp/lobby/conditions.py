# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/bootcamp/lobby/conditions.py
from tutorial.data.conditions import CONDITION_TYPE, CONDITION_STATE, ActiveCondition

class BOOTCAMP_CONDITION_TYPE(object):
    CHECKPOINT_REACHED = CONDITION_TYPE.FIRST_CUSTOM + 0


class CheckpointReachedCondition(ActiveCondition):

    def __init__(self, entityID, state=CONDITION_STATE.ACTIVE):
        super(CheckpointReachedCondition, self).__init__(entityID, BOOTCAMP_CONDITION_TYPE.CHECKPOINT_REACHED, state)
