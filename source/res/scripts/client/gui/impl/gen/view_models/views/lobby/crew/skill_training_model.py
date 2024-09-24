# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/skill_training_model.py
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_extended_model import SkillExtendedModel

class SkillTrainingModel(SkillExtendedModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(SkillTrainingModel, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(8)

    def setIsSelected(self, value):
        self._setBool(8, value)

    def getIsLearned(self):
        return self._getBool(9)

    def setIsLearned(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(SkillTrainingModel, self)._initialize()
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isLearned', False)
