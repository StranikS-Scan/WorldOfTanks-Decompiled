# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/ranked/stage_state.py
from frameworks.wulf import ViewModel

class StageState(ViewModel):
    __slots__ = ()
    STAGES_BONUS = 'stage4_bonus'
    STAGES = 'stage2_green'
    STAGE_BONUS = 'stage2_bonus'
    STAGE = 'stage_green'
    STAGE_LOST = 'stage_red'
    STAGE_IDLE = 'stage_grey'

    def __init__(self, properties=0, commands=0):
        super(StageState, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(StageState, self)._initialize()
