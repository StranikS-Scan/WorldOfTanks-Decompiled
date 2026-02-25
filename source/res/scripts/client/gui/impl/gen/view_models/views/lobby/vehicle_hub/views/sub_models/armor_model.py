# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/armor_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_attacker import ArmorAttacker
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_value_model import ArmorValueModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_vehicle import ArmorVehicle

class Modes(Enum):
    NOMINAL = 'nominal'
    PENETRATION = 'penetration'
    NO_ARMOR = 'no_armor'


class DCCType(Enum):
    PENETRATION = 'penetration'
    RICOCHET = 'ricochet'
    NO_DAMAGE = 'no_damage'


class MinorShortTooltipTypes(Enum):
    MAIN_ARMOR = 'mainArmor'
    SPACED_ARMOR = 'spacedArmor'
    DEALING_DAMAGE_CHANCE = 'dealingDamageChance'
    NO_DAMAGE = 'noDamage'
    RICOCHET = 'ricochet'
    ATTACKING_CONFIGURATION = 'attackingConfiguration'


class ArmorModel(ViewModel):
    __slots__ = ('onDragModule', 'onDragStateChanged', 'onModeChanged', 'onAttackerClicked', 'onGunItemClick', 'onTurretItemClick', 'onAttackerGunItemClick', 'onAttackerShellItemClick')

    def __init__(self, properties=11, commands=8):
        super(ArmorModel, self).__init__(properties=properties, commands=commands)

    @property
    def attacker(self):
        return self._getViewModel(0)

    @staticmethod
    def getAttackerType():
        return ArmorAttacker

    @property
    def vehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getVehicleType():
        return ArmorVehicle

    def getMainArmor(self):
        return self._getArray(2)

    def setMainArmor(self, value):
        self._setArray(2, value)

    @staticmethod
    def getMainArmorType():
        return ArmorValueModel

    def getSpacedArmor(self):
        return self._getArray(3)

    def setSpacedArmor(self, value):
        self._setArray(3, value)

    @staticmethod
    def getSpacedArmorType():
        return ArmorValueModel

    def getMainGradient(self):
        return self._getResource(4)

    def setMainGradient(self, value):
        self._setResource(4, value)

    def getSpacedGradient(self):
        return self._getResource(5)

    def setSpacedGradient(self, value):
        self._setResource(5, value)

    def getPenetrationChance(self):
        return self._getArray(6)

    def setPenetrationChance(self, value):
        self._setArray(6, value)

    @staticmethod
    def getPenetrationChanceType():
        return ArmorValueModel

    def getNoDamage(self):
        return self._getArray(7)

    def setNoDamage(self, value):
        self._setArray(7, value)

    @staticmethod
    def getNoDamageType():
        return ArmorValueModel

    def getPenetrationGradient(self):
        return self._getResource(8)

    def setPenetrationGradient(self, value):
        self._setResource(8, value)

    def getDragModuleMode(self):
        return self._getBool(9)

    def setDragModuleMode(self, value):
        self._setBool(9, value)

    def getSelectedMode(self):
        return self._getString(10)

    def setSelectedMode(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(ArmorModel, self)._initialize()
        self._addViewModelProperty('attacker', ArmorAttacker())
        self._addViewModelProperty('vehicle', ArmorVehicle())
        self._addArrayProperty('mainArmor', Array())
        self._addArrayProperty('spacedArmor', Array())
        self._addResourceProperty('mainGradient', R.invalid())
        self._addResourceProperty('spacedGradient', R.invalid())
        self._addArrayProperty('penetrationChance', Array())
        self._addArrayProperty('noDamage', Array())
        self._addResourceProperty('penetrationGradient', R.invalid())
        self._addBoolProperty('dragModuleMode', False)
        self._addStringProperty('selectedMode', '')
        self.onDragModule = self._addCommand('onDragModule')
        self.onDragStateChanged = self._addCommand('onDragStateChanged')
        self.onModeChanged = self._addCommand('onModeChanged')
        self.onAttackerClicked = self._addCommand('onAttackerClicked')
        self.onGunItemClick = self._addCommand('onGunItemClick')
        self.onTurretItemClick = self._addCommand('onTurretItemClick')
        self.onAttackerGunItemClick = self._addCommand('onAttackerGunItemClick')
        self.onAttackerShellItemClick = self._addCommand('onAttackerShellItemClick')
