# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/skills_efficiency_tooltip_model.py
from frameworks.wulf import ViewModel

class SkillsEfficiencyTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SkillsEfficiencyTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPercent(self):
        return self._getReal(0)

    def setPercent(self, value):
        self._setReal(0, value)

    def getCurrentXP(self):
        return self._getNumber(1)

    def setCurrentXP(self, value):
        self._setNumber(1, value)

    def getMaxXP(self):
        return self._getNumber(2)

    def setMaxXP(self, value):
        self._setNumber(2, value)

    def getIsDiscountInformationVisible(self):
        return self._getBool(3)

    def setIsDiscountInformationVisible(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SkillsEfficiencyTooltipModel, self)._initialize()
        self._addRealProperty('percent', 0.0)
        self._addNumberProperty('currentXP', 0)
        self._addNumberProperty('maxXP', 0)
        self._addBoolProperty('isDiscountInformationVisible', False)
