# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_rewards_vehicle_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class ArmoryYardRewardsVehicleModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(ArmoryYardRewardsVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIndex(self):
        return self._getNumber(10)

    def setIndex(self, value):
        self._setNumber(10, value)

    def getVehicleImg(self):
        return self._getString(11)

    def setVehicleImg(self, value):
        self._setString(11, value)

    def getTooltipId(self):
        return self._getString(12)

    def setTooltipId(self, value):
        self._setString(12, value)

    def getTooltipContentId(self):
        return self._getString(13)

    def setTooltipContentId(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(ArmoryYardRewardsVehicleModel, self)._initialize()
        self._addNumberProperty('index', 0)
        self._addStringProperty('vehicleImg', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
