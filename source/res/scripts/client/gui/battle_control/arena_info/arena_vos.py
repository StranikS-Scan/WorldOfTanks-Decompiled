# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/arena_vos.py
import operator
from collections import defaultdict
import nations
from constants import IGR_TYPE, FLAG_ACTION
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.battle_control import avatar_getter, vehicle_getter
from gui.battle_control.arena_info import settings
from gui.server_events import g_eventsCache
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.Vehicle import getShortUserName, VEHICLE_TAGS
from items.vehicles import VEHICLE_CLASS_TAGS
_INVALIDATE_OP = settings.INVALIDATE_OP
_VEHICLE_STATUS = settings.VEHICLE_STATUS
_PLAYER_STATUS = settings.PLAYER_STATUS
_DELIVERY_STATUS = settings.INVITATION_DELIVERY_STATUS

def getClassTag(tags):
    subSet = VEHICLE_CLASS_TAGS & tags
    result = None
    if len(subSet):
        result = list(subSet).pop()
    return result


def isObserver(tags):
    return VEHICLE_TAGS.OBSERVER in tags


def isPremium(tags):
    return VEHICLE_TAGS.PREMIUM in tags


def isPremiumIGR(tags):
    return VEHICLE_TAGS.PREMIUM_IGR in tags


def isMark1(tags):
    return VEHICLE_TAGS.MARK1 in tags


