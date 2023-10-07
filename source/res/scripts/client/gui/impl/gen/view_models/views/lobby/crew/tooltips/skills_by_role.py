# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/skills_by_role.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class SkillsByRole(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(SkillsByRole, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(0)

    def setRole(self, value):
        self._setString(0, value)

    def getSkills(self):
        return self._getArray(1)

    def setSkills(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSkillsType():
        return unicode

    def _initialize(self):
        super(SkillsByRole, self)._initialize()
        self._addStringProperty('role', '')
        self._addArrayProperty('skills', Array())
