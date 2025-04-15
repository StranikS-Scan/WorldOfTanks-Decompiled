# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/win_status_constants.py
from frameworks.wulf import ViewModel

class WinStatusConstants(ViewModel):
    __slots__ = ()
    WIN = 'win'
    DRAW = 'tie'
    LOSE = 'lose'

    def __init__(self, properties=0, commands=0):
        super(WinStatusConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(WinStatusConstants, self)._initialize()
