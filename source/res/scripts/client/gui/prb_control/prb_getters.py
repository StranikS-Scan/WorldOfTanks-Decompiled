# Embedded file name: scripts/client/gui/prb_control/prb_getters.py
import BigWorld
from constants import QUEUE_TYPE, PREBATTLE_TYPE_NAMES, ARENA_GUI_TYPE, PREBATTLE_TYPE, DEFAULT_LANGUAGE
from gui.prb_control.settings import makePrebattleSettings, VEHICLE_MAX_LEVEL

def isInRandomQueue():
    return getattr(BigWorld.player(), 'isInRandomQueue', False)


def isInTutorialQueue():
    return getattr(BigWorld.player(), 'isInTutorialQueue', False)


def isInEventBattlesQueue():
    return getattr(BigWorld.player(), 'isInEventBattles', False)


def isInSandboxQueue():
    return getattr(BigWorld.player(), 'isInSandboxQueue', False)


def getQueueType():
    queueType = 0
    if isInRandomQueue():
        queueType = QUEUE_TYPE.RANDOMS
    elif isInEventBattlesQueue():
        queueType = QUEUE_TYPE.EVENT_BATTLES
    elif isInTutorialQueue():
        queueType = QUEUE_TYPE.TUTORIAL
    elif isInSandboxQueue():
        queueType = QUEUE_TYPE.SANDBOX
    return queueType


def getClientPrebattle():
    return getattr(BigWorld.player(), 'prebattle', None)


def getPrebattleID():
    clientPrb = getClientPrebattle()
    prbID = 0
    if clientPrb:
        prbID = clientPrb.id
    return prbID


def isPrebattleSettingsReceived(prebattle = None):
    prb = prebattle or getClientPrebattle()
    if prb is not None:
        return prb.settings is not None
    else:
        return False


def getPrebattleSettings(prebattle = None):
    prb = prebattle or getClientPrebattle()
    if prb and prb.settings:
        return makePrebattleSettings(prb.settings)
    return makePrebattleSettings()


def getPrebattleProps(prebattle = None):
    prb = prebattle or getClientPrebattle()
    result = {}
    if prb and prb.properties:
        result = prb.properties
    return result


def getPrebattleRosters(prebattle = None):
    prb = prebattle or getClientPrebattle()
    result = {}
    if prb:
        result = prb.rosters
    return result


def getPrebattleTeamStates(prebattle = None):
    prb = prebattle or getClientPrebattle()
    result = [None, 0, 0]
    if prb:
        result = prb.teamStates
    return result


def getPrebattleAutoInvites():
    autoInvites = {}
    player = BigWorld.player()
    if hasattr(player, 'prebattleAutoInvites'):
        autoInvites = player.prebattleAutoInvites
    return autoInvites


def getPrebattleType(prebattle = None, settings = None):
    try:
        if settings is None:
            settings = getPrebattleSettings(prebattle=prebattle)
        return settings['type']
    except KeyError:
        return

    return


def getPrebattleTypeName(prbType = None):
    if prbType is None:
        prbType = getPrebattleType()
    if prbType in PREBATTLE_TYPE_NAMES:
        prbTypeName = PREBATTLE_TYPE_NAMES[prbType]
    else:
        prbTypeName = 'PREBATTLE'
    return prbTypeName


_ARENA_GUI_TYPE_BY_PRB_TYPE = {PREBATTLE_TYPE.SQUAD: ARENA_GUI_TYPE.RANDOM,
 PREBATTLE_TYPE.TRAINING: ARENA_GUI_TYPE.TRAINING,
 PREBATTLE_TYPE.COMPANY: ARENA_GUI_TYPE.COMPANY}
_ARENA_GUI_TYPE_BY_QUEUE_TYPE = {QUEUE_TYPE.RANDOMS: ARENA_GUI_TYPE.RANDOM,
 QUEUE_TYPE.EVENT_BATTLES: ARENA_GUI_TYPE.EVENT_BATTLES}

