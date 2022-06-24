# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/views/team_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.user_model import UserModel

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

    @staticmethod
    def getUsersType():
        return UserModel

    def _initialize(self):
        super(TeamModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('users', Array())
