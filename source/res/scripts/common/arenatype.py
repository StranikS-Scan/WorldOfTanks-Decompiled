# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ArenaType.py
import os
from realm_utils import ResMgr
from constants import IS_BOT, IS_WEB, IS_CLIENT, ARENA_TYPE_XML_PATH
from constants import ARENA_BONUS_TYPE_IDS, ARENA_GAMEPLAY_IDS, ARENA_GAMEPLAY_NAMES, TEAMS_IN_ARENA, HAS_DEV_RESOURCES, MinimapLayerType
from constants import IS_CELLAPP, IS_BASEAPP
from constants import CHAT_COMMAND_FLAGS
from coordinate_system import AXIS_ALIGNED_DIRECTION
from items.vehicles import CAMOUFLAGE_KINDS
from debug_utils import LOG_CURRENT_EXCEPTION
from items import _xml
from typing import Dict
from soft_exception import SoftException
from collections import defaultdict
from data_structures import DictObj
from visual_script.misc import ASPECT, VisualScriptTag, readVisualScriptPlanParams, readVisualScriptPlans
from SpaceVisibilityFlags import SpaceVisibilityFlagsFactory, SpaceVisibilityFlags
from Math import Vector2
if IS_CLIENT:
    from helpers import i18n
    import WWISE
elif IS_WEB:
    from web_stubs import *
if IS_CELLAPP or IS_BASEAPP:
    from server_constants import ARENA_ESTIMATED_LOAD_DEFAULT
g_cache = {}
g_geometryCache = {}
g_spaceCache = {}
g_geometryNamesToIDs = {}
g_gameplayNames = set()
g_gameplaysMask = 0

def getVisibilityMask(typeID):
    global g_spaceCache
    gameplayID, geometryID = parseTypeID(typeID)
    return g_spaceCache[geometryID][SpaceVisibilityFlags.FLAGS_CONFIG_SECTION].getMaskForGameplayID(gameplayID)


def getCompositeVisibilityMask(geometryID, gameplayIDs):
    return g_spaceCache[geometryID][SpaceVisibilityFlags.FLAGS_CONFIG_SECTION].getMaskForGameplayIDs(gameplayIDs)


def getGameplaysMask(gameplayNames):
    return sum([ 1 << ARENA_GAMEPLAY_IDS[name] for name in set(gameplayNames) ])


def getGameplayIDsForMask(gameplaysMask):
    return [ gameplayID for gameplayID in xrange(len(ARENA_GAMEPLAY_NAMES)) if bool(gameplaysMask & 1 << gameplayID) ]


def getGameplayName(gameplayID):
    return ARENA_GAMEPLAY_NAMES[gameplayID]


def getGameplayIDForName(gameplayName):
    return ARENA_GAMEPLAY_IDS[gameplayName]


def parseTypeID(typeID):
    return (typeID >> 16, typeID & 65535)


def buildArenaTypeID(gameplayID, geometryID):
    return geometryID | gameplayID << 16


_LIST_XML = ARENA_TYPE_XML_PATH + '_list_.xml'
_DEFAULT_XML = ARENA_TYPE_XML_PATH + '_default_.xml'

def init(isFullCache=True):
    global g_gameplayNames
    global g_cache
    global g_geometryNamesToIDs
    global g_gameplaysMask
    rootSection = ResMgr.openSection(_LIST_XML)
    if rootSection is None:
        raise SoftException("Can't open '%s'" % _LIST_XML)
    defaultXml = ResMgr.openSection(_DEFAULT_XML)
    if defaultXml is None:
        raise SoftException("Can't open '%s'" % _DEFAULT_XML)
    defaultGameplayTypesXml = defaultXml['gameplayTypes']
    if defaultGameplayTypesXml is None or not defaultGameplayTypesXml:
        raise SoftException("No defaults for 'gameplayTypes'")
    geometriesSet = set()
    for key, value in rootSection.items():
        isDevelopmentArena = value.readBool('isDevelopment')
        if value.readBool('isHangar'):
            continue
        geometryID = value.readInt('id')
        if geometryID in geometriesSet:
            raise SoftException('Geometry ID=%d is not unique' % geometryID)
        buildResult = __buildCache(geometryID, value.readString('name'), defaultXml, isFullCache, isDevelopmentArena)
        if buildResult:
            geometriesSet.add(geometryID)

    ResMgr.purge(_LIST_XML, True)
    ResMgr.purge(_DEFAULT_XML, True)
    g_gameplaysMask = getGameplaysMask(g_gameplayNames)
    g_geometryNamesToIDs = {arenaType.geometryName:arenaType.geometryID for arenaType in g_cache.itervalues()}
    return


class _BonusTypeOverridesMixin(object):

    def __init__(self):
        self._bonusType = None
        self.__bonusTypeCfg = {}
        return

    def __getattr__(self, name):
        return self.__bonusTypeCfg.get(self._bonusType, {}).get(name) if self._bonusType is not None else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._bonusType = None
        return

    def useBonusTypeOverrides(self, bonusType=None):
        self._bonusType = bonusType
        return self

    def setBonusTypeCfg(self, cfg):
        if self._bonusType is None:
            return
        elif not cfg:
            return
        else:
            self.__bonusTypeCfg[self._bonusType] = cfg
            return


