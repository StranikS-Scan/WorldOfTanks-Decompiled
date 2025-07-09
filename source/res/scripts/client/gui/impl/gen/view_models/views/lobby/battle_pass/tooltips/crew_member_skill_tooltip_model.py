# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/crew_member_skill_tooltip_model.py
from frameworks.wulf import ViewModel

class CrewMemberSkillTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CrewMemberSkillTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIsZero(self):
        return self._getBool(1)

    def setIsZero(self, value):
        self._setBool(1, value)

    def getHasZeroPerk(self):
        return self._getBool(2)

    def setHasZeroPerk(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CrewMemberSkillTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addBoolProperty('isZero', False)
        self._addBoolProperty('hasZeroPerk', False)
