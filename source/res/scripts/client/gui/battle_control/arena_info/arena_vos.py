# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_vos.py
import operator
from debug_utils import LOG_ERROR
from gui.shared import fo_precache
from gui.shared.gui_items.Vehicle import getShortUserName
import nations
from collections import defaultdict
from constants import IGR_TYPE, FLAG_ACTION
from gui import makeHtmlString
from gui.server_events import g_eventsCache
from gui.battle_control.arena_info import settings, getPlayerVehicleID
from gui.battle_control.arena_info import isPlayerTeamKillSuspected
from items.vehicles import VEHICLE_CLASS_TAGS, PREMIUM_IGR_TAGS
from gui.shared.gui_items import Vehicle
_INVALIDATE_OP = settings.INVALIDATE_OP
_VEHICLE_STATUS = settings.VEHICLE_STATUS
_PLAYER_STATUS = settings.PLAYER_STATUS

def _getClassTag(tags):
    subSet = VEHICLE_CLASS_TAGS & tags
    result = None
    if len(subSet):
        result = list(subSet).pop()
    return result


def _isObserver(tags):
    if len(tags):
        result = bool(tags & frozenset(('observer',)))
    else:
        result = False
    return result


class PlayerInfoVO(object):
    __slots__ = ('accountDBID', 'name', 'clanAbbrev', 'igrType', 'potapovQuestIDs', 'isPrebattleCreator', 'forbidInBattleInvitations', 'tags')

    def __init__(self, accountDBID = 0L, name = None, clanAbbrev = '', igrType = IGR_TYPE.NONE, potapovQuestIDs = None, isPrebattleCreator = False, forbidInBattleInvitations = False, vehicleType = None, **kwargs):
        super(PlayerInfoVO, self).__init__()
        self.accountDBID = accountDBID
        self.name = name
        self.clanAbbrev = clanAbbrev
        self.igrType = igrType
        self.potapovQuestIDs = potapovQuestIDs or []
        self.isPrebattleCreator = isPrebattleCreator
        self.forbidInBattleInvitations = forbidInBattleInvitations
        self.tags = frozenset()
        if vehicleType is not None:
            vehicleType = vehicleType.type
            self.tags = vehicleType.tags.copy()
        return

    def __repr__(self):
        return 'PlayerInfoVO(accountDBID = {0:n}, name = {1:>s})'.format(self.accountDBID, self.name)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def update(self, invalidate = _INVALIDATE_OP.NONE, name = None, accountDBID = 0L, clanAbbrev = '', isPrebattleCreator = False, igrType = IGR_TYPE.NONE, forbidInBattleInvitations = False, **kwargs):
        if self.name != name:
            self.name = name
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.SORTING)
        self.accountDBID = accountDBID
        self.clanAbbrev = clanAbbrev
        self.igrType = igrType
        self.isPrebattleCreator = isPrebattleCreator
        self.forbidInBattleInvitations = forbidInBattleInvitations
        return invalidate

    def getPlayerLabel(self):
        if self.name:
            return self.name
        return settings.UNKNOWN_PLAYER_NAME

    def isIGR(self):
        return bool(self.tags & PREMIUM_IGR_TAGS)

    def getIGRLabel(self):
        if self.isIGR():
            igrLabel = makeHtmlString('html_templates:igr/iconBig', 'premium' if self.igrType == IGR_TYPE.PREMIUM else 'basic')
        else:
            igrLabel = ''
        return igrLabel

    def getRandomPotapovQuests(self):
        pQuests = g_eventsCache.random.getQuests()
        return self.__getPotapovQuests(pQuests)

    def getFalloutPotapovQuests(self):
        pQuests = g_eventsCache.fallout.getQuests()
        return self.__getPotapovQuests(pQuests)

    def __getPotapovQuests(self, pQuests):
        try:
            return map(lambda qID: pQuests[qID], self.potapovQuestIDs)
        except KeyError as e:
            LOG_ERROR('Key error trying to get potapov quests: no key in cache', e)
            return []


