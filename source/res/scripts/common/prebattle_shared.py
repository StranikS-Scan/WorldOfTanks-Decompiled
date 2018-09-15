# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/prebattle_shared.py
import nations
from items import vehicles, ITEM_TYPES
from account_shared import AmmoIterator
from constants import PREBATTLE_ACCOUNT_STATE, VEHICLE_CLASSES, ARENA_GUI_TYPE, PREBATTLE_ROLE, IGR_TYPE, IS_DEVELOPMENT
from debug_utils import LOG_DEBUG

def decodeRoster(roster):
    return (roster & 15, not roster & 240)


def encodeRoster(team, assigned):
    return team | (not assigned) << 4


def isVehicleValid(vehDescr, vehAmmo, limits):
    minLevel, maxLevel = limits['level']
    classLevelLimits = limits['classLevel']
    for classTag in VEHICLE_CLASSES:
        if classTag not in vehDescr.type.tags:
            continue
        if classTag in classLevelLimits:
            classMinLevel, classMaxLevel = classLevelLimits[classTag]
            if not classMinLevel <= vehDescr.level <= classMaxLevel:
                return (False, 'limits/classLevel')
        if not minLevel <= vehDescr.level <= maxLevel:
            return (False, 'limits/level')

    classesLimits = limits['classes']
    if classesLimits is not None:
        for classTag in VEHICLE_CLASSES:
            if classTag in vehDescr.type.tags and classTag not in classesLimits:
                return (False, 'limits/classes')

    nationLimits = limits['nations']
    if nationLimits is not None and nations.NAMES[vehDescr.type.id[0]] not in nationLimits:
        return (False, 'limits/nations')
    else:
        vehTypeCompDescr = vehDescr.type.compactDescr
        vehicleLimits = limits['vehicles']
        if vehicleLimits is not None and vehTypeCompDescr not in vehicleLimits:
            return (False, 'limits/vehicles')
        componentLimits = limits['components'].get(vehTypeCompDescr, None)
        if componentLimits is not None:
            isValid, components = componentLimits
            for compDescr in _collectCurrentReplaceableVehicleComponents(vehDescr):
                if isValid and compDescr not in components:
                    return (False, 'limits/components')
                if not isValid and compDescr in components:
                    return (False, 'limits/components')

        ammoLimits = limits['ammo']
        if ammoLimits is not None:
            isValid, ammoSet = ammoLimits
            for compDescr, count in AmmoIterator(vehAmmo):
                if compDescr == 0 or count == 0:
                    continue
                if isValid and compDescr not in ammoSet:
                    return (False, 'limits/ammo')
                if not isValid and compDescr in ammoSet:
                    return (False, 'limits/ammo')

        shellsLimits = limits['shells']
        if shellsLimits:
            for compDescr, count in AmmoIterator(vehAmmo):
                if compDescr == 0 or count == 0:
                    continue
                itemTypeIdx = vehicles.parseIntCompactDescr(compDescr)[0]
                if itemTypeIdx != ITEM_TYPES.shell:
                    continue
                if count > shellsLimits.get(compDescr, 65535):
                    return (False, 'limits/shells')

        tagsLimits = limits['tags']
        if tagsLimits is not None:
            isValid, tagSet = tagsLimits
            for tag in tagSet:
                if isValid and tag not in vehDescr.type.tags:
                    return (False, 'limits/tags')
                if not isValid and tag in vehDescr.type.tags:
                    return (False, 'limits/tags')

        return (True, None)


def isObserver(vehCompDescr):
    return bool(vehCompDescr) and 'observer' in vehicles.getVehicleType(vehCompDescr).tags


def isTeamValid(accountsInfo, limits):
    minLevel, maxLevel = limits['level']
    tagsLimits = limits['tags']
    count = 0
    totalLevel = 0
    observerCount = 0
    vehs = {}
    for accInfo in accountsInfo.itervalues():
        if not accInfo['state'] & PREBATTLE_ACCOUNT_STATE.READY:
            continue
        if 'vehTypeCompDescr' not in accInfo or 'vehLevel' not in accInfo:
            vehDescr = vehicles.VehicleDescr(compactDescr=accInfo['vehCompDescr'])
            vehLevel = vehDescr.level
            vehTypeCompDescr = vehDescr.type.compactDescr
        else:
            vehLevel = accInfo['vehLevel']
            vehTypeCompDescr = accInfo['vehTypeCompDescr']
        if not minLevel <= vehLevel <= maxLevel:
            return (False, 'limits/level')
        vehTags = vehicles.getVehicleType(vehTypeCompDescr).tags
        if tagsLimits is not None:
            isValid, tagSet = tagsLimits
            for tag in tagSet:
                if isValid and tag not in vehTags:
                    return (False, 'limits/tags')
                if not isValid and tag in vehTags:
                    return (False, 'limits/tags')

        count += 1
        observerCount += int('observer' in vehTags)
        totalLevel += vehLevel
        vehs[vehTypeCompDescr] = vehs.get(vehTypeCompDescr, 0) + 1

    if count < limits['minCount']:
        return (False, 'limit/minCount')
    else:
        if observerCount > 0 and count == observerCount:
            if not IS_DEVELOPMENT:
                return (False, 'limit/observerVehicles')
            LOG_DEBUG('Ignoring limit for observers in development mode.')
        minTotalLevel, maxTotalLevel = limits['totalLevel']
        if not minTotalLevel <= totalLevel <= maxTotalLevel:
            return (False, 'limit/totalLevel')
        vehicleLimits = limits['vehicles']
        if vehicleLimits is not None:
            for vehTypeCompDescr, (minCount, maxCount) in vehicleLimits.iteritems():
                count = vehs.get(vehTypeCompDescr, 0)
                if not minCount <= count <= maxCount:
                    return (False, 'limits/vehicles')

        return (True, '')


