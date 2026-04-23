# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/banned_vehicle_model.py
from comp7.gui.impl.gen.view_models.views.battle.comp7_vehicle_model import Comp7VehicleModel

class BannedVehicleModel(Comp7VehicleModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(BannedVehicleModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(12)

    def setCount(self, value):
        self._setNumber(12, value)

    def _initialize(self):
        super(BannedVehicleModel, self)._initialize()
        self._addNumberProperty('count', 0)