class PlayerInfoVO(object):
    __slots__ = ('accountDBID', 'name', 'clanAbbrev', 'igrType', 'potapovQuestIDs', 'isPrebattleCreator', 'forbidInBattleInvitations')

    def __init__(self, accountDBID=0L, name=None, clanAbbrev='', igrType=IGR_TYPE.NONE, potapovQuestIDs=None, isPrebattleCreator=False, forbidInBattleInvitations=False, **kwargs):
        super(PlayerInfoVO, self).__init__()
        self.accountDBID = accountDBID
        self.name = name
        self.clanAbbrev = clanAbbrev
        self.igrType = igrType
        self.potapovQuestIDs = potapovQuestIDs or []
        self.isPrebattleCreator = isPrebattleCreator
        self.forbidInBattleInvitations = forbidInBattleInvitations

    def __repr__(self):
        return 'PlayerInfoVO(accountDBID = {0:n}, name = {1:>s})'.format(self.accountDBID, self.name)

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def update(self, invalidate=_INVALIDATE_OP.NONE, name=None, accountDBID=0L, clanAbbrev='', isPrebattleCreator=False, igrType=IGR_TYPE.NONE, forbidInBattleInvitations=False, **kwargs):
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
        return self.name if self.name else settings.UNKNOWN_PLAYER_NAME

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
    __slots__ = ('compactDescr', 'shortName', 'name', 'level', 'iconName', 'iconPath', 'isObserver', 'isPremiumIGR', 'guiName', 'shortNameWithPrefix', 'classTag', 'nationID', 'turretYawLimits', 'maxHealth', 'isMark1')

    def __init__(self, vehicleType=None, **kwargs):
        super(VehicleTypeInfoVO, self).__init__()
        self.__setVehicleData(vehicleType)

    def __repr__(self):
        return 'VehicleTypeInfoVO(compactDescr = {0:n})'.format(self.compactDescr)

    def __cmp__(self, other):
        result = cmp(other.level, self.level)
        if result:
            return result
        result = cmp(self.getOrderByClass(), other.getOrderByClass())
        return result if result else cmp(self.shortName, other.shortName)

    def update(self, invalidate=_INVALIDATE_OP.NONE, vehicleType=None, **kwargs):
        if vehicleType is not None and self.compactDescr != vehicleType.type.compactDescr:
            self.__setVehicleData(vehicleType)
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.SORTING)
        return invalidate

    def __setVehicleData(self, vehicleDescr=None):
        if vehicleDescr is not None:
            vehicleType = vehicleDescr.type
            self.compactDescr = vehicleType.compactDescr
            tags = vehicleType.tags
            self.classTag = getClassTag(tags)
            self.isObserver = isObserver(tags)
            self.isPremiumIGR = isPremiumIGR(tags)
            self.isMark1 = isMark1(tags)
            self.turretYawLimits = vehicle_getter.getYawLimits(vehicleDescr)
            self.shortName = vehicleType.shortUserString
            self.name = Vehicle.getUserName(vehicleType=vehicleType, textPrefix=True)
            self.shortNameWithPrefix = Vehicle.getShortUserName(vehicleType=vehicleType, textPrefix=True)
            self.guiName = getShortUserName(vehicleType)
            self.nationID = vehicleType.id[0]
            self.level = vehicleType.level
            self.maxHealth = vehicleDescr.maxHealth
            vName = vehicleType.name
            self.iconName = settings.makeVehicleIconName(vName)
            self.iconPath = settings.makeContourIconSFPath(vName)
            if not settings.addContourIconToCache(vName):
                self.iconName = settings.UNKNOWN_CONTOUR_ICON_NAME
                self.iconPath = settings.UNKNOWN_CONTOUR_ICON_SF_PATH
        else:
            self.compactDescr = 0
            self.classTag = None
            self.isObserver = False
            self.isPremiumIGR = False
            self.isMark1 = False
            self.turretYawLimits = None
            self.shortName = settings.UNKNOWN_VEHICLE_NAME
            self.name = settings.UNKNOWN_VEHICLE_NAME
            self.guiName = settings.UNKNOWN_VEHICLE_NAME
            self.shortNameWithPrefix = settings.UNKNOWN_VEHICLE_NAME
            self.nationID = nations.NONE_INDEX
            self.level = settings.UNKNOWN_VEHICLE_LEVEL
            self.iconName = settings.UNKNOWN_CONTOUR_ICON_NAME
            self.iconPath = settings.UNKNOWN_CONTOUR_ICON_SF_PATH
            self.shortNameWithPrefix = settings.UNKNOWN_VEHICLE_NAME
            self.maxHealth = None
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
    __slots__ = ('vehicleID', 'team', 'player', 'playerStatus', 'vehicleType', 'vehicleStatus', 'prebattleID', 'events', 'squadIndex', 'invitationDeliveryStatus')

    def __init__(self, vehicleID, team=0, isAlive=None, isAvatarReady=None, isTeamKiller=None, prebattleID=None, events=None, forbidInBattleInvitations=False, **kwargs):
        super(VehicleArenaInfoVO, self).__init__()
        self.vehicleID = vehicleID
        self.team = team
        self.player = PlayerInfoVO(forbidInBattleInvitations=forbidInBattleInvitations, **kwargs)
        self.vehicleType = VehicleTypeInfoVO(**kwargs)
        self.prebattleID = prebattleID
        self.vehicleStatus = self.__getVehicleStatus(isAlive, isAvatarReady)
        self.playerStatus = self.__getPlayerStatus(isTeamKiller)
        self.invitationDeliveryStatus = self.__getInvitationStatus(forbidInBattleInvitations)
        self.events = events or {}
        self.squadIndex = 0

    def __repr__(self):
        return 'VehicleArenaInfoVO(vehicleID = {0!r:s}, team = {1!r:s}, player = {2!r:s}, playerStatus = {3:n}, vehicleType = {4!r:s}, vehicleStatus = {5:n}, prebattleID = {6!r:s})'.format(self.vehicleID, self.team, self.player, self.playerStatus, self.vehicleType, self.vehicleStatus, self.prebattleID)

    def __eq__(self, other):
        return self.vehicleID == other.vehicleID

    def __cmp__(self, other):
        result = cmp(self.team, other.team)
        if result:
            return result
        result = cmp(other.isAlive(), self.isAlive())
        if result:
            return result
        result = cmp(self.vehicleType, other.vehicleType)
        return result if result else cmp(self.player, other.player)

    def updateVehicleStatus(self, invalidate=_INVALIDATE_OP.NONE, isAlive=None, isAvatarReady=None, stopRespawn=False, **kwargs):
        prev, self.vehicleStatus = self.vehicleStatus, self.__getVehicleStatus(isAlive, isAvatarReady, stopRespawn)
        diff = self.vehicleStatus ^ prev
        if diff:
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.VEHICLE_STATUS)
            if diff & _VEHICLE_STATUS.IS_ALIVE > 0 or diff & _VEHICLE_STATUS.STOP_RESPAWN > 0:
                invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.SORTING)
        return invalidate

    def updatePlayerStatus(self, invalidate=_INVALIDATE_OP.NONE, isTeamKiller=None, isSquadMan=None, **kwargs):
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

    def updateInvitationStatus(self, invalidate=_INVALIDATE_OP.NONE, include=_DELIVERY_STATUS.NONE, exclude=_DELIVERY_STATUS.NONE, forbidInBattleInvitations=False, **kwargs):
        status = self.invitationDeliveryStatus
        if forbidInBattleInvitations:
            status = _DELIVERY_STATUS.addIfNot(status, _DELIVERY_STATUS.FORBIDDEN_BY_RECEIVER)
        status = _DELIVERY_STATUS.addIfNot(status, include)
        status = _DELIVERY_STATUS.removeIfHas(status, exclude)
        if self.invitationDeliveryStatus ^ status:
            self.invitationDeliveryStatus = status
            invalidate = _INVALIDATE_OP.addIfNot(invalidate, _INVALIDATE_OP.INVITATION_DELIVERY_STATUS)
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
        invalidate = self.updateInvitationStatus(invalidate=invalidate, **kwargs)
        return invalidate

    def getSquadID(self):
        return self.prebattleID if self.isSquadMan() else 0

    def isSquadMan(self, prebattleID=None, playerTeam=None):
        if playerTeam and self.team != playerTeam:
            return False
        elif prebattleID is not None and self.prebattleID != prebattleID:
            return False
        else:
            return self.playerStatus & _PLAYER_STATUS.IS_SQUAD_MAN > 0
            return

    def isSquadCreator(self):
        return self.player.isPrebattleCreator and self.isSquadMan()

    def isTeamKiller(self, playerTeam=None):
        if playerTeam is not None and self.team != playerTeam:
            return False
        elif self.vehicleID == avatar_getter.getPlayerVehicleID() and avatar_getter.isPlayerTeamKillSuspected():
            return True
        else:
            return self.playerStatus & _PLAYER_STATUS.IS_TEAM_KILLER > 0
            return

    def getPlayerStatusInTeam(self, playerTeam=None):
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

    def getIGRLabel(self):
        if self.vehicleType.isPremiumIGR:
            if self.player.igrType == IGR_TYPE.PREMIUM:
                key = 'premium'
            else:
                key = 'basic'
            igrLabel = makeHtmlString('html_templates:igr/iconBig', key)
        else:
            igrLabel = ''
        return igrLabel

    @staticmethod
    def __getVehicleStatus(isAlive=None, isAvatarReady=None, stopRespawn=False):
        vehicleStatus = _VEHICLE_STATUS.DEFAULT
        if isAlive:
            vehicleStatus |= _VEHICLE_STATUS.IS_ALIVE
        if isAvatarReady:
            vehicleStatus |= _VEHICLE_STATUS.IS_READY
        if isAlive is None or isAvatarReady is None:
            vehicleStatus = _VEHICLE_STATUS.NOT_AVAILABLE
        if stopRespawn:
            vehicleStatus |= _VEHICLE_STATUS.STOP_RESPAWN
        return vehicleStatus

    def __getPlayerStatus(self, isTeamKiller=None):
        playerStatus = _PLAYER_STATUS.DEFAULT
        if isTeamKiller:
            playerStatus |= _PLAYER_STATUS.IS_TEAM_KILLER
        if self.isActionsDisabled():
            playerStatus |= _PLAYER_STATUS.IS_ACTION_DISABLED
        return playerStatus

    @staticmethod
    def __getInvitationStatus(forbidInBattleInvitations=False):
        invitationStatus = _DELIVERY_STATUS.NONE
        if forbidInBattleInvitations:
            invitationStatus = _DELIVERY_STATUS.FORBIDDEN_BY_RECEIVER
        return invitationStatus


