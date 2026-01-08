# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_results_view/vehicle_financial_report_model.py
from gui.impl.gen.view_models.views.lobby.battle_results.financial_report_model import FinancialReportModel
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class VehicleFinancialReportModel(FinancialReportModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(VehicleFinancialReportModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicle(self):
        return self._getViewModel(5)

    @staticmethod
    def getVehicleType():
        return VehicleModel

    def getIsGeneralInfo(self):
        return self._getBool(6)

    def setIsGeneralInfo(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(VehicleFinancialReportModel, self)._initialize()
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addBoolProperty('isGeneralInfo', False)
