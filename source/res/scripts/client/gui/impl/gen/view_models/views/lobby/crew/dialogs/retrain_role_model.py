# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/retrain_role_model.py
from frameworks.wulf import ViewModel

class RetrainRoleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(RetrainRoleModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getIsTaken(self):
        return self._getBool(1)

    def setIsTaken(self, value):
        self._setBool(1, value)

    def getRolesCount(self):
        return self._getNumber(2)

    def setRolesCount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(RetrainRoleModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isTaken', False)
        self._addNumberProperty('rolesCount', 0)
