# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/statistics_category_tooltip_bonus_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.tooltips.tankman_info_model import TankmanInfoModel

class StatisticsCategoryTooltipBonusModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(StatisticsCategoryTooltipBonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleType():
        return VehicleInfoModel

    @property
    def tankman(self):
        return self._getViewModel(1)

    @staticmethod
    def getTankmanType():
        return TankmanInfoModel

    def getLabel(self):
        return self._getString(2)

    def setLabel(self, value):
        self._setString(2, value)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getValue(self):
        return self._getString(4)

    def setValue(self, value):
        self._setString(4, value)

    def getCount(self):
        return self._getNumber(5)

    def setCount(self, value):
        self._setNumber(5, value)

    def getIcon(self):
        return self._getString(6)

    def setIcon(self, value):
        self._setString(6, value)

    def getOverlayType(self):
        return self._getString(7)

    def setOverlayType(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(StatisticsCategoryTooltipBonusModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleInfoModel())
        self._addViewModelProperty('tankman', TankmanInfoModel())
        self._addStringProperty('label', '')
        self._addStringProperty('name', '')
        self._addStringProperty('value', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('icon', '')
        self._addStringProperty('overlayType', '')
