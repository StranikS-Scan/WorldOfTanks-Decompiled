# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/role_skill_slot_model.py
from frameworks.wulf import ViewModel

class RoleSkillSlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RoleSkillSlotModel, self).__init__(properties=properties, commands=commands)

    def getRoleSkill(self):
        return self._getString(0)

    def setRoleSkill(self, value):
        self._setString(0, value)

    def getRoleName(self):
        return self._getString(1)

    def setRoleName(self, value):
        self._setString(1, value)

    def getTooltipId(self):
        return self._getString(2)

    def setTooltipId(self, value):
        self._setString(2, value)

    def getTooltipHeader(self):
        return self._getString(3)

    def setTooltipHeader(self, value):
        self._setString(3, value)

    def getTooltipBody(self):
        return self._getString(4)

    def setTooltipBody(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RoleSkillSlotModel, self)._initialize()
        self._addStringProperty('roleSkill', '')
        self._addStringProperty('roleName', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipHeader', '')
        self._addStringProperty('tooltipBody', '')
