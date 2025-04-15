# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_battle_type.py
from frameworks.wulf import ViewModel

class FunBattleType(ViewModel):
    __slots__ = ()
    STANDARD = 'standard'
    RACE = 'race'

    def __init__(self, properties=0, commands=0):
        super(FunBattleType, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FunBattleType, self)._initialize()
