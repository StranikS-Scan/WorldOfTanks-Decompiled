# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ArenaType.py
# Compiled at: 2011-11-01 17:33:27
import ResMgr
from debug_utils import *
from constants import IS_CLIENT, IS_BASEAPP, IS_WEB, ARENA_TYPE_XML_PATH, ARENA_GAMEPLAY_TYPE
from constants import IS_CELLAPP
_COMMON_XML = ARENA_TYPE_XML_PATH + '_common_.xml'
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:

    class i18n():

        @staticmethod
        def makeString(name):
            return name


g_list = None
g_cache = None
GAMEPLAY_TYPE_TO_VISIBILITY_MASK = {ARENA_GAMEPLAY_TYPE.STANDARD: 1 << 0,
 ARENA_GAMEPLAY_TYPE.TYPE_1: 1 << 1,
 ARENA_GAMEPLAY_TYPE.TYPE_2: 1 << 2,
 ARENA_GAMEPLAY_TYPE.TYPE_3: 1 << 3,
 ARENA_GAMEPLAY_TYPE.TYPE_4: 1 << 4,
 ARENA_GAMEPLAY_TYPE.TYPE_5: 1 << 5,
 ARENA_GAMEPLAY_TYPE.TYPE_6: 1 << 6}
_GAMEPLAY_TYPE_TO_NAME = {ARENA_GAMEPLAY_TYPE.STANDARD: 'ctf',
 ARENA_GAMEPLAY_TYPE.TYPE_1: 'domination',
 ARENA_GAMEPLAY_TYPE.TYPE_2: 'assault',
 ARENA_GAMEPLAY_TYPE.TYPE_3: 'escort',
 ARENA_GAMEPLAY_TYPE.TYPE_4: 'ctf2',
 ARENA_GAMEPLAY_TYPE.TYPE_5: 'domination2',
 ARENA_GAMEPLAY_TYPE.TYPE_6: 'assault2'}
_GAMEPLAY_TYPE_FROM_NAME = dict(((x[1], x[0]) for x in _GAMEPLAY_TYPE_TO_NAME.iteritems()))

def init(preloadAll=not IS_CLIENT):
    global g_list
    global g_cache
    g_cache = Cache()
    g_list = List()
    rootSection = ResMgr.openSection(ARENA_TYPE_XML_PATH + '_list_.xml')
    if rootSection is None:
        raise Exception, "Can't open '%s'" % ARENA_TYPE_XML_PATH + '_list_.xml'
    for key, value in rootSection.items():
        typeID = value.readInt('id')
        if g_list.has_key(typeID):
            raise Exception, 'Arena type ID=%d is not unique' % typeID
        g_list[typeID] = value.readString('name')
        if preloadAll:
            g_cache.get(typeID)

    return


def reload():
    from sys import modules
    import __builtin__
    __builtin__.reload(modules[reload.__module__])
    init()


