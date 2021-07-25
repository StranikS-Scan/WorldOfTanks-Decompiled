# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/skill_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.skill_base_model import SkillBaseModel

class SkillModel(SkillBaseModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getSkillPercent(self):
        return self._getNumber(2)

    def setSkillPercent(self, value):
        self._setNumber(2, value)

    def getIsAllocated(self):
        return self._getBool(3)

    def setIsAllocated(self, value):
        self._setBool(3, value)

    def getType(self):
        return self._getString(4)

    def setType(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addNumberProperty('skillPercent', 0)
        self._addBoolProperty('isAllocated', False)
        self._addStringProperty('type', '')
