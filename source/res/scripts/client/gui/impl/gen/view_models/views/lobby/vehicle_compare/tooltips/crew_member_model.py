# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_compare/tooltips/crew_member_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CrewMemberModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CrewMemberModel, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(0)

    def setRole(self, value):
        self._setString(0, value)

    def getAdditionalRoles(self):
        return self._getArray(1)

    def setAdditionalRoles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getAdditionalRolesType():
        return unicode

    def _initialize(self):
        super(CrewMemberModel, self)._initialize()
        self._addStringProperty('role', '')
        self._addArrayProperty('additionalRoles', Array())