class ArenaType(object):

    def __init__(self, typeID, typeName, section, commonXml):
        self.typeID = typeID
        self.typeName = typeName
        self.geometry = self.__readString('geometry', section, commonXml)
        self.minPlayersInTeam = self.__readInt('minPlayersInTeam', section, commonXml)
        if self.minPlayersInTeam < 0:
            self.__raiseWrongXml("wrong 'minPlayersInTeam' value")
        self.maxPlayersInTeam = self.__readInt('maxPlayersInTeam', section, commonXml)
        if self.maxPlayersInTeam < 0:
            self.__raiseWrongXml("wrong 'maxPlayersInTeam' value")
        if self.maxPlayersInTeam < self.minPlayersInTeam:
            self.__raiseWrongXml("'maxPlayersInTeam' value < 'minPlayersInTeam' value")
        self.roundLength = self.__readInt('roundLength', section, commonXml)
        if self.roundLength < 0:
            self.__raiseWrongXml("wrong 'roundLength' value")
        bottomLeft = section.readVector2('boundingBox/bottomLeft')
        upperRight = section.readVector2('boundingBox/upperRight')
        if bottomLeft[0] >= upperRight[0] or bottomLeft[1] >= upperRight[1]:
            self.__raiseWrongXml("wrong 'boundingBox' values")
        self.boundingBox = (bottomLeft, upperRight)
        self.weatherPresets = self.__readWeatherPresets(section)
        if IS_CLIENT or IS_WEB:
            self.name = i18n.makeString(self.__readString('name', section, commonXml))
            self.description = i18n.makeString(self.__readString('description', section, commonXml))
            self.defaultMinimap = self.__readString('defaultMinimap', section, commonXml)
            self.music = self.__readString('music', section, commonXml)
            self.loadingMusic = self.__readString('loadingMusic', section, commonXml)
            self.ambientSound = self.__readString('ambientSound', section, commonXml)
        if IS_CLIENT:
            self.umbraEnabled = self.__readInt('umbraEnabled', section, commonXml)
            self.batchingEnabled = self.__readInt('batchingEnabled', section, commonXml)
            self.waterTexScale = section.readFloat('water/texScale', 0.5)
            self.waterFreqX = section.readFloat('water/freqX', 1.0)
            self.waterFreqZ = section.readFloat('water/freqZ', 1.0)
            self.defaultGroundEffect = None
            defaultGroundEff = section.readString('defaultGroundEffect').strip()
            if defaultGroundEff == '':
                defaultGroundEff = commonXml.readString('defaultGroundEffect').strip()
            if defaultGroundEff != '':
                if defaultGroundEff.find('|') != -1:
                    defaultGroundEff = defaultGroundEff.split('|')
                    for i in xrange(0, len(defaultGroundEff)):
                        defaultGroundEff[i] = defaultGroundEff[i].strip()

                self.defaultGroundEffect = defaultGroundEff
        if IS_BASEAPP or IS_WEB:
            self.kickAfterFinishWaitTime = self.__readFloat('kickAfterFinishWaitTime', section, commonXml)
            if self.kickAfterFinishWaitTime < 0:
                self.__raiseWrongXml("wrong 'kickAfterFinishWaitTime' value")
            self.arenaStartDelay = self.__readFloat('arenaStartDelay', section, commonXml)
            if self.arenaStartDelay <= 0:
                self.__raiseWrongXml("wrong 'arenaStartDelay' value")
        if IS_CELLAPP:
            if section.has_key('useAdvancedPhysics'):
                self.useAdvancedPhysics = section.readBool('useAdvancedPhysics')
            else:
                self.useAdvancedPhysics = False
        self.subtypeIDs, self.gameplayTypes = self.__readSubtypes(section)
        return

    def __readString(self, key, xml, commonXml):
        value = xml.readString(key)
        if value == '':
            value = commonXml.readString(key)
            if value == '':
                self.__raiseWrongXml("missing key '%s'" % key)
        return value

    def __readFloat(self, key, xml, commonXml):
        value = xml.readFloat(key, -1.0)
        if value == -1.0:
            value = commonXml.readFloat(key, -1.0)
            if value == -1.0:
                self.__raiseWrongXml("missing key '%s'" % key)
        return value

    def __readInt(self, key, xml, commonXml):
        value = xml.readInt(key, -1)
        if value == -1:
            value = commonXml.readInt(key, -1)
            if value == -1:
                self.__raiseWrongXml("missing key '%s'" % key)
        return value

    def __readWeatherPresets(self, section):
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

    def __readSubtypes(self, section):
        subsection = section['gameplayTypes']
        if subsection is None:
            descrs = None
            gid = ARENA_GAMEPLAY_TYPE.STANDARD
            descrs = {gid: {'winnerIfTimeout': 0}}
            if IS_CLIENT:
                descrs[gid]['minimap'] = self.defaultMinimap
            return ((self.typeID + (gid << 16),), descrs)
        else:
            if not subsection:
                self.__raiseWrongXml('no <gameplayTypes> are specified')
            ids = []
            descrs = {}
            for name, subsection in subsection.items():
                gid = _GAMEPLAY_TYPE_FROM_NAME.get(name)
                if gid is None:
                    self.__raiseWrongXml("unknown name '%s' in <gameplayTypes>" % name)
                ids.append(self.typeID + (gid << 16))
                descrs[gid] = {'winnerIfTimeout': subsection.readInt('winnerIfTimeout', 0)}
                if not IS_CLIENT:
                    continue
                s = subsection['minimap']
                descrs[gid]['minimap'] = s.asString if s is not None else self.defaultMinimap
                self.__readOptionalTeamPositionsAsDicts(descrs[gid], subsection, 'teamBasePositions', name)
                self.__readOptionalTeamPositionsAsLists(descrs[gid], subsection, 'teamSpawnPoints', name)
                s = subsection['controlPoint']
                if s is not None:
                    descrs[gid]['controlPoint'] = s.asVector2

            return (tuple(ids), descrs)

    def __readOptionalTeamPositionsAsDicts(self, descr, section, subsectionName, gameplayTypeName):
        section = section[subsectionName]
        if section is None:
            return
        else:
            teams = ({}, {})
            for teamIdx, teamTag in ((0, 'team1'), (1, 'team2')):
                s = section[teamTag]
                if s is None:
                    self.__raiseWrongXml('missing subsection gameplayTypes/%s/%s/%s' % (gameplayTypeName, subsectionName, teamTag))
                for s in s.values():
                    try:
                        id = int(s.name[8:])
                    except:
                        self.__raiseWrongXml('wrong subsection gameplayTypes/%s/%s/%s/%s' % (gameplayTypeName,
                         subsectionName,
                         teamTag,
                         s.name))

                    teams[teamIdx][id] = s.asVector2

            descr[subsectionName] = teams
            return

    def __readOptionalTeamPositionsAsLists(self, descr, section, subsectionName, gameplayTypeName):
        section = section[subsectionName]
        if section is None:
            return
        else:
            teams = ([], [])
            for teamIdx, teamTag in ((0, 'team1'), (1, 'team2')):
                s = section[teamTag]
                if s is None:
                    self.__raiseWrongXml('missing subsection gameplayTypes/%s/%s/%s' % (gameplayTypeName, subsectionName, teamTag))
                teams[teamIdx].extend(s.readVector2s('position'))

            descr[subsectionName] = teams
            return

    def __raiseWrongXml(self, msg):
        raise Exception, "wrong arena type XML '%s': %s" % (self.typeName, msg)


