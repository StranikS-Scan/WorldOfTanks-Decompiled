# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class PrebattleVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(PrebattleVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIsFavorite(self):
        return self._getBool(9)

    def setIsFavorite(self, value):
        self._setBool(9, value)

    def getIsSelected(self):
        return self._getBool(10)

    def setIsSelected(self, value):
        self._setBool(10, value)

    def getIsVisible(self):
        return self._getBool(11)

    def setIsVisible(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(PrebattleVehicleModel, self)._initialize()
        self._addBoolProperty('isFavorite', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isVisible', True)