class VehicleTypeInfoVO(object):
    __slots__ = ('compactDescr', 'shortName', 'name', 'level', 'iconPath', 'isObserver', 'guiName', 'shortNameWithPrefix', 'classTag', 'nationID')

    def __init__(self, vehicleType = None, **kwargs):
        super(VehicleTypeInfoVO, self).__init__()
        self.__setVehicleData(vehicleType)

    def __repr__(self):
        return 'VehicleTypeInfoVO(compactDescr = {0:n})'.format(self.compactDescr)

    def __cmp__(self, other):
        result = cmp(other.level, self.level)
        if result:
            return result
        result = cmp(self.getOrderByClass(), other.getOrderByClass())
        if result:
            return result
        return cmp(self.shortName, other.shortName)

    def update(self, invalidate = _INVALIDATE_OP.NONE, vehicleType = None, **kwargs):
        if vehicleType is not None and self.compactDescr != vehicleType.type.compactDescr:
            self.__setVehicleData(vehicleType)
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.SORTING)
        return invalidate

    def __setVehicleData(self, vehicleDescr = None):
        if vehicleDescr is not None:
            vehicleType = vehicleDescr.type
            self.compactDescr = vehicleType.compactDescr
            tags = vehicleType.tags
            self.classTag = _getClassTag(tags)
            self.isObserver = _isObserver(tags)
            self.shortName = vehicleType.shortUserString
            self.name = Vehicle.getUserName(vehicleType=vehicleType, textPrefix=True)
            self.shortNameWithPrefix = Vehicle.getShortUserName(vehicleType=vehicleType, textPrefix=True)
            self.guiName = getShortUserName(vehicleType)
            self.nationID = vehicleType.id[0]
            self.level = vehicleType.level
            vName = vehicleType.name
            self.iconPath = settings.makeContourIconSFPath(vName)
            if not fo_precache.add(settings.makeContourIconResPath(vName)):
                self.iconPath = settings.UNKNOWN_CONTOUR_ICON_SF_PATH
        else:
            self.compactDescr = 0
            self.classTag = None
            self.isObserver = False
            self.shortName = settings.UNKNOWN_VEHICLE_NAME
            self.name = settings.UNKNOWN_VEHICLE_NAME
            self.guiName = settings.UNKNOWN_VEHICLE_NAME
            self.shortNameWithPrefix = settings.UNKNOWN_VEHICLE_NAME
            self.nationID = nations.NONE_INDEX
            self.level = settings.UNKNOWN_VEHICLE_LEVEL
            self.iconPath = settings.UNKNOWN_CONTOUR_ICON_SF_PATH
            self.shortNameWithPrefix = settings.UNKNOWN_VEHICLE_NAME
        return

    def getClassName(self):
        if self.classTag is not None:
            return self.classTag
        else:
            return settings.UNKNOWN_VEHICLE_CLASS_NAME
            return

    def getOrderByClass(self):
        return settings.getOrderByVehicleClass(self.classTag)