class List(dict):

    def __getitem__(self, typeID):
        return dict.__getitem__(self, typeID & 65535)

    def __contains__(self, typeID):
        return dict.__contains__(self, typeID & 65535)

    def get(self, typeID, defVal=None):
        return dict.get(self, typeID & 65535, defVal)

    def has_key(self, typeID):
        return dict.has_key(self, typeID & 65535)


class Cache(object):

    def __init__(self):
        self.__cont = {}
        self.__commonXml = ResMgr.openSection(_COMMON_XML)
        if self.__commonXml is None:
            raise NameError, 'can not open ' + _COMMON_XML
        return

    def get(self, typeID):
        typeID &= 65535
        ct = self.__cont.get(typeID)
        if ct:
            return ct
        else:
            typeName = g_list.get(typeID, None)
            if typeName is None:
                raise NameError, 'can not get arena type name (%d)' % typeID
            sectionName = ARENA_TYPE_XML_PATH + typeName + '.xml'
            section = ResMgr.openSection(sectionName)
            if section is None:
                raise NameError, "can not open '%s'" % sectionName
            ct = ArenaType(typeID, typeName, section, self.__commonXml)
            self.__cont[typeID] = ct
            section = None
            ResMgr.purge(sectionName, True)
            return ct

    def clear(self):
        self.__cont.clear()
