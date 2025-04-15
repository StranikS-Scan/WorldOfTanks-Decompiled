# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/division_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_ability_model import DivisionAbilityModel

class DivisionModel(ViewModel):
    __slots__ = ('onVehicleChanged',)

    def __init__(self, properties=4, commands=1):
        super(DivisionModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getVehicleType(self):
        return self._getString(1)

    def setVehicleType(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getAbilities(self):
        return self._getArray(3)

    def setAbilities(self, value):
        self._setArray(3, value)

    @staticmethod
    def getAbilitiesType():
        return DivisionAbilityModel

    def _initialize(self):
        super(DivisionModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('level', 0)
        self._addArrayProperty('abilities', Array())
        self.onVehicleChanged = self._addCommand('onVehicleChanged')
