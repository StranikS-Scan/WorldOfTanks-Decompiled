# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_battle_status.py
from frameworks.wulf import ViewModel

class FunBattleStatus(ViewModel):
    __slots__ = ()
    FINISHED = 'finished'
    NOT_FINISHED = 'notFinished'

    def __init__(self, properties=0, commands=0):
        super(FunBattleStatus, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FunBattleStatus, self)._initialize()
