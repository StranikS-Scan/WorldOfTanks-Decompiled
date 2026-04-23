# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/submodel_presenters/battle_efficiency.py
from __future__ import absolute_import
import typing
from comp7.gui.impl.gen.view_models.views.lobby.comp7_battle_results_view_model import Comp7BattleResultsViewModel
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
from gui.impl.lobby.battle_results.submodel_presenters.battle_efficiency import getEfficiencyParametersToPropertiesMap
from gui.impl.lobby.tooltips.battle_efficiency_tooltips_views import BattleResultsCriticalDamageTooltipView, BattleResultsStatsTooltipView
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.common import getEnemies
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
    from comp7_core.gui.battle_results.reusable.shared import Comp7CoreVehicleSummarizeInfo

class Comp7BattleEfficiencySubPresenter(BattleResultsSubPresenter):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)

    @classmethod
    def getViewModelType(cls):
        return Comp7BattleResultsViewModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsStatsTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        if contentID == R.views.mono.post_battle.tooltips.critical_damage():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsCriticalDamageTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        return super(Comp7BattleEfficiencySubPresenter, self).createToolTipContent(event, contentID)

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        self.__packDetailedPersonalEfficiency(viewModel.getDetailedPersonalEfficiency(), battleResults)
        self.__packVehicleSummarizeEfficiency(viewModel, battleResults)

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
        for parameter, value in paramsMap.items():
            efficiencyItem = DetailedPersonalEfficiencyItemModel()
            efficiencyItem.setParamType(parameter)
            efficiencyItem.setValue(getattr(player, value, 0))
            model.addViewModel(efficiencyItem)

        model.invalidate()

    def __packVehicleSummarizeEfficiency(self, model, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        result = reusable.vehicles.getVehicleSummarizeInfo(reusable.getPlayerInfo(), results['vehicles'])
        model.baseCaptureInfo.setCapturePoints(result.capturePoints)
        model.baseCaptureInfo.setDroppedCapturePoints(result.droppedCapturePoints)