class ArenaType(_BonusTypeOverridesMixin):

    def __init__(self, geometryCfg, gameplayCfg):
        super(ArenaType, self).__init__()
        if isinstance(geometryCfg, GeometryType):
            self.__geometryType = geometryCfg
        else:
            self.__geometryType = GeometryType(geometryCfg)
        self.__gameplayCfg = gameplayCfg
        self.__gameplayCfg['id'] = gameplayCfg['gameplayID'] << 16 | self.__geometryType.geometryID
        if self.maxPlayersInTeam < self.minPlayersInTeam:
            raise SoftException("'maxPlayersInTeam' value < 'minPlayersInTeam' value")

    def __getattr__(self, name):
        value = super(ArenaType, self).__getattr__(name)
        if value is not None:
            return value
        elif name in self.__gameplayCfg:
            return self.__gameplayCfg[name]
        else:
            with self.__geometryType.useBonusTypeOverrides(self._bonusType) as geometryTypeForBonus:
                return getattr(geometryTypeForBonus, name, None)
            return


class GeometryType(_BonusTypeOverridesMixin):

    def __init__(self, cfg):
        super(GeometryType, self).__init__()
        self.__cfg = cfg

    def __getattr__(self, name):
        value = super(GeometryType, self).__getattr__(name)
        return value if value is not None else self.__cfg.get(name)


class _DroneSettingHolder(object):

    def __init__(self):
        super(_DroneSettingHolder, self).__init__()
        self.__defaultValue = None
        self.__specificValues = {}
        return

    def setValue(self, arenaTypeLabel, value):
        self.__specificValues[arenaTypeLabel] = value
        return self

    def getValue(self, arenaTypeLabel):
        value = self.__specificValues.get(arenaTypeLabel)
        return value if value is not None else self.__defaultValue

    def setDefault(self, value):
        self.__defaultValue = value
        return self

    def getDefault(self):
        return self.__defaultValue

    def getSpecificItemsCount(self):
        return len(self.__specificValues)

    def __getitem__(self, key):
        return self.getValue(key)


def __buildCache(geometryID, geometryName, defaultXml, isFullCache, isDevelopmentArena=False):
    global g_geometryCache
    sectionName = ARENA_TYPE_XML_PATH + geometryName + '.xml'
    section = ResMgr.openSection(sectionName)
    if section is None:
        if isDevelopmentArena:
            return False
        raise SoftException("Can't open '%s'" % sectionName)
    geometryCfg = __readGeometryCfg(geometryID, geometryName, section, defaultXml)
    geometryType = GeometryType(geometryCfg)
    g_geometryCache[geometryID] = __addBonusTypeOverrides(geometryType, section, defaultXml)
    if isFullCache:
        spaceName = os.path.basename(geometryCfg['geometry'])
        spaceData = __readSpaceCfg(spaceName)
        g_spaceCache[geometryID] = spaceData
    for gameplayCfg in __readGameplayCfgs(geometryName, section, defaultXml, geometryCfg):
        arenaType = ArenaType(geometryType, gameplayCfg)
        g_cache[arenaType.id] = arenaType
        g_gameplayNames.add(arenaType.gameplayName)

    ResMgr.purge(sectionName, True)
    return True


def __addBonusTypeOverrides(overridable, section, defaultXml):
    for bonusTypeID, bonusType in ARENA_BONUS_TYPE_IDS.iteritems():
        with overridable.useBonusTypeOverrides(bonusTypeID) as overriden:
            bonusTypeCfg = __readBonusTypeCfgs(overridable.geometryName, section, defaultXml, bonusType)
            overriden.setBonusTypeCfg(bonusTypeCfg)

    return overridable


def __readBonusTypeCfgs(geometryName, section, defaultXml, bonusType):
    overrides = section['bonusTypeOverrides'] or defaultXml['bonusTypeOverrides']
    if overrides is None:
        return {}
    else:
        bonusOverrides = overrides[bonusType]
        if bonusOverrides is None:
            return {}
        try:
            cfg = {}
            if IS_CELLAPP or IS_BASEAPP:
                cfg['estimatedLoad'] = _readFloat('estimatedLoad', bonusOverrides, defaultXml, ARENA_ESTIMATED_LOAD_DEFAULT)
            if __hasKey('maxPlayersInTeam', bonusOverrides, defaultXml):
                cfg['maxPlayersInTeam'] = __readMaxPlayersInTeam(bonusOverrides, defaultXml)
            if __hasKey('runDelay', bonusOverrides, defaultXml):
                cfg['runDelay'] = _readInt('runDelay', bonusOverrides, defaultXml)
            if __hasKey('runDelayDev', bonusOverrides, defaultXml):
                cfg['runDelayDev'] = _readInt('runDelayDev', bonusOverrides, defaultXml)
        except Exception as e:
            LOG_CURRENT_EXCEPTION()
            raise SoftException("wrong %s bonusTypeOverrides section '%s' : %s" % (geometryName, bonusType, e))

        return cfg


def __readGeometryCfg(geometryID, geometryName, section, defaultXml):
    try:
        cfg = {}
        cfg['geometryID'] = geometryID
        cfg['geometryName'] = geometryName
        cfg['geometry'] = _readString('geometry', section, defaultXml)
        cfg['boundingBox'] = _readBoundingBox(section)
        cfg['spaceBoundingBox'] = __calcSpaceBoundingBox(cfg['boundingBox'])
        cfg['weatherPresets'] = __readWeatherPresets(section)
        cfg['vehicleCamouflageKind'] = __readVehicleCamouflageKind(section)
        cfg['isDevelopment'] = __readBool('isDevelopment', section, defaultXml, False)
        if IS_CELLAPP or IS_BASEAPP:
            cfg['estimatedLoad'] = _readFloat('estimatedLoad', section, defaultXml, ARENA_ESTIMATED_LOAD_DEFAULT)
        if IS_CLIENT or IS_WEB:
            cfg['name'] = i18n.makeString(_readString('name', section, defaultXml))
        if IS_CLIENT:
            cfg['umbraEnabled'] = _readInt('umbraEnabled', section, defaultXml)
            cfg['defaultReverbPreset'] = _readString('defaultReverbPreset', section, defaultXml).strip()
            cfg['batchingEnabled'] = _readInt('batchingEnabled', section, defaultXml)
            cfg['waterTexScale'] = section.readFloat('water/texScale', 0.5)
            cfg['waterFreqX'] = section.readFloat('water/freqX', 1.0)
            cfg['waterFreqZ'] = section.readFloat('water/freqZ', 1.0)
            cfg['defaultGroundEffect'] = __readDefaultGroundEffect(section, defaultXml)
        cfg.update(__readCommonCfg(section, defaultXml, True, {}))
    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise SoftException("Wrong arena type XML '%s' : %s" % (geometryName, str(e)))

    return cfg


