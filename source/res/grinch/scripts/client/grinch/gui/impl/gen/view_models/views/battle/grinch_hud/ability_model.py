# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_hud/ability_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AbilityTypeEnum(Enum):
    NONE = 'none'
    SHELLASSAULT = 'shellAssault'
    SHELLCARRIER = 'shellCarrier'
    SHELLSUPPORT = 'shellSupport'
    REPAIRKIT = 'repairKit'
    TURRET = 'turret'
    HEAL = 'heal'
    STEALTH = 'stealth'
    FLARE = 'flare'
    BLIZZARD = 'blizzard'
    RAGE = 'rage'


class AbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(AbilityModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return AbilityTypeEnum(self._getString(0))

    def setType(self, value):
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

    def getIsTargeting(self):
        return self._getBool(4)

    def setIsTargeting(self, value):
        self._setBool(4, value)

    def getIsEnabled(self):
        return self._getBool(5)

    def setIsEnabled(self, value):
        self._setBool(5, value)

    def getKeyBind(self):
        return self._getString(6)

    def setKeyBind(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(AbilityModel, self)._initialize()
        self._addStringProperty('type', AbilityTypeEnum.NONE.value)
        self._addRealProperty('reloadTimeLeft', 0.0)
        self._addRealProperty('reloadTime', 0.0)
        self._addBoolProperty('isActive', False)
        self._addBoolProperty('isTargeting', False)
        self._addBoolProperty('isEnabled', True)
        self._addStringProperty('keyBind', '')
