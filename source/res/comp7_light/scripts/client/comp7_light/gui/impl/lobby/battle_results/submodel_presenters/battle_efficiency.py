# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/battle_results/submodel_presenters/battle_efficiency.py
from __future__ import absolute_import
import typing
from comp7_light.gui.impl.gen.view_models.views.lobby.comp7_light_battle_results_view_model import Comp7LightBattleResultsViewModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.lobby.battle_results.submodel_presenters.battle_efficiency import getEfficiencyParametersToPropertiesMap
from gui.impl.lobby.tooltips.battle_efficiency_tooltips_views import BattleResultsCriticalDamageTooltipView, BattleResultsStatsTooltipView
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.common import getEnemies
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array, ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
    from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.battle_results.base_capture_info_model import BaseCaptureInfoModel

class Comp7LightBattleEfficiencySubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return Comp7LightBattleResultsViewModel

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        self.__packDetailedPersonalEfficiency(viewModel.getDetailedPersonalEfficiency(), battleResults)
        self.__packBaseCaptureInfo(viewModel.baseCaptureInfo, battleResults)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsStatsTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        if contentID == R.views.mono.post_battle.tooltips.critical_damage():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsCriticalDamageTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        return super(Comp7LightBattleEfficiencySubPresenter, self).createToolTipContent(event, contentID)

    def __packDetailedPersonalEfficiency(self, model, battleResults):
        model.clear()
        reusable, results = battleResults.reusable, battleResults.results
        for enemy in getEnemies(reusable, results):
            enemyItem = DetailedPersonalEfficiencyModel()
            enemyItem.setDatabaseID(enemy.player.dbID)
            enemyItem.setUserName(enemy.player.realName)
            self.__packDetailedPersonalInfo(enemyItem.getPersonalEfficiencyItems(), enemy)
            model.addViewModel(enemyItem)

        model.invalidate()

    def __packDetailedPersonalInfo(self, model, player):
        model.clear()
        paramsMap = getEfficiencyParametersToPropertiesMap()
        for parameter, propertyName in paramsMap.items():
            efficiencyItem = DetailedPersonalEfficiencyItemModel()
            efficiencyItem.setParamType(parameter)
            efficiencyItem.setValue(getattr(player, propertyName, 0))
            model.addViewModel(efficiencyItem)

        model.invalidate()

    def __packBaseCaptureInfo(self, model, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        result = reusable.vehicles.getVehicleSummarizeInfo(reusable.getPlayerInfo(), results['vehicles'])
        model.setCapturePoints(result.capturePoints)
        model.setDroppedCapturePoints(result.droppedCapturePoints)
