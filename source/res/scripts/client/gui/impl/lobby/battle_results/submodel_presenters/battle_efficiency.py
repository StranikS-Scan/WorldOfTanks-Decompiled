# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/submodel_presenters/battle_efficiency.py
import typing
from frameworks.wulf import Array
from gui.impl.lobby.tooltips.battle_efficiency_tooltips_views import BattleResultsStatsTooltipView, BattleResultsCriticalDamageTooltipView
from gui.battle_results.presenters.battle_results_sub_presenter import BattleResultsSubPresenter
from gui.battle_results.pbs_helpers.common import getEnemies
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_item_model import DetailedPersonalEfficiencyItemModel
from gui.impl.gen.view_models.views.lobby.battle_results.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
from gui.impl.gen.view_models.views.lobby.battle_results.random.random_battle_results_view_model import RandomBattleResultsViewModel
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from gui.battle_results.stats_ctrl import BattleResults
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.battle_results.base_capture_info_model import BaseCaptureInfoModel
EFFICIENCY_ITEMS_TO_PROPERTIES = {DetailedPersonalEfficiencyItemModel.KILLED: 'targetKills',
 DetailedPersonalEfficiencyItemModel.SPOTTED: 'spotted',
 DetailedPersonalEfficiencyItemModel.DAMAGE_DEALT: 'damageDealt',
 DetailedPersonalEfficiencyItemModel.PIERCINGS: 'piercings',
 DetailedPersonalEfficiencyItemModel.STUN: 'damageAssistedStun',
 DetailedPersonalEfficiencyItemModel.STUN_COUNT: 'stunNum',
 DetailedPersonalEfficiencyItemModel.DAMAGE_ASSISTED: 'damageAssisted',
 DetailedPersonalEfficiencyItemModel.CRITICAL_DAMAGE: 'critsCount',
 DetailedPersonalEfficiencyItemModel.DAMAGE_BLOCKED_BY_ARMOR: 'damageBlockedByArmor',
 DetailedPersonalEfficiencyItemModel.RICKOCHETS_RECEIVED: 'rickochetsReceived',
 DetailedPersonalEfficiencyItemModel.NO_DAMAGE_DIRECT_HITS_RECIEVEVD: 'noDamageDirectHitsReceived'}

def getEfficiencyParametersToPropertiesMap():
    return EFFICIENCY_ITEMS_TO_PROPERTIES


class BattleEfficiencySubPresenter(BattleResultsSubPresenter):

    @classmethod
    def getViewModelType(cls):
        return RandomBattleResultsViewModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.BattleResultsStatsTooltipView():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsStatsTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        if contentID == R.views.mono.post_battle.tooltips.critical_damage():
            paramType = event.getArgument('paramType')
            userName = event.getArgument('userName')
            return BattleResultsCriticalDamageTooltipView(self.parentView.arenaUniqueID, paramType, userName)
        return super(BattleEfficiencySubPresenter, self).createToolTipContent(event, contentID)

    def packBattleResults(self, battleResults):
        viewModel = self.getViewModel()
        self.__packDetailedPersonalEfficiency(viewModel.getDetailedPersonalEfficiency(), battleResults)
        self.__packBaseCaptureInfo(viewModel.baseCaptureInfo, battleResults)

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
        for parameter in paramsMap:
            efficiencyItem = DetailedPersonalEfficiencyItemModel()
            efficiencyItem.setParamType(parameter)
            efficiencyItem.setValue(getattr(player, paramsMap[parameter], 0))
            model.addViewModel(efficiencyItem)

        model.invalidate()

    def __packBaseCaptureInfo(self, model, battleResults):
        reusable, results = battleResults.reusable, battleResults.results
        result = reusable.vehicles.getVehicleSummarizeInfo(reusable.getPlayerInfo(), results['vehicles'])
        model.setCapturePoints(result.capturePoints)
        model.setDroppedCapturePoints(result.droppedCapturePoints)
