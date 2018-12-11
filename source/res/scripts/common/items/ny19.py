# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/ny19.py
import typing
from constants import IS_BASEAPP
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR
from items import collectibles
from items.components.ny_constants import BONUS_THRESHOLDS
from wotdecorators import singleton
from soft_exception import SoftException
from itertools import chain
from items.components import ny_constants as CONSTS
from items.readers.ny_readers import readLevelRewards, readSlots, readVariadicDiscounts, readCollectionRewards

def _countToysByCollection(toysDescrs, collectingFunction=None):
    counts = {}
    for toy in toysDescrs:
        cid = collectingFunction(toyDescr=toy)
        counts.setdefault(cid, 0)
        counts[cid] += 1

    return list((counts[cid] for cid in sorted(counts.keys())))


def _buildToyGroups(toysDescrs):
    groups = {}
    for toy in toysDescrs:
        groupID = getToyGroupID(toyDescr=toy)
        groups.setdefault(groupID, [])
        groups[groupID].append(toy.id)

    if any((len(gv) < 1 for gk, gv in groups.iteritems())):
        raise SoftException('Inconsistent toys description. Degenerate group size < 1')
    if len(groups) != CONSTS.MAX_TOY_RANK * len(CONSTS.ToySettings.NEW) * len(CONSTS.TOY_TYPES):
        missingToys = []
        for typeID in xrange(len(CONSTS.TOY_TYPES)):
            for settingID in xrange(len(CONSTS.ToySettings.NEW)):
                for rank in xrange(1, CONSTS.MAX_TOY_RANK + 1):
                    if getToyGroupID(typeID, settingID, rank) not in groups:
                        missingToys.append((CONSTS.TOY_TYPES[typeID], CONSTS.ToySettings.NEW[settingID], rank))

        raise SoftException('Inconsistent toys description. Missing toys: {} of {}'.format(len(missingToys), missingToys))
    return groups


def dictlike(f):
    return type('', (object,), {'__call__': lambda s, arg: f(arg),
     '__getitem__': lambda s, k: f(*(k if isinstance(k, tuple) else (k,)))})()


@singleton
class g_cache(object):

    def __init__(self):
        self.__cfg = {}

    def __getattr__(self, attr):
        return self.__cfg[attr]

    def init(self, nofail=True):
        cfg = self.__cfg
        try:
            getToyCollectionID = getToySettingID
            ny18Toys = collectibles.g_cache.ny18.toys
            ny19Toys = collectibles.g_cache.ny19.toys
            cfg['toys'] = ny19Toys
            cfg['collections'] = set((getToyCollectionID(toyDescr=toyDescr) for toyDescr in chain(ny19Toys.itervalues(), ny18Toys.itervalues())))
            cfg['slots'] = readSlots(CONSTS.SLOTS_XML_PATH)
            cfg['levels'] = readLevelRewards(CONSTS.LEVEL_REWARDS_XML_PATH)
            cfg['variadicDiscounts'] = readVariadicDiscounts(CONSTS.VARIADIC_DISCOUNTS_XML_PATH)
            cfg['collectionRewardsByCollectionID'] = dict(chain(readCollectionRewards(CONSTS.COLLECTION2019_REWARDS_XML_PATH).iteritems(), readCollectionRewards(CONSTS.COLLECTION2018_REWARDS_XML_PATH).iteritems()))
            cfg['toyCountByCollectionID'] = _countToysByCollection(chain(ny19Toys.itervalues(), ny18Toys.itervalues()), collectingFunction=getToyCollectionID)
            if IS_BASEAPP:
                cfg['collectionIDs'] = dictlike(getToyCollectionID)
                cfg['levelRewardsByID'] = dict(((lr.level, lid) for lid, lr in self.levels.iteritems()))
                cfg['toyGroups'] = _buildToyGroups(self.toys.itervalues())
        except Exception:
            self.ffini()
            if nofail:
                raise
            LOG_CURRENT_EXCEPTION()

    def ffini(self):
        self.__cfg.clear()

    def __nonzero__(self):
        return bool(self.__cfg)


def isRandomValue(value):
    return value is None or value == CONSTS.RANDOM_VALUE


