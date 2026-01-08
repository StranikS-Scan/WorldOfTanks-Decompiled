# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/post_battle_results_view/battle_financial_report_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.vehicle_financial_report_model import VehicleFinancialReportModel

class BattleFinancialReportModel(ViewModel):
    __slots__ = ()
    PLAYER_RANK_XP = 'playerRankXP'

    def __init__(self, properties=3, commands=0):
        super(BattleFinancialReportModel, self).__init__(properties=properties, commands=commands)

    def getHasAnyPremium(self):
        return self._getBool(0)

    def setHasAnyPremium(self, value):
        self._setBool(0, value)

    def getHasWotPlus(self):
        return self._getBool(1)

    def setHasWotPlus(self, value):
        self._setBool(1, value)

    def getVehiclesFinancialStats(self):
        return self._getArray(2)

    def setVehiclesFinancialStats(self, value):
        self._setArray(2, value)

    @staticmethod
    def getVehiclesFinancialStatsType():
        return VehicleFinancialReportModel

    def _initialize(self):
        super(BattleFinancialReportModel, self)._initialize()
        self._addBoolProperty('hasAnyPremium', False)
        self._addBoolProperty('hasWotPlus', False)
        self._addArrayProperty('vehiclesFinancialStats', Array())
