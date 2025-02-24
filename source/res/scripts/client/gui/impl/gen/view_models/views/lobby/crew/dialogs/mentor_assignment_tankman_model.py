# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/mentor_assignment_tankman_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_model import CrewSkillModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_tankman_base_model import DialogTankmanBaseModel

class MentorAssignmentTankmanModel(DialogTankmanBaseModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(MentorAssignmentTankmanModel, self).__init__(properties=properties, commands=commands)

    def getUserName(self):
        return self._getString(6)

    def setUserName(self, value):
        self._setString(6, value)

    def getMajorSkills(self):
        return self._getArray(7)

    def setMajorSkills(self, value):
        self._setArray(7, value)

    @staticmethod
    def getMajorSkillsType():
        return CrewSkillModel

    def _initialize(self):
        super(MentorAssignmentTankmanModel, self)._initialize()
        self._addStringProperty('userName', '')
        self._addArrayProperty('majorSkills', Array())
