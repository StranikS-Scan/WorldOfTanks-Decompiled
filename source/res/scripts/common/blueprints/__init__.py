# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/blueprints/__init__.py
import typing
from constants import IS_CLIENT
from debug_utils import LOG_CURRENT_EXCEPTION
from soft_exception import SoftException
from wotdecorators import singleton
from dossiers2.custom.cache import getCache as getHelperCache
_CONFIG_FILE = 'scripts/server_xml/blueprints.xml'

class BlueprintsException(SoftException):
    pass


def wipe(blueprints_cfg, pdata, leaveGold):
    pdata['blueprints'] = {}


def makeDefaults():
    return {'isEnabled': False,
     'useBlueprintsForUnlock': False,
     'allowBlueprintsConversion': False,
     'levels': {}}


def readConfig(verbose, **overrides):
    if IS_CLIENT:
        return makeDefaults()
    import XmlConfigReader
    reader = XmlConfigReader.makeReader(_CONFIG_FILE, '', verbose)
    result = _readBlueprints(reader, 'blueprints')
    for k in result:
        if k not in overrides:
            continue
        if k in ('isEnabled', 'useBlueprintsForUnlock', 'allowBlueprintsConversion'):
            result[k] &= overrides[k]
        result[k] = overrides[k]

    return result


def _readBlueprints(reader, subsectionName):
    section = reader.getSubsection(subsectionName)
    if section is None:
        return {}
    else:
        isEnabled = section.readBool('isEnabled', False)
        useBlueprintsForUnlock = section.readBool('useBlueprintsForUnlock', False)
        allowBlueprintsConversion = section.readBool('allowBlueprintsConversion', False)
        levels = {}
        levelsSubsection = reader.getSubsection(subsectionName + '/levels')
        for lname, lsection in levelsSubsection.items():
            _, lvl = str(lname).split('_', 1)
            parts = lsection.readInt('parts', 0)
            progress = lsection.readFloat('progress', 0)
            requires = tuple((int(i) for i in lsection.readString('requires').split())) or (0, 0)
            decays = tuple((float(i) for i in lsection.readString('decays').split())) or (0, 0)
            levels[int(lvl)] = (parts,
             progress,
             requires,
             decays)

        return {'isEnabled': isEnabled,
         'useBlueprintsForUnlock': useBlueprintsForUnlock,
         'allowBlueprintsConversion': allowBlueprintsConversion,
         'levels': levels}


@singleton
class g_cache(object):

    def __init__(self):
        self.__cfg = makeDefaults()

    def __getattr__(self, attr):
        try:
            return self.__cfg[attr]
        except KeyError:
            raise AttributeError

    def init(self, gameParams=None, nofail=True):
        cfg = self.__cfg
        try:
            if gameParams is not None:
                blueprints = gameParams['blueprints_config'].settings
            else:
                blueprints = readConfig(True)
            cfg.update(blueprints)
        except Exception:
            self.fini()
            if nofail:
                raise
            LOG_CURRENT_EXCEPTION()

        return

    def fini(self):
        self.__cfg.clear()

    def __nonzero__(self):
        return bool(self.__cfg)


def init(gameParams=None, nofail=True):
    g_cache.init(gameParams=gameParams, nofail=nofail)


def getAllResearchedVehicles(defaultUnlocks=frozenset()):
    return getHelperCache()['vehiclesInTrees'] - defaultUnlocks


def isNationResearched(nationID, defaultUnlocks=frozenset(), unlocks=frozenset()):
    return not bool(getHelperCache()['vehiclesInTreesByNation'][nationID] - defaultUnlocks - unlocks)
