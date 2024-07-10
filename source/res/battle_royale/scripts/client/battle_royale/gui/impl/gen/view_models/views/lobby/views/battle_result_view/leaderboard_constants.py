# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/battle_result_view/leaderboard_constants.py
from frameworks.wulf import ViewModel

class LeaderboardConstants(ViewModel):
    __slots__ = ()
    ROW_TYPE_BR_PLAYER = 'rowBrPlayer'
    ROW_TYPE_BR_ENEMY = 'rowBrEnemy'

    def __init__(self, properties=0, commands=0):
        super(LeaderboardConstants, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(LeaderboardConstants, self)._initialize()
