# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ArenaType.py
from collections import defaultdict
import ResMgr
from constants import IS_BOT, IS_WEB, IS_CLIENT, ARENA_TYPE_XML_PATH, ARENA_GUI_TYPE_LABEL
from constants import ARENA_GAMEPLAY_IDS, TEAMS_IN_ARENA, ARENA_GAMEPLAY_NAMES
from constants import IS_CELLAPP, IS_BASEAPP
from items.vehicles import CAMOUFLAGE_KINDS
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG_DEV
from GasAttackSettings import GasAttackSettings
from items import _xml
from BossModeSettings import BossModeSettings
if IS_CLIENT:
    from helpers import i18n
    import WWISE
elif IS_WEB:
    from web_stubs import *
if IS_CELLAPP or IS_BASEAPP:
    from server_constants import ARENA_ESTIMATED_LOAD_DEFAULT
g_cache = {}
g_geometryCache = {}
g_geometryNamesToIDs = {}
g_gameplayNames = set()
g_gameplaysMask = 0

def getVisibilityMask(gameplayID):
    return 1 << gameplayID


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


_DEFAULT_XML = ARENA_TYPE_XML_PATH + '_default_.xml'

def init():
    global g_gameplayNames
    global g_cache
    global g_geometryNamesToIDs
    global g_gameplaysMask
    rootSection = ResMgr.openSection(ARENA_TYPE_XML_PATH + '_list_.xml')
    if rootSection is None:
        raise Exception("Can't open '%s'" % (ARENA_TYPE_XML_PATH + '_list_.xml'))
    defaultXml = ResMgr.openSection(_DEFAULT_XML)
    if defaultXml is None:
        raise Exception("Can't open '%s'" % _DEFAULT_XML)
    defaultGameplayTypesXml = defaultXml['gameplayTypes']
    if defaultGameplayTypesXml is None or not defaultGameplayTypesXml:
        raise Exception("No defaults for 'gameplayTypes'")
    geometriesSet = set()
    for key, value in rootSection.items():
        geometryID = value.readInt('id')
        if geometryID in geometriesSet:
            raise Exception('Geometry ID=%d is not unique' % geometryID)
        geometriesSet.add(geometryID)
        __buildCache(geometryID, value.readString('name'), defaultXml)

    g_gameplaysMask = getGameplaysMask(g_gameplayNames)
    g_geometryNamesToIDs = dict([ (arenaType.geometryName, arenaType.geometryID) for arenaType in g_cache.itervalues() ])
    return


class ArenaType(object):

    def __init__(self, geometryCfg, gameplayCfg):
        self.__geometryCfg = geometryCfg
        self.__gameplayCfg = gameplayCfg
        self.__gameplayCfg['id'] = gameplayCfg['gameplayID'] << 16 | geometryCfg['geometryID']
        if self.maxPlayersInTeam < self.minPlayersInTeam:
            raise Exception("'maxPlayersInTeam' value < 'minPlayersInTeam' value")

    def __getattr__(self, name):
        return self.__gameplayCfg[name] if name in self.__gameplayCfg else self.__geometryCfg.get(name, None)


