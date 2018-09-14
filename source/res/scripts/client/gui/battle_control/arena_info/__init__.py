# Embedded file name: scripts/client/gui/battle_control/arena_info/__init__.py
import BigWorld
import constants
from constants import ARENA_BONUS_TYPE_CAPS as caps

def getClientArena(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        arena = avatar.arena
    except AttributeError:
        arena = None

    return arena


def getArenaType(avatar = None):
    return getattr(getClientArena(avatar), 'arenaType', None)


def getArenaTypeID(avatar = None):
    if avatar is None:
        avatar = BigWorld.player()
    try:
        arenaTypeID = avatar.arenaTypeID
    except AttributeError:
        arenaTypeID = 0

    return arenaTypeID


def getPlayerVehicleID():
    return getattr(BigWorld.player(), 'playerVehicleID', 0)


def isPlayerTeamKillSuspected():
    return bool(getattr(BigWorld.player(), 'tkillIsSuspected', 0))


def getArenaGuiType(arena = None):
    if arena is None:
        arena = getClientArena()
    return getattr(arena, 'guiType', constants.ARENA_GUI_TYPE.UNKNOWN)


def getArenaBonusType():
    return getattr(getClientArena(), 'bonusType', constants.ARENA_BONUS_TYPE.UNKNOWN)


def getArenaGuiTypeLabel():
    arenaGuiType = getArenaGuiType()
    if arenaGuiType in constants.ARENA_GUI_TYPE_LABEL.LABELS:
        label = constants.ARENA_GUI_TYPE_LABEL.LABELS[getArenaGuiType()]
    else:
        label = ''
    return label


def isLowLevelBattle():
    arena, battleLevel = getClientArena(), None
    if arena is not None:
        battleLevel = arena.extraData.get('battleLevel')
    return 0 < battleLevel < 4


def isRandomBattle():
    return getArenaGuiType() == constants.ARENA_GUI_TYPE.RANDOM


def isEventBattle():
    return getArenaGuiType() == constants.ARENA_GUI_TYPE.EVENT_BATTLES


def isFalloutBattle():
    arenaType = getArenaType()
    return isEventBattle() and arenaType is not None and arenaType.gameplayName.startswith('fallout')


def isInSandboxBattle(arena = None):
    return getArenaGuiType(arena=arena) in constants.ARENA_GUI_TYPE.SANDBOX_RANGE


def makeClientTeamBaseID(team, baseID):
    if baseID is None:
        baseID = 0
    return (int(baseID) << 6) + team


def parseClientTeamBaseID(clientID):
    team = clientID & 63
    return (team, clientID >> 6)


def isArenaInWaiting():
    arena = getClientArena()
    return arena is not None and arena.period == constants.ARENA_PERIOD.WAITING


def getArenaIconKey(arenaType = None, arenaGuiType = None):
    if arenaType is None:
        arena = getClientArena()
        if arena is None:
            return ''
        arenaType = arena.arenaType
    arenaGuiType = arenaGuiType or getArenaGuiType()
    arenaIcon = arenaType.geometryName
    if arenaGuiType == constants.ARENA_GUI_TYPE.EVENT_BATTLES and arenaType.gameplayName.startswith('fallout'):
        return '%s_fallout' % arenaIcon
    else:
        return arenaIcon


def getArenaIcon(iconKey, arenaType = None, arenaGuiType = None):
    return iconKey % getArenaIconKey(arenaType, arenaGuiType)


def hasFlags(arenaType = None, arenBonusType = None):
    if arenaType is None:
        arenaType = getArenaType()
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenaType is not None and arenBonusType is not None:
        return caps.get(arenBonusType) & caps.FLAG_MECHANICS > 0 and arenaType.flagSpawnPoints
    else:
        return False


def hasResourcePoints(arenaType = None, arenBonusType = None):
    if arenaType is None:
        arenaType = getArenaType()
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenaType is not None and arenBonusType is not None:
        return caps.get(arenBonusType) & caps.RESOURCE_POINTS > 0 and arenaType.resourcePoints
    else:
        return False


def getIsMultiteam(arenaType = None):
    if arenaType is None:
        arenaType = getArenaType()
    return arenaType.gameplayName in ('fallout', 'fallout2', 'fallout3')


def hasRepairPoints(arenaType = None, arenBonusType = None):
    if arenaType is None:
        arenaType = getArenaType()
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenaType is not None and arenBonusType is not None:
        return caps.get(arenBonusType) & caps.REPAIR_MECHANICS > 0 and arenaType.repairPoints
    else:
        return False


def hasRespawns(arenBonusType = None):
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenBonusType is not None:
        return caps.get(arenBonusType) & caps.RESPAWN > 0
    else:
        return False


def hasRage(arenBonusType = None):
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenBonusType is not None:
        return caps.get(arenBonusType) & caps.RAGE_MECHANICS > 0
    else:
        return False


def hasGasAttack(arenBonusType = None):
    if arenBonusType is None:
        arenBonusType = getArenaBonusType()
    if arenBonusType is not None:
        return caps.get(arenBonusType) & caps.GAS_ATTACK_MECHANICS > 0 and getIsMultiteam()
    else:
        return False