def calculateCraftCost(typeID=None, settingID=None, rank=None):
    if isRandomValue(rank):
        baseCost = CONSTS.Craft.RANDOM_TOY_COST
    else:
        baseCost = CONSTS.Craft.COST_BY_RANK[rank - 1]
    result = baseCost
    if not isRandomValue(settingID):
        result += baseCost * CONSTS.Craft.SETTING_COST_FACTOR
    if not isRandomValue(typeID):
        customization = getObjectByToyType(CONSTS.ToyTypes.ALL[typeID])
        result += baseCost * CONSTS.Craft.CUSTOMIZATION_COST_FACTOR[customization]
    return result


def calculateOldCraftCost(toyID):
    toy = collectibles.g_cache.ny18.toys[toyID]
    return CONSTS.Craft.NY18_COST_BY_RANK[int(toy.rank) - 1]


def getObjectByToyType(toyType):
    for customizationType, toyTypes in CONSTS.TOY_TYPES_BY_OBJECT.iteritems():
        if toyType in toyTypes:
            return customizationType

    return None


def getTotalAtmosphere(toys):
    toysDescrs = g_cache.toys
    return sum((CONSTS.TOY_ATMOSPHERE_BY_RANK[int(toysDescrs[toyID].rank) - 1] for toyID in toys if toyID != -1))


def getCollectionLevel(collectionRating):
    for level, bound in enumerate(CONSTS.COLLECTION_RATING_LIMIT_BY_LEVEL):
        if collectionRating < bound:
            return level

    return CONSTS.MAX_COLLECTION_LEVEL


def calcCollectionBonus(bonusCollectionID, collectionDistributions):
    collectedCount = sum(collectionDistributions[bonusCollectionID])
    return calcCollectionBonusBySum(bonusCollectionID, collectedCount)


def calcCollectionBonusBySum(bonusCollectionID, collectedCount):
    result = 0.0
    for toyCountThreshold, bonusPercent in BONUS_THRESHOLDS[bonusCollectionID]:
        if collectedCount >= toyCountThreshold:
            result = bonusPercent

    return result


def calcBattleBonus(bonusType, collectionDistributions, level):
    return level * calcCollectionBonus(bonusType, collectionDistributions)


def getAtmosphereLevel(totalAtmosphere):
    for level, bound in enumerate(CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL):
        if totalAtmosphere < bound:
            return level

    return CONSTS.MAX_ATMOSPHERE_LEVEL


def getAtmosphereProgress(totalAtmosphere):
    for level, bound in enumerate(CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL):
        if totalAtmosphere < bound:
            prevBound = CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL[level - 1]
            return (totalAtmosphere - prevBound, bound - prevBound)

    finalDelta = CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL[-1] - CONSTS.ATMOSPHERE_LIMIT_BY_LEVEL[-2]
    return (finalDelta, finalDelta)


def getToyGroupID(typeID=None, settingID=None, rank=None, toyDescr=None):
    typeID = CONSTS.TOY_TYPE_IDS_BY_NAME[toyDescr.type] if toyDescr is not None else typeID
    settingID = CONSTS.TOY_SETTING_IDS_BY_NAME[toyDescr.setting] if toyDescr is not None else settingID
    rank = int(toyDescr.rank if toyDescr else rank)
    return typeID << 16 | settingID << 8 | rank


def getToyCost(toyID=None, toyDescr=None):
    if toyDescr is None:
        toyDescr = g_cache.toys[toyID]
    return getattr(toyDescr, 'fragments', 0) or CONSTS.TOY_DECAY_COST_BY_RANK[toyDescr.type, toyDescr.rank]


def getToyObjectID(toyID=None, toyDescr=None):
    if toyDescr is None:
        toyDescr = g_cache.toys[toyID]
    myType = toyDescr.type
    for o, types in CONSTS.TOY_TYPES_BY_OBJECT.iteritems():
        if myType in types:
            return CONSTS.TOY_OBJECTS_IDS_BY_NAME.get(o, -1)

    return -1


def getToySettingID(toyID=None, toyDescr=None):
    if toyDescr is None:
        toyDescr = g_cache.toys[toyID]
    return CONSTS.TOY_SETTING_IDS_BY_NAME.get(toyDescr.setting, -1)


def init(nofail=True):
    if not g_cache:
        g_cache.init(nofail)
