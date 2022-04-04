# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/bonuses/bp_vehicle_bonus_model.py
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel

class BpVehicleBonusModel(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(BpVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getBigIcon(self):
        return self._getString(4)

    def setBigIcon(self, value):
        self._setString(4, value)

    def getIndex(self):
        return self._getNumber(5)

    def setIndex(self, value):
        self._setNumber(5, value)

    def getName(self):
        return self._getString(6)

    def setName(self, value):
        self._setString(6, value)

    def getValue(self):
        return self._getString(7)

    def setValue(self, value):
        self._setString(7, value)

    def getIsCompensation(self):
        return self._getBool(8)

    def setIsCompensation(self, value):
        self._setBool(8, value)

    def getTooltipId(self):
        return self._getString(9)

    def setTooltipId(self, value):
        self._setString(9, value)

    def getTooltipContentId(self):
        return self._getString(10)

    def setTooltipContentId(self, value):
        self._setString(10, value)

    def getLabel(self):
        return self._getString(11)

    def setLabel(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(BpVehicleBonusModel, self)._initialize()
        self._addStringProperty('bigIcon', '')
        self._addNumberProperty('index', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addBoolProperty('isCompensation', False)
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipContentId', '')
        self._addStringProperty('label', '')
