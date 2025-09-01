# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/cgf_components/wt_helpers.py
import BigWorld
from constants import IS_CLIENT, ARENA_PERIOD
from white_tiger_common.wt_constants import ARENA_BONUS_TYPE, WT_TEAMS, WT_VEHICLE_TAGS, WT_BATTLE_STAGE
from constants import EQUIPMENT_STAGES
if IS_CLIENT:
    import CGF
    from ArenaInfo import ArenaInfo
    from shared_utils import first
    from helpers import dependency
    from skeletons.gui.battle_session import IBattleSessionProvider
    from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE
    from gui.battle_control import avatar_getter
    from white_tiger.cgf_components import BossTag, HunterTag, PlayerVehicleTag
    from Vehicle import Vehicle
    from WTIndexPool import WTIndexPool
    import sound_event_managers
_SECONDS_IN_MINUTE = 60.0

def getBattleStateComponent():
    arenaInfo = avatar_getter.getArenaInfo()
    return arenaInfo.dynamicComponents.get('wtBattleStateComponent') if arenaInfo else None


def getPlasmaBonusComponent():
    arena = avatar_getter.getArena()
    return arena.arenaInfo.dynamicComponents.get('wtPlasmaBonusComponent') if arena and arena.arenaInfo else None


def isBoss():
    return getattr(BigWorld.player(), 'team', 0) == WT_TEAMS.BOSS_TEAM


def isBossVehicle(vehicle):
    return vehicle.entityGameObject.findComponentByType(BossTag) is not None


def isBossTeam(vehicle):
    vehicleInfo = getVehicleInfo(vehicle.id)
    return vehicleInfo['team'] == WT_TEAMS.BOSS_TEAM


@dependency.replace_none_kwargs(battleSession=IBattleSessionProvider)
def isBossBot(vehicleID=0, vInfo=None, battleSession=None):
    if vInfo is None:
        arenaDP = battleSession.getArenaDP()
        vInfo = arenaDP.getVehicleInfo(vehicleID)
    tags = vInfo.vehicleType.tags
    return WT_VEHICLE_TAGS.BOT in tags and WT_VEHICLE_TAGS.BOSS not in tags


def isPlayerVehicle(vehicle):
    return vehicle.entityGameObject.findComponentByType(PlayerVehicleTag) is not None if vehicle is not None else False


def getBossVehicle():
    query = CGF.Query(BigWorld.player().spaceID, (BossTag, Vehicle))
    vehData = first(query)
    return vehData[1] if vehData is not None else None


def getPlayerVehicle():
    query = CGF.Query(BigWorld.player().spaceID, (PlayerVehicleTag, Vehicle))
    vehData = first(query)
    return vehData[1] if vehData is not None else None


def getVehicleInfo(vehicleId):
    arena = getattr(BigWorld.player(), 'arena')
    return arena.vehicles.get(vehicleId) if arena is not None else None


def isEngineAuditionPresent(vehicle):
    return False if not vehicle or not vehicle.appearance else vehicle.appearance.engineAudition is not None


def isMinibossInArena():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    if not sessionProvider:
        return False
    arenaDP = sessionProvider.getArenaDP()
    if not arenaDP:
        return False
    for vInfo in arenaDP.getVehiclesInfoIterator():
        if WT_VEHICLE_TAGS.MINIBOSS in vInfo.vehicleType.tags and vInfo.isAlive():
            return True

    return False


def getHuntersCount():
    query = CGF.Query(BigWorld.player().spaceID, (HunterTag, Vehicle))
    hunters = [ v for _, v in query.values() if v.isAlive() or getLives(v.id) > 0 ]
    return len(hunters)


def getPlayerVehicleHealthPercent():
    query = CGF.Query(BigWorld.player().spaceID, (PlayerVehicleTag, Vehicle))
    vehData = first(query)
    return 100.0 * vehData[1].health / vehData[1].maxHealth if vehData is not None else 0.0


def getBossVehicleHealthPercent():
    battleStateComponent = getBattleStateComponent()
    if battleStateComponent:
        for healthInfo in battleStateComponent.healthInfoList:
            vehicleInfo = getVehicleInfo(healthInfo['vehicleID'])
            if vehicleInfo is not None and WT_VEHICLE_TAGS.BOSS in vehicleInfo['vehicleType'].type.tags:
                return 100.0 * healthInfo['health'] / vehicleInfo['maxHealth']

    return 0.0


def getLives(vehicleId):
    if vehicleId is not None:
        avatar = BigWorld.player()
        if avatar is not None and avatar.arena is not None and avatar.arena.arenaInfo is not None:
            teamLivesComponent = avatar.arena.arenaInfo.dynamicComponents.get('teamLivesComponent')
            if teamLivesComponent is not None:
                return teamLivesComponent.getLives(vehicleId)
    return 0


def getPlayerLives():
    playerVehicle = BigWorld.player().vehicle
    return playerVehicle.VehicleLivesComponent.lives if playerVehicle and 'VehicleLivesComponent' in playerVehicle.dynamicComponents else 0


def getBattleTimeLeft():
    arena = getattr(BigWorld.player(), 'arena', None)
    return (arena.periodEndTime - BigWorld.serverTime()) / _SECONDS_IN_MINUTE if arena is not None and arena.period == ARENA_PERIOD.BATTLE else 0.0


def getDestroyedGeneratorsCount():
    return getBattleStateComponent().generatorsLeft


def getCampCount():
    campsQuery = CGF.Query(BigWorld.player().spaceID, WTIndexPool)
    camps = [ camp for camp in campsQuery.values() if camp.label == 'camp' ]
    return len(camps)


def getKilledByBoss():
    inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
    if inputHandler is not None:
        killerInfo = getVehicleInfo(inputHandler.getKillerVehicleID())
        return killerInfo is not None and WT_VEHICLE_TAGS.BOSS in killerInfo['vehicleType'].type.tags
    else:
        return False


def getHasDebuff():
    arenaInfoQuery = CGF.Query(BigWorld.player().spaceID, ArenaInfo)
    arenaInfo = first(arenaInfoQuery)
    if arenaInfo is not None:
        state = WT_BATTLE_STAGE.getCurrent(arenaInfo)
        return state == WT_BATTLE_STAGE.DEBUFF or state == WT_BATTLE_STAGE.END_GAME
    else:
        return False


def getTotalPlayerDamage():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    efficiencyCtrl = sessionProvider.shared.personalEfficiencyCtrl
    return int(efficiencyCtrl.getTotalEfficiency(PERSONAL_EFFICIENCY_TYPE.DAMAGE))


def isEventBattle():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    bonusType = sessionProvider.arenaVisitor.getArenaBonusType()
    return bonusType in ARENA_BONUS_TYPE.EVENT_BATTLES_RANGE


def getIsExpertPlayer():
    return sound_event_managers.WTBattleCountManager.isExpert(isBoss())


def isHyperionCharging(stage):
    return stage in [EQUIPMENT_STAGES.EXHAUSTED, EQUIPMENT_STAGES.STARTUP_COOLDOWN]
