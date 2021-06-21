# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/role_model.py
from frameworks.wulf import ViewModel

class RoleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RoleModel, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(0)

    def setRole(self, value):
        self._setString(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RoleModel, self)._initialize()
        self._addStringProperty('role', '')
        self._addNumberProperty('id', 0)
