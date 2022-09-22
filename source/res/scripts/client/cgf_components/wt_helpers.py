# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/wt_helpers.py
import BigWorld
from constants import IS_CLIENT, ARENA_PERIOD, WT_TEAMS, ARENA_BONUS_TYPE
if IS_CLIENT:
    import CGF
    import GenericComponents
    from ArenaInfo import ArenaInfo
    from shared_utils import first
    from helpers import dependency
    from skeletons.gui.battle_session import IBattleSessionProvider
    from gui.battle_control.battle_constants import PERSONAL_EFFICIENCY_TYPE
    from cgf_components import BossTag, HunterTag, PlayerVehicleTag
    from Vehicle import Vehicle
    from EntityInfo import EntityInfo
WT_SHIELD_DEBUFF_DURATION = 'wtShieldDebuffDuration'
_BOSS_TAG = 'event_boss'
_SECONDS_IN_MINUTE = 60.0

def isBoss():
    return getattr(BigWorld.player(), 'team', 0) == WT_TEAMS.BOSS_TEAM


def isBossVehicle(vehicle):
    return vehicle.entityGameObject.findComponentByType(BossTag) is not None


def isPlayerVehicle(vehicle):
    return vehicle.entityGameObject.findComponentByType(PlayerVehicleTag) is not None


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


def canRespawn():
    return getPlayerLives() > 1


def getHuntersCount():
    query = CGF.Query(BigWorld.player().spaceID, (HunterTag, Vehicle))
    hunters = [ v for _, v in query.values() if v.isAlive() or getLives(v.id) > 0 ]
    return len(hunters)


def getPlayerVehicleHealthPercent():
    query = CGF.Query(BigWorld.player().spaceID, (PlayerVehicleTag, Vehicle))
    vehData = first(query)
    return 100.0 * vehData[1].health / vehData[1].maxHealth if vehData is not None else 0.0


def getBossVehicleHealthPercent():
    arenaInfoQuery = CGF.Query(BigWorld.player().spaceID, ArenaInfo)
    arenaInfo = first(arenaInfoQuery)
    if arenaInfo is not None:
        publicHealth = arenaInfo.dynamicComponents.get('arenaPublicHealth')
        if publicHealth is not None:
            for healthInfo in publicHealth.healthInfoList:
                vehicleInfo = getVehicleInfo(healthInfo['vehicleID'])
                if vehicleInfo is not None and _BOSS_TAG in vehicleInfo['vehicleType'].type.tags:
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
    return getLives(getattr(BigWorld.player(), 'playerVehicleID', None))


def getBattleTimeLeft():
    arena = getattr(BigWorld.player(), 'arena', None)
    return (arena.periodEndTime - BigWorld.serverTime()) / _SECONDS_IN_MINUTE if arena is not None and arena.period == ARENA_PERIOD.BATTLE else 0.0


def getDestroyedGeneratorsCount():
    query = CGF.Query(BigWorld.player().spaceID, GenericComponents.BattleStage)
    stageComponent = first(query.values())
    return stageComponent.maximum - stageComponent.current if stageComponent is not None else 0


def getCampCount():
    campsQuery = CGF.Query(BigWorld.player().spaceID, EntityInfo)
    camps = [ camp for camp in campsQuery.values() if camp.label == 'camp' ]
    return len(camps)


def getKilledByBoss():
    inputHandler = getattr(BigWorld.player(), 'inputHandler', None)
    if inputHandler is not None:
        killerInfo = getVehicleInfo(inputHandler.getKillerVehicleID())
        return killerInfo is not None and _BOSS_TAG in killerInfo['vehicleType'].type.tags
    else:
        return False


def getHasDebuff():
    arenaInfoQuery = CGF.Query(BigWorld.player().spaceID, ArenaInfo)
    arenaInfo = first(arenaInfoQuery)
    return WT_SHIELD_DEBUFF_DURATION in arenaInfo.dynamicComponents if arenaInfo is not None else False


def getTotalPlayerDamage():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    efficiencyCtrl = sessionProvider.shared.personalEfficiencyCtrl
    return int(efficiencyCtrl.getTotalEfficiency(PERSONAL_EFFICIENCY_TYPE.DAMAGE))


def isEventBattle():
    sessionProvider = dependency.instance(IBattleSessionProvider)
    bonusType = sessionProvider.arenaVisitor.getArenaBonusType()
    return bonusType in ARENA_BONUS_TYPE.EVENT_BATTLES_RANGE