class VehicleArenaInteractiveStatsVO(object):
    __slots__ = ('xp', 'damageDealt', 'capturePts', 'flagActions', 'winPoints', 'deathCount', 'resourceAbsorbed', 'stopRespawn', 'equipmentDamage', 'equipmentKills', 'teamWinPoints', 'team')

    def __init__(self, xp=0, damageDealt=0, capturePts=0, flagActions=None, winPoints=0, deathCount=0, resourceAbsorbed=0, stopRespawn=False, equipmentDamage=0, equipmentKills=0, *args):
        super(VehicleArenaInteractiveStatsVO, self).__init__()
        self.xp = xp
        self.damageDealt = damageDealt
        self.capturePts = capturePts
        self.flagActions = flagActions or (0,) * len(FLAG_ACTION.RANGE)
        self.winPoints = winPoints
        self.deathCount = deathCount
        self.resourceAbsorbed = resourceAbsorbed
        self.stopRespawn = stopRespawn
        self.equipmentDamage = equipmentDamage
        self.equipmentKills = equipmentKills
        self.teamWinPoints = 0

    def clear(self):
        self.xp = 0
        self.damageDealt = 0
        self.capturePts = 0
        self.flagActions = (0,) * len(FLAG_ACTION.RANGE)
        self.winPoints = 0
        self.deathCount = 0
        self.resourceAbsorbed = 0
        self.stopRespawn = False
        self.equipmentDamage = 0
        self.equipmentKills = 0
        self.teamWinPoints = 0

    def update(self, xp=0, damageDealt=0, capturePts=0, flagActions=None, winPoints=0, deathCount=0, resourceAbsorbed=0, stopRespawn=False, equipmentDamage=0, equipmentKills=0, *args):
        result = _INVALIDATE_OP.VEHICLE_ISTATS
        self.xp += xp
        self.damageDealt += damageDealt
        self.capturePts += capturePts
        if flagActions is not None:
            self.flagActions = map(operator.add, self.flagActions, flagActions)
        if winPoints:
            result |= _INVALIDATE_OP.SORTING
        self.winPoints += winPoints
        self.deathCount += deathCount
        self.resourceAbsorbed += resourceAbsorbed
        self.stopRespawn = self.stopRespawn or stopRespawn
        self.equipmentDamage += equipmentDamage
        self.equipmentKills += equipmentKills
        return result

    def getCapturedFlags(self):
        return self.flagActions[FLAG_ACTION.CAPTURED]

    def getTotalDamage(self):
        return self.damageDealt + self.equipmentDamage


