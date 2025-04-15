# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/team_stats_column_types.py
from frameworks.wulf import ViewModel

class TeamStatsColumnTypes(ViewModel):
    __slots__ = ()
    SQUAD = 'squad'
    PLAYER = 'player'
    DAMAGE = 'damage'
    FRAG = 'frag'
    XP = 'xp'
    VEHICLE = 'tank'

    def __init__(self, properties=0, commands=0):
        super(TeamStatsColumnTypes, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(TeamStatsColumnTypes, self)._initialize()
