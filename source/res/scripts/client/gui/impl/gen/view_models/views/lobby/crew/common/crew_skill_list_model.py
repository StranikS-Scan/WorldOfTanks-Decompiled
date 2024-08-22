# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_skill_list_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_model import CrewSkillModel

class CrewSkillListModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CrewSkillListModel, self).__init__(properties=properties, commands=commands)

    def getMajorSkills(self):
        return self._getArray(0)

    def setMajorSkills(self, value):
        self._setArray(0, value)

    @staticmethod
    def getMajorSkillsType():
        return CrewSkillModel

    def getBonusSkills(self):
        return self._getArray(1)

    def setBonusSkills(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusSkillsType():
        return CrewSkillModel

    def getSkillsEfficiency(self):
        return self._getReal(2)

    def setSkillsEfficiency(self, value):
        self._setReal(2, value)

    def _initialize(self):
        super(CrewSkillListModel, self)._initialize()
        self._addArrayProperty('majorSkills', Array())
        self._addArrayProperty('bonusSkills', Array())
        self._addRealProperty('skillsEfficiency', 0.0)
