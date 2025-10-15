# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/vehicle_bonus_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class VehicleBonusModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(9)

    def setIsElite(self, value):
        self._setBool(9, value)

    def getVehicleLvl(self):
        return self._getNumber(10)

    def setVehicleLvl(self, value):
        self._setNumber(10, value)

    def getTooltipId(self):
        return self._getString(11)

    def setTooltipId(self, value):
        self._setString(11, value)

    def getTooltipContentId(self):
        return self._getString(12)

    def setTooltipContentId(self, value):
        self._setString(12, value)

    def getUserName(self):
        return self._getString(13)

    def setUserName(self, value):
        self._setString(13, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addNumberProperty('vehicleLvl', 1)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('userName', '')
