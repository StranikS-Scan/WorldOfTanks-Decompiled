# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/detailed_efficiency.py
import typing
from frameworks.wulf import Array
from gui.battle_results.br_constants import PersonalEfficiency
from gui.battle_results import br_helper
from gui.battle_results.presenter.common import setBaseUserInfo, setBaseEnemyVehicleInfo
from gui.battle_results.reusable.shared import getPlayerPlaceInTeam
from gui.impl.gen.view_models.views.lobby.postbattle.enemy_multi_params_model import EnemyMultiParamsModel
from gui.impl.gen.view_models.views.lobby.postbattle.efficiency_item_model import EfficiencyItemModel
from gui.impl.gen.view_models.views.lobby.postbattle.simple_efficiency_model import SimpleEfficiencyModel
from gui.impl.gen.view_models.views.lobby.postbattle.detailed_personal_efficiency_model import DetailedPersonalEfficiencyModel
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import ReusableInfo
_EFFICIENCY_ITEMS = [PersonalEfficiency.KILLS,
 PersonalEfficiency.DAMAGE,
 PersonalEfficiency.ASSIST,
 PersonalEfficiency.ARMOR]
_PARAMETER_VALUE_CHECKER = {PersonalEfficiency.STUN: br_helper.checkStunParameterValue}
_PARAMETER_VALUE_EXTRACTOR = {PersonalEfficiency.STUN: br_helper.getStunParameterValue,
 PersonalEfficiency.DAMAGE: br_helper.getDamageParameterValue,
 PersonalEfficiency.ARMOR: br_helper.getArmorParameterValue}
_ICON_PARAMETER_CHECKER = {PersonalEfficiency.STUN: br_helper.checkStunIconShown,
 PersonalEfficiency.DAMAGE: br_helper.checkDamageIconShown,
 PersonalEfficiency.ARMOR: br_helper.checkArmorIconShown}

def setDetailedEfficiency(model, reusable, rawResult):
    _fillEfficiencyEnemies(model, reusable, rawResult)
    _setPersonalEfficiency(model, reusable, rawResult)


def _fillEfficiencyEnemies(model, reusable, result):
    enemyItems = Array()
    for enemy in br_helper.getEnemies(reusable, result):
        hasParams = False
        for param in PersonalEfficiency.ALL:
            checker = _PARAMETER_VALUE_CHECKER.get(param, br_helper.getDefaultParameterValue)
            if checker(enemy, param) > 0:
                hasParams = True
                break

        if not hasParams:
            continue
        enemyItem = EnemyMultiParamsModel()
        setBaseUserInfo(enemyItem.user, reusable, enemy.vehicleID)
        enemyItem.setDbID(enemy.player.dbID)
        setBaseEnemyVehicleInfo(enemyItem, enemy)
        enemyItem.setVehicleCD(enemy.vehicle.intCD)
        enemyItem.setVehicleID(enemy.vehicleID)
        enemyItemParams = enemyItem.getParams()
        for paramName in PersonalEfficiency.ALL:
            paramItem = EfficiencyItemModel()
            paramItem.setParamName(paramName)
            totalExtractor = _PARAMETER_VALUE_EXTRACTOR.get(paramName, br_helper.getDefaultParameterValue)
            paramItem.setSimpleValue(totalExtractor(enemy, paramName))
            iconChecker = _ICON_PARAMETER_CHECKER.get(paramName, br_helper.getDefaultParameterValue)
            paramItem.setIsVisible(iconChecker(enemy, paramName))
            paramItem.setDetailedValue(br_helper.getDefaultParameterValue(enemy, paramName))
            enemyItemParams.addViewModel(paramItem)

        enemyItemParams.invalidate()
        enemyItems.addViewModel(enemyItem)

    model.setEnemies(enemyItems)


def _setPersonalEfficiency(submodel, reusable, result):
    info = reusable.getPersonalVehiclesInfo(result['personal'])
    efficiency = Array()
    efficiency.reserve(len(_EFFICIENCY_ITEMS))
    for paramName in _EFFICIENCY_ITEMS:
        personalEfficiency = SimpleEfficiencyModel()
        personalEfficiency.setParamName(paramName)
        paramValue = getattr(info, paramName)
        if 'event_boss' not in info.vehicle.tags:
            paramValue = getattr(info, paramName)
        else:
            paramValue = 0
        personalEfficiency.setRank(getPlayerPlaceInTeam(reusable, result, paramName, paramValue))
        efficiency.addViewModel(personalEfficiency)

    submodel.setPersonalEfficiency(efficiency)