class VehicleArenaStatsVO(object):
    """Value object containing statistics that are related to vehicles."""
    __slots__ = ('vehicleID', '__frags', '__interactive')

    def __init__(self, vehicleID, frags=0, **kwargs):
        super(VehicleArenaStatsVO, self).__init__()
        self.vehicleID = vehicleID
        self.__frags = frags
        self.__interactive = None
        return

    def __repr__(self):
        return 'VehicleArenaStatsVO(vehicleID = {}, frags = {}, interactive = {})'.format(self.vehicleID, self.__frags, self.__interactive)

    @property
    def frags(self):
        if self.__interactive is not None:
            return self.__frags + self.__interactive.equipmentKills
        else:
            return self.__frags
            return

    @property
    def interactive(self):
        if self.__interactive is None:
            self.__interactive = VehicleArenaInteractiveStatsVO()
        return self.__interactive

    @property
    def stopRespawn(self):
        if self.__interactive is not None:
            return self.__interactive.stopRespawn
        else:
            return False
            return

    @property
    def winPoints(self):
        if self.__interactive is not None:
            return self.__interactive.winPoints
        else:
            return 0
            return

    def clearInteractiveStats(self):
        if self.__interactive is not None:
            self.__interactive.clear()
        return

    def updateInteractiveStats(self, *args):
        if self.__interactive is None:
            self.__interactive = VehicleArenaInteractiveStatsVO()
        return self.__interactive.update(*args)

    def updateVehicleStats(self, frags=None, **kwargs):
        if frags is not None:
            self.__frags = frags
            return _INVALIDATE_OP.VEHICLE_STATS
        else:
            return _INVALIDATE_OP.NONE
            return


class VehicleArenaStatsDict(defaultdict):

    def __missing__(self, key):
        self[key] = value = VehicleArenaStatsVO(key)
        return value

    def clearInteractiveStats(self):
        for vo in self.itervalues():
            vo.clearInteractiveStats()


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