class VehicleArenaInfoVO(object):
    __slots__ = ('vehicleID', 'team', 'player', 'playerStatus', 'vehicleType', 'vehicleStatus', 'prebattleID', 'events', 'squadIndex')

    def __init__(self, vehicleID, team = 0, isAlive = None, isAvatarReady = None, isTeamKiller = None, prebattleID = None, events = None, **kwargs):
        super(VehicleArenaInfoVO, self).__init__()
        self.vehicleID = vehicleID
        self.team = team
        self.player = PlayerInfoVO(**kwargs)
        self.vehicleType = VehicleTypeInfoVO(**kwargs)
        self.prebattleID = prebattleID
        self.vehicleStatus = self.__getVehicleStatus(isAlive, isAvatarReady)
        self.playerStatus = self.__getPlayerStatus(isTeamKiller)
        self.events = events or {}
        self.squadIndex = 0

    def __repr__(self):
        return 'VehicleArenaInfoVO(vehicleID = {0!r:s}, team = {1!r:s}, player = {2!r:s}, playerStatus = {3:n}, vehicleType = {4!r:s}, vehicleStatus = {5:n}, prebattleID = {6!r:s})'.format(self.vehicleID, self.team, self.player, self.playerStatus, self.vehicleType, self.vehicleStatus, self.prebattleID)

    def __cmp__(self, other):
        result = cmp(self.team, other.team)
        if result:
            return result
        result = cmp(other.isAlive(), self.isAlive())
        if result:
            return result
        result = cmp(self.vehicleType, other.vehicleType)
        if result:
            return result
        return cmp(self.player, other.player)

    def updateVehicleStatus(self, invalidate = _INVALIDATE_OP.NONE, isAlive = None, isAvatarReady = None, **kwargs):
        prev, self.vehicleStatus = self.vehicleStatus, self.__getVehicleStatus(isAlive, isAvatarReady)
        diff = self.vehicleStatus ^ prev
        if diff:
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.VEHICLE_STATUS)
            if diff & _VEHICLE_STATUS.IS_ALIVE > 0:
                invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.SORTING)
        return invalidate

    def updatePlayerStatus(self, invalidate = _INVALIDATE_OP.NONE, isTeamKiller = None, isSquadMan = None, **kwargs):
        if isTeamKiller:
            status = _PLAYER_STATUS.addIfNot(self.playerStatus, _PLAYER_STATUS.IS_TEAM_KILLER)
            if self.playerStatus ^ status:
                self.playerStatus = status
                invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.PLAYER_STATUS)
        if isSquadMan:
            status = _PLAYER_STATUS.addIfNot(self.playerStatus, _PLAYER_STATUS.IS_SQUAD_MAN)
            if self.playerStatus ^ status:
                self.playerStatus = status
                invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.PLAYER_STATUS)
        return invalidate

    def update(self, **kwargs):
        invalidate = _INVALIDATE_OP.VEHICLE_INFO
        newPrbID = kwargs.get('prebattleID', 0)
        if self.prebattleID != newPrbID:
            self.prebattleID = newPrbID
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.PREBATTLE_CHANGED)
        invalidate = self.player.update(invalidate=invalidate, **kwargs)
        invalidate = self.vehicleType.update(invalidate=invalidate, **kwargs)
        invalidate = self.updateVehicleStatus(invalidate=invalidate, **kwargs)
        invalidate = self.updatePlayerStatus(invalidate=invalidate, **kwargs)
        return invalidate

    def getSquadID(self):
        if self.isSquadMan():
            return self.prebattleID
        return 0

    def isSquadMan(self, prebattleID = None, playerTeam = None):
        if playerTeam and self.team != playerTeam:
            return False
        elif prebattleID is not None and self.prebattleID != prebattleID:
            return False
        else:
            return self.playerStatus & _PLAYER_STATUS.IS_SQUAD_MAN > 0
            return

    def isTeamKiller(self, playerTeam = None):
        if playerTeam and self.team != playerTeam:
            return False
        elif self.vehicleID == getPlayerVehicleID() and isPlayerTeamKillSuspected():
            return True
        else:
            return self.playerStatus & _PLAYER_STATUS.IS_TEAM_KILLER > 0

    def getPlayerStatusInTeam(self, playerTeam = None):
        playerStatus = 0
        if self.isSquadMan():
            playerStatus |= _PLAYER_STATUS.IS_SQUAD_MAN
        if self.isTeamKiller(playerTeam=playerTeam):
            playerStatus |= _PLAYER_STATUS.IS_TEAM_KILLER
        return playerStatus

    def isAlive(self):
        return self.vehicleStatus & _VEHICLE_STATUS.IS_ALIVE > 0

    def isReady(self):
        return self.vehicleStatus & _VEHICLE_STATUS.IS_READY > 0

    def isObserver(self):
        return self.vehicleType.isObserver

    def isActionsDisabled(self):
        return not self.player.accountDBID

    def getTypeInfo(self):
        return (self.vehicleType.classTag, self.vehicleType.level, nations.NAMES[self.vehicleType.nationID])

    def __getVehicleStatus(self, isAlive = None, isAvatarReady = None):
        vehicleStatus = 0
        if isAlive:
            vehicleStatus |= _VEHICLE_STATUS.IS_ALIVE
        if isAvatarReady:
            vehicleStatus |= _VEHICLE_STATUS.IS_READY
        if isAlive is None or isAvatarReady is None:
            vehicleStatus = _VEHICLE_STATUS.NOT_AVAILABLE
        return vehicleStatus

    def __getPlayerStatus(self, isTeamKiller = None):
        playerStatus = 0
        if isTeamKiller:
            playerStatus |= _PLAYER_STATUS.IS_TEAM_KILLER
        return playerStatus


