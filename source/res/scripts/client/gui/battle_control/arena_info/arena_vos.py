# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_vos.py
from collections import defaultdict
from constants import IGR_TYPE, ARENA_GUI_TYPE
from gui import makeHtmlString
from gui.server_events import g_eventsCache
from gui.battle_control.arena_info import getArenaGuiType
from gui.battle_control.arena_info.settings import *
from items.vehicles import VEHICLE_CLASS_TAGS, getVehicleType, PREMIUM_IGR_TAGS

class PlayerInfoVO(object):
    __slots__ = ('accountDBID', 'name', 'clanAbbrev', 'igrType', 'potapovQuestIDs')

    def __init__(self, accountDBID = 0L, name = None, clanAbbrev = '', igrType = IGR_TYPE.NONE, potapovQuestIDs = None, **kwargs):
        super(PlayerInfoVO, self).__init__()
        self.accountDBID = accountDBID
        self.name = name
        self.clanAbbrev = clanAbbrev
        self.igrType = igrType
        self.potapovQuestIDs = potapovQuestIDs or []

    def __repr__(self):
        return 'PlayerInfoVO(accountDBID = {0:n}, name = {1:>s})'.format(self.accountDBID, self.name)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def update(self, invalidate = INVALIDATE_OP.NONE, name = None, accountDBID = 0L, clanAbbrev = '', igrType = IGR_TYPE.NONE, **kwargs):
        if self.name != name:
            self.name = name
            invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.SORTING)
        self.accountDBID = accountDBID
        self.clanAbbrev = clanAbbrev
        self.igrType = igrType
        return invalidate

    def getPlayerLabel(self):
        if self.name:
            return self.name
        return UNKNOWN_PLAYER_NAME

    def isIGR(self):
        return self.igrType != IGR_TYPE.NONE

    def getIGRLabel(self):
        if self.isIGR():
            igrLabel = makeHtmlString('html_templates:igr/iconBig', 'premium' if self.igrType == IGR_TYPE.PREMIUM else 'basic')
        else:
            igrLabel = ''
        return igrLabel

    def getPotapovQuests(self):
        pQuests = g_eventsCache.potapov.getQuests()
        return map(lambda qID: pQuests[qID], self.potapovQuestIDs)


class VehicleTypeInfoVO(object):
    __slots__ = ('compactDescr', 'shortName', 'name', 'level', 'iconPath', 'tags')

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

    def update(self, invalidate = INVALIDATE_OP.NONE, vehicleType = None, **kwargs):
        if self.compactDescr == 0 and vehicleType is not None:
            self.__setVehicleData(vehicleType)
            invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.SORTING)
        return invalidate

    def __setVehicleData(self, vehicleDescr = None):
        if vehicleDescr is not None:
            vehicleType = vehicleDescr.type
            if getArenaGuiType() == ARENA_GUI_TYPE.HISTORICAL and getattr(vehicleType, 'historicalModelOf', None):
                vehicleType = getVehicleType(vehicleType.historicalModelOf)
            self.compactDescr = vehicleType.compactDescr
            self.tags = vehicleType.tags.copy()
            self.shortName = vehicleType.shortUserString
            self.name = vehicleType.shortUserString if self.isPremiumIGR() else vehicleType.userString
            self.level = vehicleType.level
            self.iconPath = makeContourIconPath(vehicleType.name)
        else:
            self.compactDescr = 0
            self.tags = frozenset()
            self.shortName = UNKNOWN_VEHICLE_NAME
            self.name = UNKNOWN_VEHICLE_NAME
            self.level = UNKNOWN_VEHICLE_LEVEL
            self.iconPath = UNKNOWN_CONTOUR_ICON_PATH
        return

    def getClassTag(self):
        tags = VEHICLE_CLASS_TAGS & self.tags
        result = None
        if len(tags):
            result = list(tags).pop()
        return result

    def isPremiumIGR(self):
        return bool(self.tags & PREMIUM_IGR_TAGS)

    def getClassName(self):
        result = self.getClassTag()
        if result:
            return result
        return UNKNOWN_VEHICLE_CLASS_NAME

    def getOrderByClass(self):
        return getOrderByVehicleClass(self.getClassTag())


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
        result = cmp(other.isAlive(), self.isAlive())
        if result:
            return result
        result = cmp(self.vehicleType, other.vehicleType)
        if result:
            return result
        return cmp(self.player, other.player)

    def updateVehicleStatus(self, invalidate = INVALIDATE_OP.NONE, isAlive = None, isAvatarReady = None, **kwargs):
        prev, self.vehicleStatus = self.vehicleStatus, self.__getVehicleStatus(isAlive, isAvatarReady)
        diff = self.vehicleStatus ^ prev
        if diff:
            invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.VEHICLE_STATUS)
            if diff & VEHICLE_STATUS.IS_ALIVE > 0:
                invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.SORTING)
        return invalidate

    def updatePlayerStatus(self, invalidate = INVALIDATE_OP.NONE, isTeamKiller = None, isSquadMan = None, **kwargs):
        if isTeamKiller:
            status = PLAYER_STATUS.addIfNot(self.playerStatus, PLAYER_STATUS.IS_TEAM_KILLER)
            if self.playerStatus ^ status:
                self.playerStatus = status
                invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.PLAYER_STATUS)
        if isSquadMan:
            status = PLAYER_STATUS.addIfNot(self.playerStatus, PLAYER_STATUS.IS_SQUAD_MAN)
            if self.playerStatus ^ status:
                self.playerStatus = status
                invalidate = INVALIDATE_OP.addIfNot(invalidate, INVALIDATE_OP.PLAYER_STATUS)
        return invalidate

    def update(self, **kwargs):
        invalidate = INVALIDATE_OP.VEHICLE_INFO
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
            return self.playerStatus & PLAYER_STATUS.IS_SQUAD_MAN > 0
            return

    def isTeamKiller(self, playerTeam = None):
        if playerTeam and self.team != playerTeam:
            return False
        else:
            return self.playerStatus & PLAYER_STATUS.IS_TEAM_KILLER > 0

    def getPlayerStatusInTeam(self, playerTeam = None):
        playerStatus = 0
        if self.isSquadMan():
            playerStatus |= PLAYER_STATUS.IS_SQUAD_MAN
        if self.isTeamKiller(playerTeam=playerTeam):
            playerStatus |= PLAYER_STATUS.IS_TEAM_KILLER
        return playerStatus

    def isAlive(self):
        return self.vehicleStatus & VEHICLE_STATUS.IS_ALIVE > 0

    def isReady(self):
        return self.vehicleStatus & VEHICLE_STATUS.IS_READY > 0

    def isObserver(self):
        tags = self.vehicleType.tags
        if len(tags):
            return bool(tags & frozenset(('observer',)))
        result = False
        return result

    def __getVehicleStatus(self, isAlive = None, isAvatarReady = None):
        vehicleStatus = 0
        if isAlive:
            vehicleStatus |= VEHICLE_STATUS.IS_ALIVE
        if isAvatarReady:
            vehicleStatus |= VEHICLE_STATUS.IS_READY
        if isAlive is None or isAvatarReady is None:
            vehicleStatus = VEHICLE_STATUS.NOT_AVAILABLE
        return vehicleStatus

    def __getPlayerStatus(self, isTeamKiller = None):
        playerStatus = 0
        if isTeamKiller:
            playerStatus |= PLAYER_STATUS.IS_TEAM_KILLER
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
        return INVALIDATE_OP.VEHICLE_STATS


class VehicleArenaStatsDict(defaultdict):

    def __missing__(self, key):
        self[key] = value = VehicleArenaStatsVO(key)
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
