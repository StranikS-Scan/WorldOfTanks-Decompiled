# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/special_vehicle_param_model.py
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_param_view_model import VehicleParamViewModel

class SpecialVehicleParamModel(VehicleParamViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(SpecialVehicleParamModel, self).__init__(properties=properties, commands=commands)

    def getTemplate(self):
        return self._getString(7)

    def setTemplate(self, value):
        self._setString(7, value)

    def getMeasureUnit(self):
        return self._getString(8)

    def setMeasureUnit(self, value):
        self._setString(8, value)

    def _initialize(self):
        super(SpecialVehicleParamModel, self)._initialize()
        self._addStringProperty('template', '')
        self._addStringProperty('measureUnit', '')
