# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/presenters/sub_presenters/financial_report.py
import typing
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.vehicle_financial_report_model import VehicleFinancialReportModel
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.shared import events
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_results_view.battle_financial_report_model import BattleFinancialReportModel
from frontline.gui.financial_report_packers import FrontlineCrystalsDetailsPacker, FrontlineXpDetailsPacker, FrontlineFreeXpDetailsPacker, FrontlineCreditsStatisticsPacker, FrontlineGoldStatisticsPacker
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class FrontlineFinancialReportSubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return BattleFinancialReportModel

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        viewModel.setHasWotPlus(battleResults.reusable.personal.isWotPlus)
        viewModel.setHasAnyPremium(battleResults.reusable.personal.hasAnyPremium)
        vehicleStatsList = viewModel.getVehiclesFinancialStats()
        vehicleStatsList.clear()
        vehicleStatsList.addViewModel(self.getVehBattleResultsModel(None, battleResults, vehIdx=-1))
        for vehIdx, (_, vehicle) in enumerate(battleResults.reusable.personal.getVehicleItemsIterator()):
            vehicleStatsList.addViewModel(self.getVehBattleResultsModel(vehicle, battleResults, vehIdx))

        vehicleStatsList.invalidate()
        return

    def getVehBattleResultsModel(self, vehicle, battleResults, vehIdx):
        vehicleReportModel = VehicleFinancialReportModel()
        dataToPack = [(FrontlineCrystalsDetailsPacker, vehicleReportModel.crystals, CurrencyRecordsItemModel.CRYSTAL),
         (FrontlineXpDetailsPacker, vehicleReportModel.xp, CurrencyRecordsItemModel.XP_COST),
         (FrontlineFreeXpDetailsPacker, vehicleReportModel.freeXp, CurrencyRecordsItemModel.FREE_XP),
         (FrontlineCreditsStatisticsPacker, vehicleReportModel.credits, CurrencyRecordsItemModel.CREDITS),
         (FrontlineGoldStatisticsPacker, vehicleReportModel.gold, CurrencyRecordsItemModel.GOLD)]
        for packer, modelAttr, currencyItem in dataToPack:
            packer.packModel(modelAttr, currencyItem, battleResults, vehIdx)

        if vehIdx >= 0:
            vehicleReportModel.setIsGeneralInfo(False)
            fillVehicleModel(vehicleReportModel.vehicle, vehicle, (VEHICLE_TAGS.PREMIUM_IGR,))
        else:
            vehicleReportModel.setIsGeneralInfo(True)
        return vehicleReportModel

    def _getListeners(self):
        return ((events.LobbySimpleEvent.PREMIUM_XP_BONUS_CHANGED, self.__onXpBonusStatusChanged),)

    def _getCallbacks(self):
        return (('stats.applyAdditionalXPCount', self.__onXpBonusStatusChanged), ('stats.applyAdditionalWoTPlusXPCount', self.__onXpBonusStatusChanged))

    def __onXpBonusStatusChanged(self, _=None):
        with self.getViewModel().transaction():
            self.packBattleResults(self.getBattleResults())
