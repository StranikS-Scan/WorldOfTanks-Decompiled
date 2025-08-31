# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/battle_result/tooltips/personal_efficiency.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.tooltip_efficiency_model import TooltipEfficiencyModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from gui.battle_results import reusable
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_with_one_param_model import EnemyWithOneParamModel
from white_tiger.gui.impl.lobby.battle_result.wt_battle_result_helpers import getPlayerPlaceInTeam, getEnemies, EfficiencyItems, EfficiencyKeys, setBaseUserInfo, setBaseEnemyVehicleInfo

class WtEfficiencyTooltip(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__efficiencyType', '__reusable', '__results')
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueID, efficiencyType):
        contentResID = R.views.white_tiger.lobby.postbattle.tooltips.PersonalEfficiency()
        settings = ViewSettings(contentResID)
        settings.model = TooltipEfficiencyModel()
        super(WtEfficiencyTooltip, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__efficiencyType = efficiencyType
        vo = self.__battleResults.getResultsVO(self.__arenaUniqueID)
        self.__reusable = None
        reusableRaw = vo.get('reusable')
        if reusableRaw:
            self.__reusable = reusable.createReusableInfo(reusableRaw)
        self.__results = vo.get('results')
        return

    def _onLoading(self, *args, **kwargs):
        super(WtEfficiencyTooltip, self)._onLoading(*args, **kwargs)
        if self.__reusable is None or self.__results is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                self.__setPersonalEfficiencyTooltipData(model, self.__efficiencyType)
            return

    def __setPersonalEfficiencyTooltipData(self, model, parameterName):
        info = self.__reusable.getPersonalVehiclesInfo(self.__results['personal'])
        total = getattr(info, parameterName)
        rank = getPlayerPlaceInTeam(self.__reusable, self.__results, parameterName, total)
        enemies = getEnemies(self.__reusable, self.__results)
        enemyParamName = EfficiencyItems[parameterName][EfficiencyKeys.ENEMY_PARAM_NAME]
        enemyModelArray = Array()
        for enemy in enemies:
            if enemy.player.dbID == 0:
                continue
            paramValue = getattr(enemy, enemyParamName)
            if paramValue <= 0:
                continue
            enemyModel = EnemyWithOneParamModel()
            setBaseUserInfo(enemyModel.user, enemy.vehicleID, self.__reusable)
            setBaseEnemyVehicleInfo(enemyModel, enemy)
            enemyModel.setValue(paramValue)
            enemyModelArray.addViewModel(enemyModel)

        model.setParamName(parameterName)
        model.setRank(rank)
        model.setEnemies(enemyModelArray)

    def _finalize(self):
        self.__reusable = None
        self.__results = None
        super(WtEfficiencyTooltip, self)._finalize()
        return
