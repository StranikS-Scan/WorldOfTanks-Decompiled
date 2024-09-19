# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/events/ranked/result_state.py
from frameworks.wulf import ViewModel

class ResultState(ViewModel):
    __slots__ = ()
    STAGE = 'stage'
    RANK = 'rank'
    RANK_LOST = 'rank_lost'
    DIVISION = 'division'
    LEAGUE = 'league'

    def __init__(self, properties=0, commands=0):
        super(ResultState, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ResultState, self)._initialize()
