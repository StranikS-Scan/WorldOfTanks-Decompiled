# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_efficiency_param.py
from frameworks.wulf import ViewModel

class FunEfficiencyParam(ViewModel):
    __slots__ = ()
    FINISH_TIME = 'finishTime'
    FINISH_POSITION = 'finishPosition'
    CHECKPOINTS_PASSED = 'checkpointsPassed'
    DESTROYED = 'kills'
    DEATH_COUNT = 'deathCount'

    def __init__(self, properties=0, commands=0):
        super(FunEfficiencyParam, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FunEfficiencyParam, self)._initialize()
