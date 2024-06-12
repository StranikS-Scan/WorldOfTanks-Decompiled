# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_rewards_vehicle_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class EarlyAccessRewardsVehicleModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(EarlyAccessRewardsVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(8)

    def setIndex(self, value):
        self._setNumber(8, value)

    def getVehicleImg(self):
        return self._getString(9)

    def setVehicleImg(self, value):
        self._setString(9, value)

    def getTooltipId(self):
        return self._getString(10)

    def setTooltipId(self, value):
        self._setString(10, value)

    def getTooltipContentId(self):
        return self._getString(11)

    def setTooltipContentId(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(EarlyAccessRewardsVehicleModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('vehicleImg', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
