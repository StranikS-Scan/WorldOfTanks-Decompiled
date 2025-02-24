# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_ability_tooltip_model.py
from frameworks.wulf import ViewModel

class VehicleAbilityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(VehicleAbilityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAbilityName(self):
        return self._getString(0)

    def setAbilityName(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getCooldown(self):
        return self._getNumber(3)

    def setCooldown(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(VehicleAbilityTooltipModel, self)._initialize()
        self._addStringProperty('abilityName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('cooldown', 0)
