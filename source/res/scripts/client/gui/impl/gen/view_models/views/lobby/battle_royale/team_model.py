# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/team_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.user_model import UserModel

class TeamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TeamModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getUsers(self):
        return self._getArray(1)

    def setUsers(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(TeamModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('users', Array())