def __readGameplayCfgs(geometryName, section, defaultXml, geometryCfg):
    try:
        if section['gameplayTypes'] is None:
            gameplayName = 'ctf'
            gameplayID = getGameplayIDForName(gameplayName)
            return [{'gameplayID': gameplayID,
              'gameplayName': gameplayName}]
        if not section['gameplayTypes']:
            raise SoftException("no 'gameplayTypes' section")
        cfgs = []
        defaultGameplayTypesXml = defaultXml['gameplayTypes']
        for name, subsection in section['gameplayTypes'].items():
            defaultSubsection = defaultGameplayTypesXml[name]
            if defaultSubsection is None:
                raise SoftException("no defaults for '%s'" % name)
            gameplayCfg = __readGameplayCfg(name, subsection, defaultSubsection, geometryCfg)
            if IS_CLIENT:
                wwmusicDroneSetup = 'wwmusicDroneSetup'
                gameplayCfg[wwmusicDroneSetup] = __readWWmusicDroneSection(wwmusicDroneSetup, section, defaultXml, name)
            cfgs.append(gameplayCfg)

    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise SoftException("Wrong arena type XML '%s' : %s" % (geometryName, e))

    return cfgs


def __readGameplayCfg(gameplayName, section, defaultXml, geometryCfg):
    try:
        cfg = {}
        cfg['gameplayID'] = getGameplayIDForName(gameplayName)
        cfg['gameplayName'] = gameplayName
        for setting in ('battleEndWarningAppearTime', 'battleEndWarningDuration', 'battleEndingSoonTime'):
            cfg[setting] = 0
            if not gameplayName.startswith('fallout') and __hasKey(setting, section, defaultXml):
                cfg[setting] = _readInt(setting, section, defaultXml)

        if gameplayName == 'nations':
            raise SoftException('national battles are disabled')
        notificationsRemapping = __readNotificationsRemappingSection(section, defaultXml)
        if notificationsRemapping is not None:
            cfg['notificationsRemapping'] = notificationsRemapping
        cfg.update(__readCommonCfg(section, defaultXml, False, geometryCfg))
    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise SoftException("wrong gameplay section '%s' : %s" % (gameplayName, e))

    return cfg


