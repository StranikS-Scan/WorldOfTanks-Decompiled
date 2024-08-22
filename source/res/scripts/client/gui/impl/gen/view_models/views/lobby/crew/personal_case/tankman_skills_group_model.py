# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/tankman_skills_group_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.tankman_skill_model import TankmanSkillModel

class TankmanSkillsGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TankmanSkillsGroupModel, self).__init__(properties=properties, commands=commands)

    def getRole(self):
        return self._getString(0)

    def setRole(self, value):
        self._setString(0, value)

    def getDirectiveId(self):
        return self._getNumber(1)

    def setDirectiveId(self, value):
        self._setNumber(1, value)

    def getDirectiveName(self):
        return self._getString(2)

    def setDirectiveName(self, value):
        self._setString(2, value)

    def getSelectedSkillsCount(self):
        return self._getNumber(3)

    def setSelectedSkillsCount(self, value):
        self._setNumber(3, value)

    def getSkills(self):
        return self._getArray(4)

    def setSkills(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSkillsType():
        return TankmanSkillModel

    def _initialize(self):
        super(TankmanSkillsGroupModel, self)._initialize()
        self._addStringProperty('role', '')
        self._addNumberProperty('directiveId', 0)
        self._addStringProperty('directiveName', '')
        self._addNumberProperty('selectedSkillsCount', 0)
        self._addArrayProperty('skills', Array())
