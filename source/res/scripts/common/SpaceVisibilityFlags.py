# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/SpaceVisibilityFlags.py
from constants import ARENA_GAMEPLAY_IDS, HANGAR_VISIBILITY_TAGS
import ResMgr
from soft_exception import SoftException
from debug_utils import LOG_WARNING

class SpaceVisibilityFlagsFactory(object):
    _g_cache = {}

    @staticmethod
    def create(geometryName):
        if geometryName not in SpaceVisibilityFlagsFactory._g_cache:
            SpaceVisibilityFlagsFactory._g_cache[geometryName] = SpaceVisibilityFlags(geometryName)
        return SpaceVisibilityFlagsFactory._g_cache[geometryName]


class SpaceVisibilityFlags(object):
    FLAGS_CONFIG_SECTION = 'spaceVisibilityFlags'
    _CONFIG_FILE = 'space.settings'
    _HANGAR_CONFIG_SECTION = 'hangarSettings'
    _CONFIG_DIRECTORY = 'spaces'
    _ERROR_BIT_INDEX = -1
    _SERVER_FLAGS_NUMBER = 20

    def __init__(self, geometryName):
        settingsPath = SpaceVisibilityFlags.__formSettingPath(geometryName)
        settingsSection = _openSection(settingsPath)
        flagsSection = None
        self.types = ARENA_GAMEPLAY_IDS
        if settingsSection is not None:
            flagsSection = settingsSection[SpaceVisibilityFlags.FLAGS_CONFIG_SECTION]
            if SpaceVisibilityFlags.__isHangarSpace(settingsSection):
                self.types = HANGAR_VISIBILITY_TAGS.IDS
        self.typeIDToIndex = {}
        if not self.__formMapping(flagsSection):
            raise SoftException('Cannot create SpaceVisibilityFlags for space.settings %s' % settingsPath)
        return

    def getMaskForGameplayID(self, gameplayID):
        return 1 << self.typeIDToIndex[gameplayID]

    def getMaskForGameplayIDs(self, gameplayIDs):
        return sum((self.getMaskForGameplayID(gameplayID) for gameplayID in gameplayIDs))

    def __formMapping(self, flagsSection):
        if flagsSection is not None:
            typeIDToIndex = self.typeIDToIndex
            for name, data in flagsSection.items():
                if name == 'type':
                    tag = data.readString('tag')
                    bitIndex = data.readInt('bitIndex', SpaceVisibilityFlags._ERROR_BIT_INDEX)
                    if not tag or bitIndex < 0 or bitIndex >= SpaceVisibilityFlags._SERVER_FLAGS_NUMBER or self.types[tag] in typeIDToIndex:
                        return False
                    typeIDToIndex[self.types[tag]] = bitIndex
                return False

        else:
            self.typeIDToIndex = dict(((i, i) for i in self.types.itervalues() if 0 <= i < SpaceVisibilityFlags._SERVER_FLAGS_NUMBER))
        return False if len(self.typeIDToIndex) == 0 else True

    @staticmethod
    def __isHangarSpace(settingsSection):
        return SpaceVisibilityFlags._HANGAR_CONFIG_SECTION in settingsSection.keys()

    @staticmethod
    def __formSettingPath(geometryName):
        return '{config_directory}/{geometryName}/{file}'.format(config_directory=SpaceVisibilityFlags._CONFIG_DIRECTORY, geometryName=geometryName, file=SpaceVisibilityFlags._CONFIG_FILE)


def _openSection(path):
    section = ResMgr.openSection(path)
    if section is None:
        LOG_WARNING('space.settings file is missing %s' % path)
    return section