class GeometryType(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


def __buildCache(geometryID, geometryName, defaultXml):
    global g_geometryCache
    sectionName = ARENA_TYPE_XML_PATH + geometryName + '.xml'
    section = ResMgr.openSection(sectionName)
    if section is None:
        raise Exception("Can't open '%s'" % sectionName)
    geometryCfg = __readGeometryCfg(geometryID, geometryName, section, defaultXml)
    g_geometryCache[geometryID] = GeometryType(geometryCfg)
    for gameplayCfg in __readGameplayCfgs(geometryName, section, defaultXml, geometryCfg):
        arenaType = ArenaType(geometryCfg, gameplayCfg)
        g_cache[arenaType.id] = arenaType
        g_gameplayNames.add(arenaType.gameplayName)

    return


def __readGeometryCfg(geometryID, geometryName, section, defaultXml):
    try:
        cfg = {}
        cfg['geometryID'] = geometryID
        cfg['geometryName'] = geometryName
        cfg['geometry'] = __readString('geometry', section, defaultXml)
        cfg['boundingBox'] = __readBoundingBox(section)
        cfg['weatherPresets'] = __readWeatherPresets(section)
        cfg['vehicleCamouflageKind'] = __readVehicleCamouflageKind(section)
        if IS_CELLAPP or IS_BASEAPP:
            cfg['estimatedLoad'] = __readFloat('estimatedLoad', section, defaultXml, ARENA_ESTIMATED_LOAD_DEFAULT)
        if IS_CLIENT or IS_WEB:
            cfg['name'] = i18n.makeString(__readString('name', section, defaultXml))
        if IS_CLIENT:
            cfg['umbraEnabled'] = __readInt('umbraEnabled', section, defaultXml)
            cfg['defaultReverbPreset'] = __readString('defaultReverbPreset', section, defaultXml).strip()
            cfg['batchingEnabled'] = __readInt('batchingEnabled', section, defaultXml)
            cfg['waterTexScale'] = section.readFloat('water/texScale', 0.5)
            cfg['waterFreqX'] = section.readFloat('water/freqX', 1.0)
            cfg['waterFreqZ'] = section.readFloat('water/freqZ', 1.0)
            cfg['defaultGroundEffect'] = __readDefaultGroundEffect(section, defaultXml)
        cfg.update(__readCommonCfg(section, defaultXml, True, {}))
    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise Exception("Wrong arena type XML '%s' : %s" % (geometryName, str(e)))

    return cfg


def __readGameplayCfgs(geometryName, section, defaultXml, geometryCfg):
    try:
        if section['gameplayTypes'] is None:
            gameplayName = 'ctf'
            gameplayID = getGameplayIDForName(gameplayName)
            return [{'gameplayID': gameplayID,
              'gameplayName': gameplayName}]
        if not section['gameplayTypes']:
            raise Exception("no 'gameplayTypes' section")
        cfgs = []
        defaultGameplayTypesXml = defaultXml['gameplayTypes']
        for name, subsection in section['gameplayTypes'].items():
            defaultSubsection = defaultGameplayTypesXml[name]
            if defaultSubsection is None:
                raise Exception("no defaults for '%s'" % name)
            cfgs.append(__readGameplayCfg(name, subsection, defaultSubsection, geometryCfg))

    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise Exception("Wrong arena type XML '%s' : %s" % (geometryName, e))

    return cfgs


def __readGameplayCfg(gameplayName, section, defaultXml, geometryCfg):
    try:
        cfg = {}
        cfg['gameplayID'] = getGameplayIDForName(gameplayName)
        cfg['gameplayName'] = gameplayName
        for setting in ('battleEndWarningAppearTime', 'battleEndWarningDuration', 'battleEndingSoonTime'):
            cfg[setting] = 0
            if not gameplayName.startswith('fallout') and __hasKey(setting, section, defaultXml):
                cfg[setting] = __readInt(setting, section, defaultXml)

        if gameplayName == 'nations':
            raise Exception('national battles are disabled')
        if __hasKey('bossModes', section, defaultXml):
            cfg['bossModes'] = __readBossModes(section['bossModes'])
        else:
            cfg['bossModes'] = None
        cfg.update(__readCommonCfg(section, defaultXml, False, geometryCfg))
    except Exception as e:
        LOG_CURRENT_EXCEPTION()
        raise Exception("wrong gameplay section '%s' : %s" % (gameplayName, e))

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
        cfg['runDelay'] = __readInt('runDelay', section, defaultXml)
    if raiseIfMissing or __hasKey('roundLength', section, defaultXml):
        cfg['roundLength'] = __readInt('roundLength', section, defaultXml)
    if raiseIfMissing or __hasKey('winnerIfTimeout', section, defaultXml):
        cfg['winnerIfTimeout'] = __readInt('winnerIfTimeout', section, defaultXml)
    if raiseIfMissing or __hasKey('winnerIfExtermination', section, defaultXml):
        cfg['winnerIfExtermination'] = __readInt('winnerIfExtermination', section, defaultXml)
    if raiseIfMissing or __hasKey('artilleryPreparationChance', section, defaultXml):
        cfg['artilleryPreparationChance'] = __readFloat('artilleryPreparationChance', section, defaultXml)
    if raiseIfMissing or section.has_key('mapActivities'):
        cfg['mapActivitiesTimeframes'] = __readMapActivitiesTimeframes(section)
    if raiseIfMissing or section.has_key('boundingBox'):
        cfg['boundingBox'] = __readBoundingBox(section)
    maxTeamsInArena = cfg.get('maxTeamsInArena', geometryCfg.get('maxTeamsInArena', None))
    assert maxTeamsInArena is not None
    cfg.update(__readWinPoints(section))
    cfg.update(__readGameplayPoints(section, geometryCfg))
    cfg['teamBasePositions'] = __readTeamBasePositions(section, maxTeamsInArena)
    cfg['teamSpawnPoints'] = __readTeamSpawnPoints(section, maxTeamsInArena)
    cfg['squadTeamNumbers'], cfg['soloTeamNumbers'] = __readTeamNumbers(section, maxTeamsInArena)
    if raiseIfMissing or __hasKey('numPlayerGroups', section, defaultXml):
        cfg['numPlayerGroups'] = __readInt('numPlayerGroups', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('playerGroupLimit', section, defaultXml):
        cfg['playerGroupLimit'] = __readInt('playerGroupLimit', section, defaultXml, 0)
    if raiseIfMissing or __hasKey('crystalRewardFactor', section, defaultXml):
        cfg['crystalRewardFactor'] = __readFloat('crystalRewardFactor', section, defaultXml, 1.0)
    if IS_CLIENT or IS_WEB:
        if raiseIfMissing or __hasKey('description', section, defaultXml):
            cfg['description'] = i18n.makeString(__readString('description', section, defaultXml))
        if raiseIfMissing or __hasKey('minimap', section, defaultXml):
            cfg['minimap'] = __readString('minimap', section, defaultXml)
        if raiseIfMissing or __hasKey('wwambientSound', section, defaultXml):
            cfg['ambientSound'] = __readString('wwambientSound', section, defaultXml)
        musicSetup = None
        if raiseIfMissing or __hasKey('wwmusicSetup', section, defaultXml):
            musicSetup = __readWWmusicSection(section, defaultXml)
        if musicSetup is not None:
            cfg['wwmusicSetup'] = musicSetup
        wwmusicDroneSetup = 'wwmusicDroneSetup'
        if raiseIfMissing or __hasKey(wwmusicDroneSetup, section, defaultXml):
            cfg[wwmusicDroneSetup] = __readWWmusicDroneSection(wwmusicDroneSetup, section, defaultXml)
        if raiseIfMissing or __hasKey('wwbattleCountdownTimerSound', section, defaultXml):
            cfg['battleCountdownTimerSound'] = __readString('wwbattleCountdownTimerSound', section, defaultXml)
        if raiseIfMissing or section.has_key('mapActivities'):
            cfg['mapActivitiesSection'] = section['mapActivities']
        if section.has_key('soundRemapping'):
            cfg['soundRemapping'] = section['soundRemapping']
    if IS_CLIENT or IS_BOT:
        cfg['controlPoints'] = __readControlPoints(section)
        cfg['teamLowLevelSpawnPoints'] = __readTeamSpawnPoints(section, maxTeamsInArena, nodeNameTemplate='team%d_low', required=False)
        cfg['botPoints'] = __readBotPoints(section)
    if __hasKey('gasAttack', section, defaultXml):
        gasAttackSection = section['gasAttack']
        cfg['gasAttackSettings'] = __readGasAttackSettings(gasAttackSection['gameplaySettings'])
        if IS_CLIENT:
            from battleground import gas_attack
            cfg['gasAttackVisual'] = gas_attack.GasAttackMapSettings.fromSection(gasAttackSection['visualSettings'])
    elif raiseIfMissing:
        cfg['gasAttackSettings'] = None
        cfg['gasAttackVisual'] = None
    if not IS_CLIENT:
        if raiseIfMissing or __hasKey('battleScenarios', section, defaultXml):
            cfg['battleScenarios'] = __readBattleScenarios(section, defaultXml)
        if raiseIfMissing or __hasKey('waypoints', section, defaultXml):
            cfg['waypoints'] = __readString('waypoints', section, defaultXml)
    return cfg


def __readWWmusicSection(section, defaultXml):
    wwmusic = None
    if __hasKey('wwmusicSetup', section, defaultXml):
        wwmusic = dict()
        dataSection = section if section.has_key('wwmusicSetup') else defaultXml
        for name, value in _xml.getChildren(defaultXml, dataSection, 'wwmusicSetup'):
            wwmusic[name] = value.asString

    return wwmusic


def __readWWmusicDroneSection(wwmusicDroneSetup, section, defaultXml):
    """
    Parses wwmusicDroneSetup section from current xml.
    Example:
        <wwmusicDroneSetup>
            <timeRemained>
                <value> 20 </value>
                <arena_type_label> ARENA_GUI_TYPE_LABEL.LABELS.* </arena_type_label>
                <gameplay_name> ARENA_GAMEPLAY_NAMES.* </gameplay_name>
            </timeRemained>
            ...
        </wwmusicDroneSetup>
    :param wwmusicDroneSetup: the name of tag 'wwmusicDroneSetup'
    :param section: current arena xml
    :param defaultXml: /arena_defs/_default_.xml
    :return: dict: {settingName: {(ARENA_GUI_TYPE_LABEL.LABELS.*, ARENA_GAMEPLAY_NAMES.*): value, ...}...}
    """
    dataSection = section if section.has_key(wwmusicDroneSetup) else defaultXml
    outcome = defaultdict(dict)
    droneChildren = sorted(_xml.getChildren(defaultXml, dataSection, wwmusicDroneSetup), key=lambda item: len(item[1].items()))
    valueTag = 'value'
    for settingName, settingChildren in droneChildren:
        if settingChildren.has_key(valueTag):
            settingValue = settingChildren.readInt(valueTag)
            if settingChildren.has_key('arena_type_label'):
                if settingChildren.has_key('gameplay_name'):
                    gameplayType = settingChildren.readString('gameplay_name')
                    arenaTypeLabel = settingChildren.readString('arena_type_label')
                    outcome[settingName][arenaTypeLabel, gameplayType] = settingValue
                else:
                    arenaTypeLabel = settingChildren.readString('arena_type_label')
                    for gameplayType in ARENA_GAMEPLAY_NAMES:
                        outcome[settingName][arenaTypeLabel, gameplayType] = settingValue

            elif settingChildren.has_key('gameplay_name'):
                gameplayType = settingChildren.readString('gameplay_name')
                for arenaTypeLabel in ARENA_GUI_TYPE_LABEL.LABELS.itervalues():
                    outcome[settingName][arenaTypeLabel, gameplayType] = settingValue

            else:
                for arenaTypeLabel in ARENA_GUI_TYPE_LABEL.LABELS.itervalues():
                    for gameplayType in ARENA_GAMEPLAY_NAMES:
                        outcome[settingName][arenaTypeLabel, gameplayType] = settingValue

        raise Exception('"{}" section missed the key "{}"!'.format(settingName, valueTag))

    return dict(outcome)


def __hasKey(key, xml, defaultXml):
    return xml.has_key(key) or defaultXml.has_key(key)


def __readString(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readString(key)
    elif defaultXml.has_key(key):
        return defaultXml.readString(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise Exception("missing key '%s'" % key)
        return


def __readStrings(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readStrings(key)
    elif defaultXml.has_key(key):
        return defaultXml.readStrings(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise Exception("missing key '%s'" % key)
        return


def __readInt(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readInt(key)
    elif defaultXml.has_key(key):
        return defaultXml.readInt(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise Exception("missing key '%s'" % key)
        return


def __readFloat(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readFloat(key)
    elif defaultXml.has_key(key):
        return defaultXml.readFloat(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise Exception("missing key '%s'" % key)
        return


def __readBool(key, xml, defaultXml, defaultValue=None):
    if xml.has_key(key):
        return xml.readBool(key)
    elif defaultXml.has_key(key):
        return defaultXml.readBool(key)
    elif defaultValue is not None:
        return defaultValue
    else:
        raise Exception("missing key '%s'" % key)
        return


def __readBoundingBox(section):
    bottomLeft = section.readVector2('boundingBox/bottomLeft')
    upperRight = section.readVector2('boundingBox/upperRight')
    if bottomLeft[0] >= upperRight[0] or bottomLeft[1] >= upperRight[1]:
        raise Exception("wrong 'boundingBox' values")
    return (bottomLeft, upperRight)


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


def __readBattleScenarios(section, defaultSection):
    section = section['battleScenarios']
    if section is None:
        section = defaultSection['battleScenarios']
    res = {}
    if section.has_key('scenario'):
        res['default'] = section.readStrings('scenario')
    for name, subsection in section.items():
        if name == 'level':
            level = subsection.readInt('id')
            if level in res:
                raise Exception('duplicate level %d' % level)
            if subsection.has_key('scenario'):
                res[level] = subsection.readStrings('scenario')
            else:
                raise Exception('missing scenarios for level %d' % level)

    return res


def __readVehicleCamouflageKind(section):
    kindName = section.readString('vehicleCamouflageKind')
    kind = CAMOUFLAGE_KINDS.get(kindName)
    if kind is None:
        raise Exception("missing or wrong section 'vehicleCamouflageKind'")
    return kind


def __readMinPlayersInTeam(section, defaultXml):
    minPlayersInTeam = __readInt('minPlayersInTeam', section, defaultXml)
    if minPlayersInTeam < 0:
        raise Exception("wrong 'minPlayersInTeam' value")
    return minPlayersInTeam


def __readMaxPlayersInTeam(section, defaultXml):
    maxPlayersInTeam = __readInt('maxPlayersInTeam', section, defaultXml)
    if maxPlayersInTeam < 0:
        raise Exception("wrong 'maxPlayersInTeam' value")
    return maxPlayersInTeam


def __readTeamsCount(key, section, defaultXml):
    value = __readInt(key, section, defaultXml)
    if not TEAMS_IN_ARENA.MIN_TEAMS <= value <= TEAMS_IN_ARENA.MAX_TEAMS:
        raise Exception('Invalid teams in arena')
    return value


def __readTeamNumbers(section, maxTeamsInArena):
    if not (section.has_key('squadTeamNumbers') or section.has_key('soloTeamNumbers')):
        if maxTeamsInArena > 2:
            raise 'For multiteam mode squadTeamNumbers and (or) soloTeamNumbers must be set'
        return (set(), set())
    squadTeamNumbers = set([ int(v) for v in section.readString('squadTeamNumbers', '').split() ])
    soloTeamNumbers = set([ int(v) for v in section.readString('soloTeamNumbers', '').split() ])
    if len(squadTeamNumbers) + len(soloTeamNumbers) != maxTeamsInArena:
        raise Exception('Number of squad (%d) and solo (%d) teams must be equal to maxTeamsInArena (%d)' % (len(squadTeamNumbers), len(soloTeamNumbers), maxTeamsInArena))
    if len(squadTeamNumbers & soloTeamNumbers) > 0:
        raise Exception('Squad and solo team numbers contains identical team numbers (%s)' % str(squadTeamNumbers & soloTeamNumbers))
    allTeamNumbers = squadTeamNumbers | soloTeamNumbers
    if min(allTeamNumbers) < 1 or max(allTeamNumbers) > TEAMS_IN_ARENA.MAX_TEAMS:
        raise Exception('Invalid team number. Must be between 1 and %d.' % TEAMS_IN_ARENA.MAX_TEAMS)
    return (squadTeamNumbers, soloTeamNumbers)


def __readMapActivitiesTimeframes(section):
    mapActivitiesXML = section['mapActivities']
    if not mapActivitiesXML:
        return []
    timeframes = []
    for activityXML in mapActivitiesXML.values():
        startTimes = activityXML.readVector2('startTime')
        if (startTimes[0] >= 0) != (startTimes[1] >= 0):
            raise Exception("wrong subsection 'mapActivities/startTime'. All values of startTime must have same sign")
        possibility = activityXML.readFloat('possibility', 1.0)
        visibilityMask = activityXML.readInt('visibilityMask', 255)
        timeframes.append((startTimes[0],
         startTimes[1],
         possibility,
         visibilityMask))

    return timeframes


def __readDefaultGroundEffect(section, defaultXml):
    defaultGroundEff = __readString('defaultGroundEffect', section, defaultXml).strip()
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
                    raise Exception("wrong subsection 'teamBasePositions/team%s/%s'" % (teamIdx, s.name))

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
                    raise Exception("missing 'teamSpawnPoints/%s'" % (nodeNameTemplate % teamIdx))
            for value in s.values():
                teamSpawnPoint.append(value.readVector2(''))

        return allTeamSpawnPoints


def __readGameplayPoints(section, geometryCfg):
    sps = []
    aps = []
    rps = {}
    rsps = []
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

    cfg = {'flagSpawnPoints': sps,
     'flagAbsorptionPoints': aps,
     'repairPoints': rps,
     'resourcePoints': rsps}
    return cfg


def __readGasAttackSettings(section):
    return GasAttackSettings(section.readInt('attackLength'), section.readFloat('preparationPeriod'), section.readVector3('position'), section.readFloat('startRadius'), section.readFloat('endRadius'), section.readFloat('compressionTime'))


def __readWinPoints(section):
    return {'winPointsSettings': section.readString('winPoints', 'DEFAULT')}


def __readBossModes(section):
    settings = BossModeSettings(section.readString('botName'))
    if section.has_key('team'):
        settings.setTeamNum(section.readInt('team'))
    if section.has_key('mineRadius'):
        settings.setMineRadius(section.readFloat('mineRadius'))
    if section.has_key('mineDamage'):
        settings.setMineDamage(section.readInt('mineDamage'))
    if section.has_key('mineDuration'):
        settings.setMineDuration(section.readFloat('mineDuration'))
    if section.has_key('mineActivationDelay'):
        settings.setMineActivationDelay(section.readFloat('mineActivationDelay'))
    if section.has_key('mineModelActivationDelay'):
        settings.setMineModelActivationDelay(section.readFloat('mineModelActivationDelay'))
    if section.has_key('mineEffects'):
        settings.setMineEffects(section['mineEffects'])
    if section.has_key('healthPowerupRadius'):
        settings.setHealthPowerupRadius(section.readFloat('healthPowerupRadius'))
    if section.has_key('healthPowerupDuration'):
        settings.setHealthPowerupDuration(section.readFloat('healthPowerupDuration'))
    if section.has_key('healthPowerupHealAmount'):
        settings.setHealthPowerupHealAmount(section.readInt('healthPowerupHealAmount'))
    if section.has_key('healthPowerupEffects'):
        settings.setHealthPowerupEffects(section['healthPowerupEffects'])
    for name, value in section.items():
        if name == 'phase':
            events = []
            for phaseKey, phaseValue in value.items():
                if phaseKey == 'health':
                    health = phaseValue.readFloat('')
                if phaseKey == 'event':
                    event = {'name': phaseValue.readString('')}
                    for eventKey, eventValue in phaseValue.items():
                        event[eventKey] = eventValue.readFloat('')

                    events.append(event)

            settings.addPhase(health, events)
        if name == 'minionEvent':
            minionEvents = []
            for phaseKey, phaseValue in value.items():
                if phaseKey == 'health':
                    health = phaseValue.readFloat('')
                if phaseKey == 'event':
                    event = {'name': phaseValue.readString('')}
                    for eventKey, eventValue in phaseValue.items():
                        event[eventKey] = eventValue.readFloat('')

                    minionEvents.append(event)

            settings.addMinionEvent(health, minionEvents)
        if name == 'mineModels':
            for key, modelData in value.items():
                for tagKey, model in modelData.items():
                    modelName = model.readString('')
                    actionName = model.readString('action')
                    settings.addMineModels(key, modelName, actionName)

        if name == 'healthPowerupModels':
            for key, modelData in value.items():
                for tagKey, model in modelData.items():
                    modelName = model.readString('')
                    actionName = model.readString('action')
                    settings.addHealthPowerupModels(key, modelName, actionName)

        if name == 'pathProgressData':
            for key, segment in value.items():
                segmentName = segment.readString('')
                startingProgressFraction = segment.readFloat('startingProgressFraction')
                endingProgressFraction = segment.readFloat('endingProgressFraction')
                segmentLength = segment.readFloat('segmentLength')
                settings.addPathProgressSegment(segmentName, startingProgressFraction, endingProgressFraction, segmentLength)

    return settings