class PrebattleSettings(object):

    def __init__(self, settings):
        self.__settings = settings

    def __getitem__(self, key):
        return self.__settings[key] if key in self.__settings else SETTING_DEFAULTS[key]

    def __setitem__(self, key, value):
        self.__settings[key] = value

    def getTeamLimits(self, team):
        return TeamLimits(self.__settings, team)


class TeamLimits(object):

    def __init__(self, settings, team):
        self.__limits = settings['limits']
        self.__team = team

    def __getitem__(self, key):
        if key in self.__limits[self.__team]:
            return self.__limits[self.__team][key]
        return self.__limits[0][key] if key in self.__limits.get(0, {}) else LIMIT_DEFAULTS[key]


SETTING_DEFAULTS = {'ver': 1,
 'arenaGuiType': ARENA_GUI_TYPE.UNKNOWN,
 'roles': {},
 'clanRoles': {},
 'teamRoles': {1: PREBATTLE_ROLE.SEE_1,
               2: PREBATTLE_ROLE.SEE_2},
 'hideNames': False,
 'hideVehicles': False,
 'hideOpponentCount': False,
 'concealFinalRoster': False,
 'initialRosters': ({}, {}),
 'defaultRoster': 1,
 'accountsToInvite': [],
 'clansToInvite': [],
 'creator': '',
 'creatorClanDBID': 0,
 'creatorClanAbbrev': '',
 'creatorIGRType': IGR_TYPE.NONE,
 'creatorDBID': 0,
 'creatorAttrs': 0,
 'isOpened': False,
 'battlesLimit': 0,
 'winsLimit': 0,
 'winnerIfDraw': 0,
 'switchBattleTeams': False,
 'lifeTime': 0,
 'destroyIfCreatorOut': True,
 'startTime': 0,
 'startIfReady': True,
 'timeBetweenBattles': 0,
 'arenaTypeID': None,
 'roundLength': None,
 'comment': '',
 'chatChannels': 1,
 'arenaVoipChannels': 0,
 'notifyWeb': False,
 'extraData': {},
 'gameplaysMask': 0,
 'vehicleLockMode': 0,
 'vehicleLockTimeFactors': {},
 'observeBothTeams': True}
LIMIT_DEFAULTS = {'maxCountTotal': 256,
 'minCount': 1,
 'totalLevel': (0, 65535),
 'level': (0, 65535),
 'classLevel': {},
 'classes': None,
 'vehicles': None,
 'components': {},
 'ammo': None,
 'shells': {},
 'tags': None,
 'nations': None}

def _collectCurrentReplaceableVehicleComponents(vehicleDescr):
    res = []
    vehicleType = vehicleDescr.type
    if len(vehicleType.chassis) > 1:
        res.append(vehicleDescr.chassis.compactDescr)
    if len(vehicleType.engines) > 1:
        res.append(vehicleDescr.engine.compactDescr)
    if len(vehicleType.radios) > 1:
        res.append(vehicleDescr.radio.compactDescr)
    for posIdx, (turretDescr, gunDescr) in enumerate(vehicleDescr.turrets):
        if len(vehicleType.turrets[posIdx]) > 1:
            res.append(turretDescr.compactDescr)
        if len(turretDescr.guns) > 1:
            res.append(gunDescr.compactDescr)

    return res


def getClanWarsExtraEquipments(clansEquipments, joinedAccountsDBIDs, prebattleID):
    cache = vehicles.g_cache
    equipmentIDs = cache.equipmentIDs()
    equipments = cache.equipments()
    extraEquipments = {}
    for team, info in clansEquipments.iteritems():
        accountDBIDs = filter(lambda dbID: dbID in joinedAccountsDBIDs, info['top_leaders'])
        if accountDBIDs:
            extraEquipments[accountDBIDs[0]] = {'prebattleID': prebattleID,
             'clanDBID': 0,
             'rev': 0,
             'equipments': [ equipments[equipmentIDs[equipmentName]].compactDescr for equipmentName in info['equipments'] ]}

    return extraEquipments
