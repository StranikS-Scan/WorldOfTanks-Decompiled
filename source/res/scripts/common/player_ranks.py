# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/player_ranks.py
import typing
from collections import namedtuple
from typing import NamedTuple, Type
from enum import Enum, unique
import ResMgr
from constants import PLAYER_RANK, ARENA_BONUS_TYPE
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
_CONFIG_FILE = 'scripts/item_defs/player_ranks.xml'
if typing.TYPE_CHECKING:
    from ResMgr import DataSection

@unique
class ALGORITHM_NAMES(Enum):
    BASIC_THRESHOLD = 'BasicThreshold'
    NONE = 'None'


@unique
class SETTINGS_NAMES(Enum):
    DEFAULT = 'DEFAULT'
    NONE = 'None'

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


class AlgorithmSettings(object):
    initialRank = property(lambda self: self._initialRank)
    name = property(lambda self: self._name)

    def __init__(self, initialRank, section=None):
        self._initialRank = initialRank
        self._name = ALGORITHM_NAMES(section.name) if section is not None else ALGORITHM_NAMES.NONE
        return


class BasicThresholdSettings(AlgorithmSettings):
    _BasicThresholdRankSettings = namedtuple('_BasicThresholdRankSettings', ('rank', 'order', 'threshold'))

    def _readBasicThresholdRankSettings(self, section, order):
        rank = parseRankFromSectionName(section.name)
        return self._BasicThresholdRankSettings(rank, order, section.readInt('threshold'))

    def __init__(self, initialRank, section):
        super(BasicThresholdSettings, self).__init__(initialRank, section)
        self.ranks = []
        order = 1
        for subsection in section.values():
            self.ranks.append(self._readBasicThresholdRankSettings(subsection, order))
            order += 1

        self.byOrder = {settings.order:settings for settings in self.ranks}
        self.byRank = {settings.rank:settings for settings in self.ranks}
        self.orderByRank = {settings.rank:settings.order for settings in self.ranks}


BonusSettings = NamedTuple('BonusSettings', [('factor100ByRank', dict)])

def makeBonusSettings(section=None):
    factor100ByRank = {}
    if section:
        for rankName in section.keys():
            rank = parseRankFromSectionName(rankName)
            bonusFactor100 = section.readInt(rankName)
            factor100ByRank[rank] = bonusFactor100

    return BonusSettings(factor100ByRank)


PlayerRanksSettings = NamedTuple('PlayerRankSettings', [('initialRank', int), ('algorithm', Type[AlgorithmSettings]), ('bonus', BonusSettings)])

def makePlayerRankSettings(section=None):
    initialRank = section.readInt('initialRank') if section else PLAYER_RANK.NO_RANK
    bonus = makeBonusSettings(section['bonus'] if section else None)
    if section is None:
        algorithm = AlgorithmSettings(initialRank)
    else:
        algorithmKeys = set(section.keys()).intersection((c.value for c in ALGORITHM_NAMES))
        algorithmName = algorithmKeys.pop()
        algorithm = ALGORITHM_NAME_TO_SETTINGS[ALGORITHM_NAMES(algorithmName)](initialRank, section[algorithmName])
    return PlayerRanksSettings(initialRank, algorithm, bonus)


ALGORITHM_NAME_TO_SETTINGS = {ALGORITHM_NAMES.BASIC_THRESHOLD: BasicThresholdSettings}
ARENA_BONUS_TYPE_TO_SETTINGS_NAME = {ARENA_BONUS_TYPE.EPIC_BATTLE: SETTINGS_NAMES.DEFAULT,
 ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING: SETTINGS_NAMES.DEFAULT,
 ARENA_BONUS_TYPE.EPIC_RANDOM_TRAINING: SETTINGS_NAMES.DEFAULT}
g_cache = None

def init():
    global g_cache
    g_cache = settings = {}
    section = ResMgr.openSection(_CONFIG_FILE)
    for name, subsection in section.items():
        settings[SETTINGS_NAMES(name)] = makePlayerRankSettings(subsection)

    for arenaBonusType, caps in ARENA_BONUS_TYPE_CAPS._typeToCaps.iteritems():
        if ARENA_BONUS_TYPE_CAPS.PLAYER_RANK_MECHANICS in caps:
            pass

    if SETTINGS_NAMES.NONE not in settings:
        settings[SETTINGS_NAMES.NONE] = makePlayerRankSettings()


def parseRankFromSectionName(name, checkInPlayerRanks=True):
    rank = int(name[1:])
    if checkInPlayerRanks:
        pass
    return rank


def getSettingsForBonusType(bonusType=None):
    return getSettings(ARENA_BONUS_TYPE_TO_SETTINGS_NAME.get(bonusType, SETTINGS_NAMES.NONE))


def getSettings(settingsName=SETTINGS_NAMES.DEFAULT):
    return g_cache.get(settingsName, g_cache[SETTINGS_NAMES.NONE])


def getTresholdForRanks():
    xpTresholdForRanks = []
    defaultAlgorithmSettings = getSettings().algorithm
    for rank in range(PLAYER_RANK.DEFAULT_RANK, PLAYER_RANK.MAX_RANK + 1):
        if rank == PLAYER_RANK.NO_RANK:
            xpTresholdForRanks.append(0)
            continue
        rankSettings = defaultAlgorithmSettings.byRank.get(rank, None)
        if rankSettings is not None:
            xpTresholdForRanks.append(rankSettings.threshold)

    return xpTresholdForRanks


def getRank(progressValue):
    result = -1
    for rankThreshold in getTresholdForRanks():
        if progressValue >= rankThreshold:
            result = result + 1
        break

    return result
