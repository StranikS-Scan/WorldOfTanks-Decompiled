# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/battle_result_team_member_model.py
from halloween.gui.impl.gen.view_models.views.lobby.common.base_team_member_model import BaseTeamMemberModel

class BattleResultTeamMemberModel(BaseTeamMemberModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(BattleResultTeamMemberModel, self).__init__(properties=properties, commands=commands)

    def getIsEnemyTeam(self):
        return self._getBool(9)

    def setIsEnemyTeam(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(BattleResultTeamMemberModel, self)._initialize()
        self._addBoolProperty('isEnemyTeam', False)
