# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/tooltips/ability_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AbilityType(Enum):
    ABILITY = 'ability'
    GUN = 'gun'


class AbilityTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(AbilityTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getAbilityType(self):
        return AbilityType(self._getString(1))

    def setAbilityType(self, value):
        self._setString(1, value.value)

    def getKeyString(self):
        return self._getString(2)

    def setKeyString(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getRadius(self):
        return self._getNumber(4)

    def setRadius(self, value):
        self._setNumber(4, value)

    def getDuration(self):
        return self._getNumber(5)

    def setDuration(self, value):
        self._setNumber(5, value)

    def getDebuffDuration(self):
        return self._getNumber(6)

    def setDebuffDuration(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(AbilityTooltipViewModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('abilityType', AbilityType.ABILITY.value)
        self._addStringProperty('keyString', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('radius', 0)
        self._addNumberProperty('duration', 0)
        self._addNumberProperty('debuffDuration', 0)
