# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/feature/battle_results/fun_race_status.py
from frameworks.wulf import ViewModel

class FunRaceStatus(ViewModel):
    __slots__ = ()
    FINISHED = 'finished'
    NOT_FINISHED = 'notFinished'

    def __init__(self, properties=0, commands=0):
        super(FunRaceStatus, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(FunRaceStatus, self)._initialize()
