# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/role_change_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.retrain_role_model import RetrainRoleModel

class DisableState(Enum):
    AVAILABLE = 'available'
    FORCED = 'forced'
    CREWLOCK = 'crewLock'
    FREEOPERATION = 'freeOperation'


class RoleChangeModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RoleChangeModel, self).__init__(properties=properties, commands=commands)

    def getIsVisible(self):
        return self._getBool(0)

    def setIsVisible(self, value):
        self._setBool(0, value)

    def getIsChecked(self):
        return self._getBool(1)

    def setIsChecked(self, value):
        self._setBool(1, value)

    def getSelectedIdx(self):
        return self._getNumber(2)

    def setSelectedIdx(self, value):
        self._setNumber(2, value)

    def getDisableState(self):
        return DisableState(self._getString(3))

    def setDisableState(self, value):
        self._setString(3, value.value)

    def getRoles(self):
        return self._getArray(4)

    def setRoles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRolesType():
        return RetrainRoleModel

    def _initialize(self):
        super(RoleChangeModel, self)._initialize()
        self._addBoolProperty('isVisible', False)
        self._addBoolProperty('isChecked', False)
        self._addNumberProperty('selectedIdx', 0)
        self._addStringProperty('disableState')
        self._addArrayProperty('roles', Array())
