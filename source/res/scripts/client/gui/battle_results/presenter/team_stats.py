# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/presenter/team_stats.py
import typing
from frameworks.wulf import Array
from gui.battle_results import br_helper
from gui.battle_results.presenter.achievements import setTeamStatsAchievements
from gui.battle_results.presenter.common import setBaseUserInfo
from gui.impl.gen.view_models.views.lobby.postbattle.player_model import PlayerModel
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME, getSimpleShortUserName
if typing.TYPE_CHECKING:
    from gui.battle_results.presenter.getter.getter import PostbattleFieldsGetter
    from gui.battle_results.reusable import ReusableInfo
    from gui.battle_results.reusable.shared import VehicleSummarizeInfo
    from gui.impl.gen.view_models.views.lobby.postbattle.player_model import PlayerDetailsModel
    from gui.impl.gen.view_models.views.lobby.postbattle.team_stats_model import TeamStatsModel

def setTeamStatsData(model, getter, reusable, result):
    allies, enemies = reusable.getBiDirectionTeamsIterator(result['vehicles'])
    items = model.getAllies()
    if items is None:
        return
    else:
        _fillModel(items, allies, reusable, result, getter)
        items = model.getEnemies()
        if items is None:
            return
        _fillModel(items, enemies, reusable, result, getter)
        return


def _fillModel(items, data, reusable, result, getter):
    items.clear()
    for idx, info in enumerate(data):
        if info.player.dbID == 0:
            continue
        player = PlayerModel()
        player.setIdx(idx)
        player.setDbID(info.player.dbID)
        playerTeam = info.player.team
        player.setTeam(playerTeam)
        player.setSquadIdx(info.player.squadIndex)
        if playerTeam == reusable.getPersonalTeam():
            isPersonal = br_helper.isPersonalResults(reusable, info.player.dbID)
            player.setIsPersonal(isPersonal)
            player.setIsSameSquad(br_helper.isOwnSquad(reusable, info.vehicleID) and not isPersonal)
        setBaseUserInfo(player.user, reusable, info.vehicleID)
        player.setVehicleName(info.vehicle.name)
        player.setLocalizedVehicleName(getSimpleShortUserName(info.vehicle))
        player.setVehicleLevel(info.vehicle.level)
        player.setVehicleType(info.vehicle.type)
        player.setVehicleCD(info.vehicle.intCD)
        player.setEarnedXp(info.xp)
        player.setKills(info.kills)
        player.setDamageDealt(info.damageDealt)
        setTeamStatsAchievements(player.details, info)
        _fillPlayerDetails(player.details, info, reusable, result, getter)
        items.addViewModel(player)

    items.invalidate()


def _fillPlayerDetails(detailBlock, info, reusable, result, getter):
    detailBlock.setAttackReason(info.deathReason)
    if br_helper.isPersonalResults(reusable, info.player.dbID):
        detailBlock.setIsLeftBattle(br_helper.isPlayerLeftBattle(reusable))
    killerVehicleID = info.killerID
    if killerVehicleID:
        setBaseUserInfo(detailBlock.killer, reusable, killerVehicleID)
    _fillStatistics(detailBlock, info, result, reusable, getter)


def _fillStatistics(model, info, results, reusable, getter):
    items = Array()
    personalInfo = reusable.getPlayerInfo()
    personalDBID = personalInfo.dbID
    isPersonal = info.player.dbID == personalDBID
    isSPG = info.vehicle.type == VEHICLE_CLASS_NAME.SPG
    isRoleExp = reusable.common.arenaVisitor.bonus.hasRoleExpSystem()
    for field in getter.getTeamStats(isSPG, isPersonal, isRoleExp):
        statsItem = field.model()
        statsItem.setValue(field.getFieldValues(info, results))
        statsItem.setItemType(field.valueType)
        statsItem.setBlockIdx(field.blockIdx)
        statsItem.setId(field.stringID)
        statsItem.setHasTooltip(field.hasTooltip)
        items.addViewModel(statsItem)

    model.setStatistics(items)
