# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/submodel_presenters/financial_report.py
from __future__ import absolute_import
from comp7_light.gui.impl.lobby.battle_results.comp7_light_financial_report_packers import Comp7LightCreditsStatisticsPacker, Comp7LightXpDetailsPacker, Comp7LightFreeXpDetailsPacker
from gui.battle_results.presenters.packers.economics.financial_report_packers import CrystalsDetailsPacker, GoldStatisticsPacker
from gui.impl.gen.view_models.views.lobby.battle_results.currency_records_item_model import CurrencyRecordsItemModel
from gui.impl.lobby.battle_results.submodel_presenters.financial_report import FinancialReportSubPresenter

class Comp7LightFinancialReportSubPresenter(FinancialReportSubPresenter):

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        CrystalsDetailsPacker.packModel(viewModel.crystals, CurrencyRecordsItemModel.CRYSTAL, battleResults)
        Comp7LightXpDetailsPacker.packModel(viewModel.xp, CurrencyRecordsItemModel.XP_COST, battleResults)
        Comp7LightFreeXpDetailsPacker.packModel(viewModel.freeXp, CurrencyRecordsItemModel.FREE_XP, battleResults)
        Comp7LightCreditsStatisticsPacker.packModel(viewModel.credits, CurrencyRecordsItemModel.CREDITS, battleResults)
        GoldStatisticsPacker.packModel(viewModel.gold, CurrencyRecordsItemModel.GOLD, battleResults)
