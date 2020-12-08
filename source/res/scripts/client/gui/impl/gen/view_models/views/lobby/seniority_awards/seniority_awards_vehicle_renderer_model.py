# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_vehicle_renderer_model.py
from frameworks.wulf import ViewModel

class SeniorityAwardsVehicleRendererModel(ViewModel):
    __slots__ = ()
    TOOLTIP_VEHICLE_REWARD = 'TOOLTIP_VEHICLE_REWARD'

    def __init__(self, properties=2, commands=0):
        super(SeniorityAwardsVehicleRendererModel, self).__init__(properties=properties, commands=commands)

    def getVehicleCD(self):
        return self._getString(0)

    def setVehicleCD(self, value):
        self._setString(0, value)

    def getImgSource(self):
        return self._getString(1)

    def setImgSource(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(SeniorityAwardsVehicleRendererModel, self)._initialize()
        self._addStringProperty('vehicleCD', '')
        self._addStringProperty('imgSource', '')
