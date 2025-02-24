# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/skill/skill_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.crew.common.skill.skill_simple_model import SkillSimpleModel

class BattleBooster(Enum):
    NONE = 'none'
    LEARNED = 'learned'
    IMPROVED = 'Improved'


class SkillModel(SkillSimpleModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getIsZero(self):
        return self._getBool(4)

    def setIsZero(self, value):
        self._setBool(4, value)

    def getIsIrrelevant(self):
        return self._getBool(5)

    def setIsIrrelevant(self, value):
        self._setBool(5, value)

    def getBattleBooster(self):
        return BattleBooster(self._getString(6))

    def setBattleBooster(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addBoolProperty('isZero', False)
        self._addBoolProperty('isIrrelevant', False)
        self._addStringProperty('battleBooster', BattleBooster.NONE.value)
