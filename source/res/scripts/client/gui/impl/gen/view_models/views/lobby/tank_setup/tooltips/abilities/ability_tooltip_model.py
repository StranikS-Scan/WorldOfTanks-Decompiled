# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/tooltips/abilities/ability_tooltip_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.bonuses_model import BonusesModel

class AbilityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(AbilityTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusesType():
        return BonusesModel

    def getVehicleIntCD(self):
        return self._getNumber(1)

    def setVehicleIntCD(self, value):
        self._setNumber(1, value)

    def getReuseCount(self):
        return self._getNumber(2)

    def setReuseCount(self, value):
        self._setNumber(2, value)

    def getDuration(self):
        return self._getNumber(3)

    def setDuration(self, value):
        self._setNumber(3, value)

    def getCooldown(self):
        return self._getNumber(4)

    def setCooldown(self, value):
        self._setNumber(4, value)

    def getIconName(self):
        return self._getString(5)

    def setIconName(self, value):
        self._setString(5, value)

    def getUserString(self):
        return self._getString(6)

    def setUserString(self, value):
        self._setString(6, value)

    def getDescription(self):
        return self._getString(7)

    def setDescription(self, value):
        self._setString(7, value)

    def getLightAdditional(self):
        return self._getBool(8)

    def setLightAdditional(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(AbilityTooltipModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addNumberProperty('vehicleIntCD', 0)
        self._addNumberProperty('reuseCount', 0)
        self._addNumberProperty('duration', 0)
        self._addNumberProperty('cooldown', 0)
        self._addStringProperty('iconName', '')
        self._addStringProperty('userString', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('lightAdditional', True)