def __readCommonCfg(section, defaultXml, raiseIfMissing, geometryCfg):
    cfg = {}
    if raiseIfMissing or __hasKey('explicitRequestOnly', section, defaultXml):
        cfg['explicitRequestOnly'] = __readBool('explicitRequestOnly', section, defaultXml)
    if raiseIfMissing or __hasKey('minPlayersInTeam', section, defaultXml):
        cfg['minPlayersInTeam'] = __readMinPlayersInTeam(section, defaultXml)
    if raiseIfMissing or __hasKey('maxPlayersInTeam', section, defaultXml):
        cfg['maxPlayersInTeam'] = __readMaxPlayersInTeam(section, defaultXml)
    if raiseIfMissing or __hasKey('maxTeamsInArena', section, defaultXml):
        cfg['maxTeamsInArena'] = __readTeamsCount('maxTeamsInArena', section, defaultXml)
    if raiseIfMissing or __hasKey('minTeamsInArena', section, defaultXml):
        cfg['minTeamsInArena'] = __readTeamsCount('minTeamsInArena', section, defaultXml)
    if raiseIfMissing or __hasKey('runDelay', section, defaultXml):
        cfg['runDelay'] = _readInt('runDelay', section, defaultXml)
    if raiseIfMissing or __hasKey('runDelayDev', section, defaultXml):
        cfg['runDelayDev'] = _readInt('runDelayDev', section, defaultXml)
    if raiseIfMissing or __hasKey('roundLength', section, defaultXml):
        cfg['roundLength'] = _readInt('roundLength', section, defaultXml)
    if raiseIfMissing or __hasKey('winnerIfTimeout', section, defaultXml):
        cfg['winnerIfTimeout'] = _readInt('winnerIfTimeout', section, defaultXml)
    if raiseIfMissing or __hasKey('winnerIfExtermination', section, defaultXml):
        cfg['winnerIfExtermination'] = _readInt('winnerIfExtermination', section, defaultXml)
    if raiseIfMissing or __hasKey('artilleryPreparationChance', section, defaultXml):
        cfg['artilleryPreparationChance'] = _readFloat('artilleryPreparationChance', section, defaultXml)
    if raiseIfMissing or section.has_key('mapActivities'):
        cfg['mapActivitiesTimeframes'] = __readMapActivitiesTimeframes(section)
    if raiseIfMissing or section.has_key('boundingBox'):
        cfg['boundingBox'] = _readBoundingBox(section)
    maxTeamsInArena = cfg.get('maxTeamsInArena', geometryCfg.get('maxTeamsInArena', None))
    cfg.update(__readWinPoints(section))
    cfg.update(__readGameplayPoints(section, geometryCfg))
    cfg['teamBasePositions'] = __readTeamBasePositions(section, maxTeamsInArena)
    cfg['teamSpawnPoints'] = __readTeamSpawnPoints(section, maxTeamsInArena)
    cfg['squadTeamNumbers'], cfg['soloTeamNumbers'] = __readTeamNumbers(section, maxTeamsInArena)
    cfg[VisualScriptTag] = _readVisualScript(section)
    if raiseIfMissing or __hasKey('numPlayerGroups', section, defaultXml):
        cfg['numPlayerGroups'] = _readInt('numPlayerGroups', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('playerGroupLimit', section, defaultXml):
        cfg['playerGroupLimit'] = _readInt('playerGroupLimit', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('respawnType', section, defaultXml):
        cfg['respawnType'] = _readString('respawnType', section, defaultXml, '')
    if raiseIfMissing or __hasKey('unlockUnusedVehiclesOnLeave', section, defaultXml):
        cfg['unlockUnusedVehiclesOnLeave'] = __readBool('unlockUnusedVehiclesOnLeave', section, defaultXml, False)
    if raiseIfMissing or __hasKey('numDestructiblesToDestroyForWin', section, defaultXml):
        cfg['numDestructiblesToDestroyForWin'] = _readInt('numDestructiblesToDestroyForWin', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('addGameTimePerDestructible', section, defaultXml):
        cfg['addGameTimePerDestructible'] = _readFloat('addGameTimePerDestructible', section, defaultXml, 0.0)
    if __hasKey('sectorSettings', section, defaultXml):
        cfg['sectorSettings'] = SectorSettings('sectorSettings', section, defaultXml)
    if __hasKey('epicSectorSettings', section, defaultXml):
        cfg['epicSectorSettings'] = EpicSectorSettings('epicSectorSettings', section, defaultXml)
    if __hasKey('epicSectorGrid', section, defaultXml):
        cfg['epicSectorGrid'] = EpicSectorGrid('epicSectorGrid', section, defaultXml)
    if __hasKey('frontLinesAlgorithm', section, defaultXml):
        cfg['frontLinesAlgorithm'] = FrontLinesAlgorithmSettings(section, defaultXml)
    if __hasKey('frontLinesGeometry', section, defaultXml):
        cfg['frontLinesGeometry'] = FrontLinesGeometrySettings(section, defaultXml)
    if __hasKey('recoveryMechanic', section, defaultXml):
        cfg['recoveryMechanic'] = RecoveryMechanicSettings(section, defaultXml)
    if __hasKey('overtimeMechanic', section, defaultXml):
        cfg['overtimeMechanic'] = OvertimeMechanicSettings(section, defaultXml)
    if raiseIfMissing or __hasKey('capturePointsLimit', section, defaultXml):
        cfg['capturePointsLimit'] = _readInt('capturePointsLimit', section, defaultXml, -1)
    if raiseIfMissing or __hasKey('defencePointsLimit', section, defaultXml):
        cfg['defencePointsLimit'] = _readInt('defencePointsLimit', section, defaultXml, -1)
    if raiseIfMissing or __hasKey('ironShieldDefenderTeam', section, defaultXml):
        cfg['ironShieldDefenderTeam'] = _readInt('ironShieldDefenderTeam', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('defenderBonusTeam', section, defaultXml):
        cfg['defenderBonusTeam'] = _readInt('defenderBonusTeam', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('defenderBonusInterval', section, defaultXml):
        cfg['defenderBonusInterval'] = _readInt('defenderBonusInterval', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('enabledChatCommandFlags', section, defaultXml):
        cfg['enabledChatCommandFlags'] = __readChatCommandFlags('enabledChatCommandFlags', section, defaultXml)
    if __hasKey('recon', section, defaultXml):
        cfg['recon'] = ReconSettings(section['recon'])
    if raiseIfMissing or __hasKey('resetLocalTeamKillerAtRespawn', section, defaultXml):
        cfg['resetLocalTeamKillerAtRespawn'] = __readBool('resetLocalTeamKillerAtRespawn', section, defaultXml)
    if raiseIfMissing or __hasKey('stopVehiclesAtArenaFreeze', section, defaultXml):
        cfg['stopVehiclesAtArenaFreeze'] = __readBool('stopVehiclesAtArenaFreeze', section, defaultXml, False)
    if raiseIfMissing or __hasKey('leaveDisconnectedTimeout', section, defaultXml):
        cfg['leaveDisconnectedTimeout'] = _readInt('leaveDisconnectedTimeout', section, defaultXml, -1)
    if IS_CLIENT or IS_WEB:
        if raiseIfMissing or __hasKey('description', section, defaultXml):
            cfg['description'] = i18n.makeString(_readString('description', section, defaultXml))
        if raiseIfMissing or __hasKey('minimap', section, defaultXml):
            cfg['minimap'] = _readString('minimap', section, defaultXml)
        if section.has_key('minimapLayers'):
            result = {}
            for item in section['minimapLayers'].values():
                layerId = item.readString('layerId')
                path = item.readString('path')
                layerType = item.readString('layerType')
                result[layerId] = (path, layerType)

            cfg['minimapLayers'] = result
        if __hasKey('overviewmap', section, defaultXml):
            cfg['overviewmap'] = _readString('overviewmap', section, defaultXml)
        if raiseIfMissing or __hasKey('wwambientSound', section, defaultXml):
            cfg['ambientSound'] = _readString('wwambientSound', section, defaultXml)
        musicSetup = None
        if raiseIfMissing or __hasKey('wwmusicSetup', section, defaultXml):
            musicSetup = __readWWmusicSection(section, defaultXml)
        if musicSetup is not None:
            cfg['wwmusicSetup'] = musicSetup
        if raiseIfMissing or __hasKey('wwbattleCountdownTimerSound', section, defaultXml):
            cfg['battleCountdownTimerSound'] = _readString('wwbattleCountdownTimerSound', section, defaultXml)
        if raiseIfMissing or section.has_key('mapActivities'):
            cfg['mapActivitiesSection'] = section['mapActivities']
        if section.has_key('soundRemapping'):
            cfg['soundRemapping'] = section['soundRemapping']
    if IS_CLIENT or IS_BOT:
        cfg['controlPoints'] = __readControlPoints(section)
        cfg['teamLowLevelSpawnPoints'] = __readTeamSpawnPoints(section, maxTeamsInArena, nodeNameTemplate='team%d_low', required=False)
        cfg['botPoints'] = __readBotPoints(section)
        cfg['pointsOfInterest'] = __readPointsOfInterest(section)
    return cfg


def __readWWmusicSection(section, defaultXml):
    wwmusic = None
    if __hasKey('wwmusicSetup', section, defaultXml):
        wwmusic = {}
        dataSection = section if section.has_key('wwmusicSetup') else defaultXml
        for name, value in _xml.getChildren(defaultXml, dataSection, 'wwmusicSetup'):
            wwmusic[name] = value.asString

    return wwmusic


def __readNotificationsRemappingSection(section, defaultXml):
    notificationsRemapping = None
    if __hasKey('notificationsRemapping', section, defaultXml):
        notificationsRemapping = {}
        dataSection = section if section.has_key('notificationsRemapping') else defaultXml
        for _, event in _xml.getChildren(defaultXml, dataSection, 'notificationsRemapping'):
            notificationsRemapping[event['name'].asString] = event['mod'].asString if event.has_key('mod') else None

    return notificationsRemapping


def __readWWmusicDroneSection(wwmusicDroneSetup, section, defaultXml, gameplayName):
    if section.has_key(wwmusicDroneSetup):
        dataSection = section
    else:
        dataSection = defaultXml
    outcome = defaultdict(_DroneSettingHolder)
    droneChildren = sorted(_xml.getChildren(defaultXml, dataSection, wwmusicDroneSetup), key=lambda item: len(item[1].items()))
    valueTag = 'value'
    for settingName, settingChildren in droneChildren:
        if settingChildren.has_key(valueTag):
            settingValue = settingChildren.readInt(valueTag)
            if settingChildren.has_key('arena_type_label'):
                if settingChildren.has_key('gameplay_name'):
                    if gameplayName == settingChildren.readString('gameplay_name'):
                        outcome[settingName].setValue(settingChildren.readString('arena_type_label'), settingValue)
                else:
                    outcome[settingName].setValue(settingChildren.readString('arena_type_label'), settingValue)
            elif settingChildren.has_key('gameplay_name'):
                if gameplayName == settingChildren.readString('gameplay_name'):
                    outcome[settingName].setDefault(settingValue)
            else:
                outcome[settingName].setDefault(settingValue)
        raise SoftException('"{}" section missed the key "{}"!'.format(settingName, valueTag))

    return outcome


def __readSpaceCfg(geometryName):
    cfg = {}
    cfg[SpaceVisibilityFlags.FLAGS_CONFIG_SECTION] = SpaceVisibilityFlagsFactory.create(geometryName)
    return cfg


def __hasKey(key, xml, defaultXml):
    return xml.has_key(key) or defaultXml.has_key(key)


def _readString(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readString(key)
    elif defaultXml.has_key(key):
        return defaultXml.readString(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def __readStrings(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readStrings(key)
    elif defaultXml.has_key(key):
        return defaultXml.readStrings(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def _readInt(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readInt(key)
    elif defaultXml.has_key(key):
        return defaultXml.readInt(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def _readFloat(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readFloat(key)
    elif defaultXml.has_key(key):
        return defaultXml.readFloat(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def __readBool(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readBool(key)
    elif defaultXml.has_key(key):
        return defaultXml.readBool(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def _readFloatArray(key, tag, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml[key].readFloats(tag)
    elif defaultXml.has_key(key):
        return defaultXml[key].readFloats(tag)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise SoftException("missing key '%s'" % key)
        return


def _readVisualScriptAspect(section, aspect, commonParams):
    plans = []
    if section.has_key(aspect):
        plans = readVisualScriptPlans(section[aspect], commonParams)
    return plans


def _readVisualScript(section):
    if section.has_key(VisualScriptTag):
        vseSection = section[VisualScriptTag]
        commonParams = {}
        if vseSection.has_key('common'):
            commonParams = readVisualScriptPlanParams(vseSection['common'])
        return {ASPECT.CLIENT: _readVisualScriptAspect(vseSection, ASPECT.CLIENT.lower(), commonParams),
         ASPECT.SERVER: _readVisualScriptAspect(vseSection, ASPECT.SERVER.lower(), commonParams)}
    return {ASPECT.CLIENT: [],
     ASPECT.SERVER: []}


def _readBoundingBox(section):
    bottomLeft = section.readVector2('boundingBox/bottomLeft')
    upperRight = section.readVector2('boundingBox/upperRight')
    if bottomLeft[0] >= upperRight[0] or bottomLeft[1] >= upperRight[1]:
        raise SoftException("wrong 'boundingBox' values")
    return (bottomLeft, upperRight)


def __calcSpaceBoundingBox(arenaBoundingBox):
    ARENA_EXTENT = 100
    return (arenaBoundingBox[0] - Vector2(ARENA_EXTENT, ARENA_EXTENT), arenaBoundingBox[1] + Vector2(ARENA_EXTENT, ARENA_EXTENT))


def __readChatCommandFlags(name, section, defaultXml):
    if section.has_key(name):
        flagsAsWhitespaceSeparatedString = section.readString(name)
    else:
        flagsAsWhitespaceSeparatedString = defaultXml.readString(name)
    flagsAsListOfStrings = flagsAsWhitespaceSeparatedString.split()
    flagsAsListOfValues = [ CHAT_COMMAND_FLAGS.FLAG_BY_NAME[flagStr] for flagStr in flagsAsListOfStrings ]
    flagsMask = 0
    for flag in flagsAsListOfValues:
        flagsMask |= flag

    return flagsMask


class ReconSettings(object):

    def __init__(self, section):
        self.flyDirections = self._readXmlReconFlyDirections(section['flyDirections'])

    def _readXmlReconFlyDirections(self, section):
        flyDirections = {}
        for name, value in section.items():
            if name == 'flyDirection':
                team = value.readInt('team')
                direction = value.readVector3('direction')
                flyDirections[team] = direction

        return flyDirections


class FrontLinesGeometrySettings(object):

    def __init__(self, section, defaultXml):
        dcfg = self._readXmlFronts(defaultXml['frontLinesGeometry'])
        cfg = self._readXmlFronts(section['frontLinesGeometry'])
        dcfg.update(cfg)
        self.fronts = dcfg

    def _readXmlFronts(self, section):
        fronts = {}
        if section is not None:
            for name, value in section.items():
                if name == 'front':
                    playerGroup = value.readInt('playerGroup')
                    settings = dict(direction=value.readVector2('direction'), bounds=_readBoundingBox(value))
                    fronts[playerGroup] = DictObj(settings)

        return fronts


class FrontLinesAlgorithmSettings(object):

    def __init__(self, section, defaultXml):
        dcfg = self._readXmlSettings(defaultXml['frontLinesAlgorithm'])
        cfg = self._readXmlSettings(section['frontLinesAlgorithm'])
        dcfg.update(cfg)
        self.__dict__ = dcfg

    def _readFloats(self, section, *names):
        return {name:section.readFloat(name) for name in names}

    def _readInts(self, section, *names):
        return {name:section.readInt(name) for name in names}

    def _readXmlSettings(self, section):
        settings = {}
        if section is not None:
            settings.update(self._readFloats(section, 'columnWidth', 'frontDropPerColumn', 'outlierFraction', 'outlierVerticalDistance', 'intrusionVerticalTolerance', 'intrusionCheckExtendBounds'))
            settings.update(self._readInts(section, 'defenderTeam', 'frontEdgeExtendColumns'))
        return settings


class RecoveryMechanicSettings(object):

    def __init__(self, section, defaultXml):
        dcfg = self._readXmlSettings(defaultXml['recoveryMechanic'])
        cfg = self._readXmlSettings(section['recoveryMechanic'])
        dcfg.update(cfg)
        self.__dict__ = dcfg

    def _readInts(self, section, *names):
        return {name:section.readInt(name) for name in names}

    def _readXmlSettings(self, section):
        settings = {}
        if section is not None:
            settings.update(self._readInts(section, 'recoveryCounter', 'recoveryBlockingCounter'))
        return settings


class OvertimeMechanicSettings(object):

    def __init__(self, section, defaultXml):
        dcfg = self._readXmlSettings(defaultXml['overtimeMechanic'])
        cfg = self._readXmlSettings(section['overtimeMechanic'])
        dcfg.update(cfg)
        self.__dict__ = dcfg

    def _readInts(self, section, *names):
        return {name:section.readInt(name) for name in names}

    def _readXmlSettings(self, section):
        settings = {}
        if section is not None:
            settings.update(self._readInts(section, 'overtimeLimit'))
        return settings


class SectorProtectionZoneSettings(object):

    def __init__(self, key, section, defaultXml):
        self.numberOfTurrets = _readInt(key + '/numberOfTurrets', section, defaultXml, 2)
        self.maxStayTime = _readFloat(key + '/maxStayTime', section, defaultXml, 5.0)
        self.minShootingTime = _readFloat(key + '/minShootingTime', section, defaultXml, 15.0)
        self.minShootingInterval = _readFloat(key + '/minShootingInterval', section, defaultXml, 1.0)
        self.shotShellNation = _readString(key + '/shotShellNation', section, defaultXml, 'germany')
        self.shotShellName = _readString(key + '/shotShellName', section, defaultXml, 'sector_artillery_shell')
        self.shotPiercingPower = _readFloat(key + '/shotPiercingPower', section, defaultXml, 45.0)
        self.shotRadius = _readFloat(key + '/shotRadius', section, defaultXml, 5.0)
        self.shotDuration = _readFloat(key + '/shotDuration', section, defaultXml, 1.0)
        self.minTurretShootInterval = _readFloat(key + '/minTurretShootInterval', section, defaultXml, 2.0)


class SectorSettings(object):

    def __init__(self, key, section, defaultXml):
        self.transitionTime = _readFloat(key + '/transitionTime', section, defaultXml, 60.0)
        self.maxStayTime = _readFloat(key + '/maxStayTime', section, defaultXml, 30.0)
        self.destructionDuration = _readFloat(key + '/destructionDuration', section, defaultXml, 5.0)
        self.closedZoneFireDelay = _readFloat(key + '/closedZoneFireDelay', section, defaultXml, 4.0)
        self.numBombs = _readInt(key + '/numBombs', section, defaultXml, 10)
        self.bombingHeight = _readFloat(key + '/bombingHeight', section, defaultXml, 70.0)
        self.bombingWidth = _readFloat(key + '/bombingWidth', section, defaultXml, 50.0)
        self.maxRandomBombsPerTarget = _readInt(key + '/maxRandomBombsPerTarget', section, defaultXml, 3)
        self.bombShellNation = _readString(key + '/bombShellNation', section, defaultXml, 'germany')
        self.bombShellName = _readString(key + '/bombShellName', section, defaultXml, 'sector_bomber_shell')
        self.protectionZone = SectorProtectionZoneSettings('sectorSettings/protectionZone', section, defaultXml)


class EpicSectorSettings(object):

    def __init__(self, key, section, defaultXml):
        addGameTimeString = _readString(key + '/addGameTimePerCapture', section, defaultXml, '')
        self.addGameTimePerCapture = [ float(s) for s in addGameTimeString.split() ]
        self.addGameTimeAllCaptured = _readFloat(key + '/addGameTimeAllCaptured', section, defaultXml, 0.0)
        self.frontLineInit = _readFloat(key + '/frontLineInit', section, defaultXml, 400.0)
        self.transitionFrontLineBoundBackward = _readFloat(key + '/transitionFrontLineBoundBackward', section, defaultXml, 300.0)
        self.transitionFrontLineBoundForward = _readFloat(key + '/transitionFrontLineBoundForward', section, defaultXml, 250.0)
        defenderMotivationFactorsString = _readString(key + '/defenderMotivationFactors', section, defaultXml, '')
        self.defenderMotivationFactors = [ float(s) for s in defenderMotivationFactorsString.split() ]
        self.overtimeMaxFrontlineOffset = _readFloat(key + '/overtimeMaxFrontlineOffset', section, defaultXml, -600.0)


class EpicSectorGrid(object):

    def __init__(self, key, section, defaultXml):
        mainDirectionName = section.readString(key + '/mainDirection', '-Z')
        self.mainDirection = AXIS_ALIGNED_DIRECTION.FROM_NAME[mainDirectionName]
        self.bordersZ = sorted(_readFloatArray(key + '/bordersZ', 'border', section, defaultXml))
        self.bordersX = sorted(_readFloatArray(key + '/bordersX', 'border', section, defaultXml))
        self.owningTeam = section.readInt(key + '/owningTeam', 1)


def __readWeatherPresets(section):
    weatherXML = section['weather']
    if weatherXML is None or not weatherXML:
        return [{'rnd_range': (0, 1)}]
    else:
        presets = []
        possibilitySum = 0
        for presetXML in weatherXML.values():
            preset = {}
            for key, valueXML in presetXML.items():
                preset[key] = valueXML.asString

            presets.append(preset)
            possibilitySum += presetXML.readFloat('possibility', 1.0)

        factor = 1 / possibilitySum
        prev_upper_limit = 0
        for preset in presets:
            possibility = float(preset.pop('possibility', 1.0))
            rnd_range = (prev_upper_limit, prev_upper_limit + possibility * factor)
            preset['rnd_range'] = rnd_range
            prev_upper_limit = rnd_range[1]

        return presets


def __readVehicleCamouflageKind(section):
    kindName = section.readString('vehicleCamouflageKind')
    kind = CAMOUFLAGE_KINDS.get(kindName)
    if kind is None:
        raise SoftException("missing or wrong section 'vehicleCamouflageKind'")
    return kind


def __readMinPlayersInTeam(section, defaultXml):
    minPlayersInTeam = _readInt('minPlayersInTeam', section, defaultXml)
    if minPlayersInTeam < 0:
        raise SoftException("wrong 'minPlayersInTeam' value")
    return minPlayersInTeam


def __readMaxPlayersInTeam(section, defaultXml):
    maxPlayersInTeam = _readInt('maxPlayersInTeam', section, defaultXml)
    if maxPlayersInTeam < 0:
        raise SoftException("wrong 'maxPlayersInTeam' value")
    return maxPlayersInTeam


def __readTeamsCount(key, section, defaultXml):
    value = _readInt(key, section, defaultXml)
    if not TEAMS_IN_ARENA.MIN_TEAMS <= value <= TEAMS_IN_ARENA.MAX_TEAMS:
        raise SoftException('Invalid teams in arena')
    return value


def __readTeamNumbers(section, maxTeamsInArena):
    if not (section.has_key('squadTeamNumbers') or section.has_key('soloTeamNumbers')):
        if maxTeamsInArena > 2:
            raise SoftException('For multiteam mode squadTeamNumbers and (or) soloTeamNumbers must be set')
        return (set(), set())
    squadTeamNumbers = set([ int(v) for v in section.readString('squadTeamNumbers', '').split() ])
    soloTeamNumbers = set([ int(v) for v in section.readString('soloTeamNumbers', '').split() ])
    if len(squadTeamNumbers) + len(soloTeamNumbers) != maxTeamsInArena:
        raise SoftException('Number of squad (%d) and solo (%d) teams must be equal to maxTeamsInArena (%d)' % (len(squadTeamNumbers), len(soloTeamNumbers), maxTeamsInArena))
    if len(squadTeamNumbers & soloTeamNumbers) > 0:
        raise SoftException('Squad and solo team numbers contains identical team numbers (%s)' % str(squadTeamNumbers & soloTeamNumbers))
    allTeamNumbers = squadTeamNumbers | soloTeamNumbers
    if min(allTeamNumbers) < 1 or max(allTeamNumbers) > TEAMS_IN_ARENA.MAX_TEAMS:
        raise SoftException('Invalid team number. Must be between 1 and %d.' % TEAMS_IN_ARENA.MAX_TEAMS)
    return (squadTeamNumbers, soloTeamNumbers)


def __readMapActivitiesTimeframes(section):
    mapActivitiesXML = section['mapActivities']
    if not mapActivitiesXML:
        return []
    timeframes = []
    for activityXML in mapActivitiesXML.values():
        startTimes = activityXML.readVector2('startTime')
        if (startTimes[0] >= 0) != (startTimes[1] >= 0):
            raise SoftException("wrong subsection 'mapActivities/startTime'. All values of startTime must have same sign")
        possibility = activityXML.readFloat('possibility', 1.0)
        timeframes.append((startTimes[0], startTimes[1], possibility))

    return timeframes


def __readDefaultGroundEffect(section, defaultXml):
    defaultGroundEff = _readString('defaultGroundEffect', section, defaultXml).strip()
    if defaultGroundEff == '':
        return None
    else:
        if defaultGroundEff.find('|') != -1:
            defaultGroundEff = defaultGroundEff.split('|')
            for i in xrange(0, len(defaultGroundEff)):
                defaultGroundEff[i] = defaultGroundEff[i].strip()

        return defaultGroundEff


def __readControlPoints(section):
    res = []
    for name, value in section.items():
        if name == 'controlPoint':
            res.append(value.readVector2(''))

    return res if res else None


def __readBotPoints(section):
    res = {}
    for name, value in section.items():
        if name == 'botPoint':
            index = value['index'].readInt('')
            pos = value['position'].readVector3('')
            res[index] = pos

    return res if res else None


def __readPointsOfInterest(section):
    res = []
    pointsSection = section['pointsOfInterestUDO']
    if pointsSection is not None:
        for name, value in pointsSection.items():
            if name == 'point':
                pointType = value.readInt('type')
                pointPosition = value.readVector2('position')
                res.append({'type': pointType,
                 'position': pointPosition})

    return res


def __readTeamBasePositions(section, maxTeamsInArena):
    section = section['teamBasePositions']
    teamBases = tuple([ {} for _ in xrange(maxTeamsInArena) ])
    if section is None:
        return teamBases
    else:
        for idx, teamBase in enumerate(teamBases):
            teamIdx = idx + 1
            s = section['team%s' % teamIdx]
            if s is None:
                continue
            for name, value in s.items():
                try:
                    id = int(name[8:])
                except:
                    raise SoftException("wrong subsection 'teamBasePositions/team%s/%s'" % (teamIdx, s.name))

                teamBase[id] = value.readVector2('')

        return teamBases


def __readTeamSpawnPoints(section, maxTeamsInArena, nodeNameTemplate='team%d', required=True):
    section = section['teamSpawnPoints']
    allTeamSpawnPoints = tuple([ [] for _ in xrange(maxTeamsInArena) ])
    if section is None:
        return allTeamSpawnPoints
    else:
        for idx, teamSpawnPoint in enumerate(allTeamSpawnPoints):
            teamIdx = idx + 1
            s = section[nodeNameTemplate % teamIdx]
            if s is None:
                if required:
                    raise SoftException("missing 'teamSpawnPoints/%s'" % (nodeNameTemplate % teamIdx))
            for value in s.values():
                teamSpawnPoint.append(value.readVector2(''))

        return allTeamSpawnPoints


def __readGameplayPoints(section, geometryCfg):
    sps = []
    aps = []
    rps = {}
    rsps = []
    swps = []
    repairPointIDByGUID = geometryCfg.setdefault('repairPointIDByGUID', {})
    for name, value in section.items():
        if name == 'flagSpawnPoint':
            sps.append({'position': value.readVector3('position'),
             'team': value.readInt('team'),
             'winPoints': value.readFloat('winPoints')})
        if name == 'flagAbsorptionPoint':
            aps.append({'position': value.readVector3('position'),
             'team': value.readInt('team'),
             'guid': value.readString('guid')})
        if name == 'repairPoint':
            guid = value.readString('guid')
            point = {'position': value.readVector3('position'),
             'team': value.readInt('team'),
             'radius': value.readFloat('radius'),
             'cooldown': value.readFloat('cooldown'),
             'repairTime': value.readFloat('repairTime'),
             'repairFlags': value.readInt('repairFlags'),
             'guid': guid}
            baseID = repairPointIDByGUID.get(guid, len(repairPointIDByGUID))
            rps[baseID] = point
            repairPointIDByGUID[guid] = baseID
        if name == 'resourcePoint':
            rsps.append({'position': value.readVector3('position'),
             'radius': value.readFloat('radius'),
             'startDelay': value.readFloat('startDelay'),
             'cooldown': value.readFloat('cooldown'),
             'damageLockTime': value.readFloat('damageLockTime'),
             'amount': value.readInt('amount'),
             'absorptionSpeed': value.readFloat('absorptionSpeed'),
             'reuseCount': value.readInt('reuseCount'),
             'team': value.readInt('team'),
             'guid': value.readString('guid')})
        if name == 'sectorWayPoint':
            swps.append({'position': value.readVector3('position'),
             'team': value.readInt('team')})

    cfg = {'flagSpawnPoints': sps,
     'flagAbsorptionPoints': aps,
     'repairPoints': rps,
     'resourcePoints': rsps,
     'sectorWayPoints': swps}
    return cfg


def __readWinPoints(section):
    return {'winPointsSettings': section.readString('winPoints', 'DEFAULT')}


def readVisualScriptSection(section):
    return _readVisualScript(section)
