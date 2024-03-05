# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/ability_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Ability(Enum):
    NONE = 'none'
    SHELL = 'shell'
    ACCELERATION = 'acceleration'
    SHIELD = 'shield'
    BLACK_HOLE = 'black_hole'
    OVERCHARGE = 'overcharge'
    RAPID_SHELLING = 'rapid_shelling'
    POWER_SHOT = 'power_shot'


class AbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(AbilityModel, self).__init__(properties=properties, commands=commands)

    def getAbility(self):
        return Ability(self._getString(0))

    def setAbility(self, value):
        self._setString(0, value.value)

    def getReloadTimeLeft(self):
        return self._getReal(1)

    def setReloadTimeLeft(self, value):
        self._setReal(1, value)

    def getReloadTime(self):
        return self._getReal(2)

    def setReloadTime(self, value):
        self._setReal(2, value)

    def getIsActive(self):
        return self._getBool(3)

    def setIsActive(self, value):
        self._setBool(3, value)

    def getIsEnabled(self):
        return self._getBool(4)

    def setIsEnabled(self, value):
        self._setBool(4, value)

    def getKeyBind(self):
        return self._getString(5)

    def setKeyBind(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(AbilityModel, self)._initialize()
        self._addStringProperty('ability', Ability.NONE.value)
        self._addRealProperty('reloadTimeLeft', 0.0)
        self._addRealProperty('reloadTime', 0.0)
        self._addBoolProperty('isActive', False)
        self._addBoolProperty('isEnabled', True)
        self._addStringProperty('keyBind', '')