def getArenaGUIType(prbType = None, queueType = None):
    if prbType is None:
        prbType = getPrebattleType()
    arenaGuiType = ARENA_GUI_TYPE.RANDOM
    if prbType is not None:
        arenaGuiType = ARENA_GUI_TYPE.UNKNOWN
        if prbType in _ARENA_GUI_TYPE_BY_PRB_TYPE:
            arenaGuiType = _ARENA_GUI_TYPE_BY_PRB_TYPE[prbType]
    elif queueType:
        if queueType in _ARENA_GUI_TYPE_BY_QUEUE_TYPE:
            arenaGuiType = _ARENA_GUI_TYPE_BY_QUEUE_TYPE[queueType]
    return arenaGuiType


def getTotalLevelLimits(teamLimits):
    return teamLimits['totalLevel']


def getLevelLimits(teamLimits):
    limit = teamLimits['level']
    return (limit[0], min(limit[1], VEHICLE_MAX_LEVEL))


def getNationsLimits(teamLimits):
    return teamLimits['nations']


def getMaxSizeLimits(teamLimits):
    return teamLimits['maxCount']


def getClassLevelLimits(teamLimits, classType):
    classesLimits = teamLimits['classes']
    if classesLimits is not None and classType not in classesLimits:
        return (0, 0)
    else:
        classLevel = teamLimits['classLevel']
        if classType in classLevel:
            limit = teamLimits['classLevel'][classType]
        else:
            limit = getLevelLimits(teamLimits)
        return (limit[0], min(limit[1], VEHICLE_MAX_LEVEL))


def getPrebattleLocalizedData(extraData = None):
    led = {}
    if extraData is None:
        extraData = getPrebattleSettings()['extraData']
    if extraData:
        from helpers import getClientLanguage
        lng = getClientLanguage()
        ld = extraData.get('localized_data', {})
        if ld:
            if lng in ld:
                led = ld[lng]
            elif DEFAULT_LANGUAGE in ld:
                led = ld[DEFAULT_LANGUAGE]
            else:
                sortedItems = ld.items()
                sortedItems.sort()
                led = sortedItems[0][1]
    return led


def getCreatorFullName():
    settings = getPrebattleSettings()
    creatorName = settings['creator']
    clanAbbrev = settings['creatorClanAbbrev']
    from gui.LobbyContext import g_lobbyContext
    creatorRegion = g_lobbyContext.getRegionCode(settings['creatorDBID'])
    if clanAbbrev:
        fullName = '{0:>s}[{1:>s}]'.format(creatorName, clanAbbrev)
    else:
        fullName = creatorName
    if creatorRegion:
        fullName = '{0:>s} {1:>s}'.format(fullName, creatorRegion)
    return fullName


def areSpecBattlesHidden():
    return not getattr(BigWorld.player(), 'prebattleAutoInvites', None)


def isCompany(settings = None):
    return getPrebattleType(settings=settings) == PREBATTLE_TYPE.COMPANY


def isTraining(settings = None):
    return getPrebattleType(settings=settings) == PREBATTLE_TYPE.TRAINING


def isBattleSession(settings = None):
    return getPrebattleType(settings=settings) in (PREBATTLE_TYPE.TOURNAMENT, PREBATTLE_TYPE.CLAN)


def isParentControlActivated():
    from gui import game_control
    return game_control.g_instance.gameSession.isParentControlActive and not isTraining()


def getClientUnitMgr():
    return getattr(BigWorld.player(), 'unitMgr', None)


def getUnitMgrID():
    return getattr(getClientUnitMgr(), 'id', None)


def getUnitIdx():
    return getattr(getClientUnitMgr(), 'unitIdx', 0)


def getBattleID():
    return getattr(getClientUnitMgr(), 'battleID', 0)


def getClientUnitBrowser():
    return getattr(BigWorld.player(), 'unitBrowser', None)


def getUnit(unitIdx, safe = False):
    unitMgr = getClientUnitMgr()
    if not unitMgr:
        if not safe:
            raise ValueError('Unit manager not found')
        return
    else:
        unit = None
        try:
            unit = unitMgr.units[unitIdx]
        except KeyError:
            if not safe:
                raise ValueError('Unit not found')

        return unit


def hasModalEntity():
    return getClientPrebattle() or getUnitIdx()