class VehicleArenaStatsVO(object):
    __slots__ = ('vehicleID', 'frags')

    def __init__(self, vehicleID, frags = 0, **kwargs):
        super(VehicleArenaStatsVO, self).__init__()
        self.vehicleID = vehicleID
        self.frags = frags

    def __repr__(self):
        return 'VehicleArenaStatsVO(vehicleID = {0:n}, frags = {1:n})'.format(self.vehicleID, self.frags)

    def update(self, frags = None, **kwargs):
        self.frags = frags
        return _INVALIDATE_OP.VEHICLE_STATS


class VehicleArenaStatsDict(defaultdict):

    def __missing__(self, key):
        self[key] = value = VehicleArenaStatsVO(key)
        return value


class VehicleArenaInteractiveStatsVO(object):
    __slots__ = ('vehicleID', 'xp', 'damageDealt', 'capturePts', 'flagActions', 'winPoints', 'deathCount', 'resourceAbsorbed', 'stopRespawn', 'equipmentDamage', 'equipmentKills')

    def __init__(self, vehicleID, xp = 0, damageDealt = 0, capturePts = 0, flagActions = None, winPoints = 0, deathCount = 0, resourceAbsorbed = 0, stopRespawn = False, equipmentDamage = 0, equipmentKills = 0, *args):
        super(VehicleArenaInteractiveStatsVO, self).__init__()
        self.vehicleID = vehicleID
        self.xp = xp
        self.damageDealt = damageDealt
        self.capturePts = capturePts
        self.flagActions = flagActions or [0] * len(FLAG_ACTION.RANGE)
        self.winPoints = winPoints
        self.deathCount = deathCount
        self.resourceAbsorbed = resourceAbsorbed
        self.stopRespawn = stopRespawn
        self.equipmentDamage = equipmentDamage
        self.equipmentKills = equipmentKills

    def update(self, xp = 0, damageDealt = 0, capturePts = 0, flagActions = None, winPoints = 0, deathCount = 0, resourceAbsorbed = 0, stopRespawn = False, equipmentDamage = 0, equipmentKills = 0, *args):
        self.xp += xp
        self.damageDealt += damageDealt
        self.capturePts += capturePts
        if flagActions is not None:
            self.flagActions = map(operator.add, self.flagActions, flagActions)
        self.winPoints += winPoints
        self.deathCount += deathCount
        self.resourceAbsorbed += resourceAbsorbed
        self.stopRespawn = self.stopRespawn or stopRespawn
        self.equipmentDamage += equipmentDamage
        self.equipmentKills += equipmentKills
        return _INVALIDATE_OP.VEHICLE_STATS


class VehicleArenaInteractiveStatsDict(defaultdict):

    def __missing__(self, key):
        self[key] = value = VehicleArenaInteractiveStatsVO(key)
        return value


class VehicleActions(object):
    """
    Represent vehicleActionMarker convertion action to bitMask
    """
    __ACTIONS = {'hunting': 1}

    @staticmethod
    def getBitMask(actions):
        bitMask = 0
        for key, value in actions.items():
            mask = VehicleActions.__ACTIONS.get(key, 0)
            if isinstance(mask, dict):
                mask = mask.get(value, 0)
            bitMask |= mask

        return bitMask

    @staticmethod
    def isHunting(actions):
        return 'hunting' in actions.keys()
