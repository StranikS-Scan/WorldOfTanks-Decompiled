# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/division_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_ability_model import DivisionAbilityModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.division_vehicle_model import DivisionVehicleModel

class DivisionLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(DivisionLevelModel, self).__init__(properties=properties, commands=commands)

    def getExperience(self):
        return self._getNumber(0)

    def setExperience(self, value):
        self._setNumber(0, value)

    def getVehicles(self):
        return self._getArray(1)

    def setVehicles(self, value):
        self._setArray(1, value)

    @staticmethod
    def getVehiclesType():
        return DivisionVehicleModel

    def getAbilities(self):
        return self._getArray(2)

    def setAbilities(self, value):
        self._setArray(2, value)

    @staticmethod
    def getAbilitiesType():
        return DivisionAbilityModel

    def _initialize(self):
        super(DivisionLevelModel, self)._initialize()
        self._addNumberProperty('experience', 0)
        self._addArrayProperty('vehicles', Array())
        self._addArrayProperty('abilities', Array())
