# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/role_skill_slot_model.py
from frameworks.wulf import ViewModel

class RoleSkillSlotModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(RoleSkillSlotModel, self).__init__(properties=properties, commands=commands)

    def getRoleSkill(self):
        return self._getString(0)

    def setRoleSkill(self, value):
        self._setString(0, value)

    def getIntCD(self):
        return self._getNumber(1)

    def setIntCD(self, value):
        self._setNumber(1, value)

    def getRoleName(self):
        return self._getString(2)

    def setRoleName(self, value):
        self._setString(2, value)

    def getCanSwitch(self):
        return self._getBool(3)

    def setCanSwitch(self, value):
        self._setBool(3, value)

    def getIsPopoverOpen(self):
        return self._getBool(4)

    def setIsPopoverOpen(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(RoleSkillSlotModel, self)._initialize()
        self._addStringProperty('roleSkill', '')
        self._addNumberProperty('intCD', 0)
        self._addStringProperty('roleName', '')
        self._addBoolProperty('canSwitch', True)
        self._addBoolProperty('isPopoverOpen', False)
        self.onClick = self._addCommand('onClick')
