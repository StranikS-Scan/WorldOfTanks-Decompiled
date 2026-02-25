# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/gen/view_models/views/lobby/tooltips/vehicle_tooltip_view_model.py
from frameworks.wulf import ViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.daily_bonus_model import DailyBonusModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.tech_parameters_cmp_view_model import TechParametersCmpViewModel
from battle_royale.gui.impl.gen.view_models.views.lobby.views.battle_royale_event_model import BattleRoyaleEventModel

class VehicleTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(VehicleTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tech(self):
        return self._getViewModel(0)

    @staticmethod
    def getTechType():
        return TechParametersCmpViewModel

    @property
    def eventInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getEventInfoType():
        return BattleRoyaleEventModel

    @property
    def dailyBonus(self):
        return self._getViewModel(2)

    @staticmethod
    def getDailyBonusType():
        return DailyBonusModel

    def getVehicleName(self):
        return self._getString(3)

    def setVehicleName(self, value):
        self._setString(3, value)

    def getVehicleNation(self):
        return self._getString(4)

    def setVehicleNation(self, value):
        self._setString(4, value)

    def getVehicleType(self):
        return self._getString(5)

    def setVehicleType(self, value):
        self._setString(5, value)

    def getStatusLevel(self):
        return self._getString(6)

    def setStatusLevel(self, value):
        self._setString(6, value)

    def getStatusText(self):
        return self._getString(7)

    def setStatusText(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(VehicleTooltipViewModel, self)._initialize()
        self._addViewModelProperty('tech', TechParametersCmpViewModel())
        self._addViewModelProperty('eventInfo', BattleRoyaleEventModel())
        self._addViewModelProperty('dailyBonus', DailyBonusModel())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleNation', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('statusLevel', '')
        self._addStringProperty('statusText', '')
