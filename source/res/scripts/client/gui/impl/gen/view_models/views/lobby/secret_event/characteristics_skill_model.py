# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/characteristics_skill_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CharacteristicsSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CharacteristicsSkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getSkillName(self):
        return self._getString(4)

    def setSkillName(self, value):
        self._setString(4, value)

    def getSkillDescription(self):
        return self._getString(5)

    def setSkillDescription(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(CharacteristicsSkillModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isEnabled', False)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('skillName', '')
        self._addStringProperty('skillDescription', '')
