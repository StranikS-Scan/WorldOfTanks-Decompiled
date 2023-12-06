# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/new_year.py
from typing import List, Optional, Dict, Callable, Iterable, TYPE_CHECKING
from constants import IS_BASEAPP, IS_CLIENT
from debug_utils import LOG_CURRENT_EXCEPTION
from items import collectibles
from items.components.ny_constants import YEARS_INFO, YEARS, MAX_MEGA_TOY_RANK, MIN_ATMOSPHERE_LVL, MAX_ATMOSPHERE_LVL, LEVEL_REWARD_ID_TEMPLATE, COLLECTION_REWARD_ID_TEMPLATE, ToySettings, TOY_USUAL_TYPES, MEGA_TOY_TYPES, COLLECTION_SLOTS_XML_PATH, VARIADIC_DISCOUNTS_XML_PATH, TOYS_TRANSFORMATIONS_XML_PATH, TOY_TYPE_IDS_BY_NAME, TOY_TYPES_BY_OBJECT, TOY_OBJECTS_IDS_BY_NAME, MAX_DOG_TOY_RANK, DOG_TOY_TYPES
from wotdecorators import singleton
from ny_common.ny_exception import NYSoftException
from itertools import chain
from items.readers.ny_readers import readSlots, readToysTransformations, buildVariadicDiscountsCache
if TYPE_CHECKING:
    from items.collectibles import ToyDescriptor

def _countToysByCollection(toysDescrs, collectingFunction=None):
    counts = {}
    for toy in toysDescrs:
        cid = collectingFunction(toyDescr=toy)
        counts.setdefault(cid, 0)
        counts[cid] += 1

    return [ counts[cid] for cid in sorted(counts.iterkeys(), key=YEARS_INFO.getCollectionIntID) ]


def _buildToyGroups(toysDescrs):
    groups = {}
    for toy in toysDescrs:
        groupID = getToyGroupID(toyDescr=toy)
        groups.setdefault(groupID, [])
        groups[groupID].append(toy.id)

    if any((len(gv) < 1 for gk, gv in groups.iteritems())):
        raise NYSoftException('Inconsistent toys description. Degenerate group size < 1')
    currYearMaxToyRank = YEARS_INFO.currYearMaxToyRank()
    toysInfos = [(currYearMaxToyRank, ToySettings.NEW, TOY_USUAL_TYPES), (MAX_MEGA_TOY_RANK, ToySettings.MEGA, MEGA_TOY_TYPES), (MAX_DOG_TOY_RANK, ToySettings.DOG, DOG_TOY_TYPES)]
    expectedGroupsCount = _calculateExpectedCount(toysInfos)
    if len(groups) == expectedGroupsCount:
        return groups
    missingToys = _findMissingToys(toysInfos, groups)
    raise NYSoftException('Inconsistent toys description. Missing toys (groups len={}, expectedGroupsLen={} toyRank={}): {} of {}'.format(len(groups), expectedGroupsCount, currYearMaxToyRank, len(missingToys), missingToys))


def _calculateExpectedCount(toysInfos):
    expectedCount = 0
    for toysInfo in toysInfos:
        maxRank, toySettingsList, toyTypesList = toysInfo
        expectedCount += maxRank * len(toySettingsList) * len(toyTypesList)

    return expectedCount


def _findMissingToys(toysInfos, obtainedGroups):

    def _find(maxRank, toySettingsList, toyTypesList):
        missing = []
        for typeID, typeName in enumerate(toyTypesList):
            for settingID, settingName in enumerate(toySettingsList):
                for rank in xrange(1, maxRank + 1):
                    if getToyGroupID(typeID, settingID, rank) not in obtainedGroups:
                        missing.append((typeName, settingName, rank))

        return missing

    missingToys = []
    for toysInfo in toysInfos:
        missingToys.extend(_find(*toysInfo))

    return missingToys


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
            cfg['toys'] = collectibles.g_cache[YEARS_INFO.CURRENT_YEAR_STR].toys
            collections = set((getToyCollectionID(toyDescr=toyDescr) for toyDescr in chain(*[ collectibles.g_cache[YEARS.getYearStrFromYearNum(year)].toys.itervalues() for year in YEARS_INFO.allYearsDecreasingIter() ])))
            cfg['collections'] = {name:YEARS_INFO.getCollectionIntID(name) for name in collections}
            cfg['collectionStrIDs'] = sorted(cfg['collections'].iterkeys(), key=YEARS_INFO.getCollectionIntID)
            cfg['slots'] = readSlots(COLLECTION_SLOTS_XML_PATH)
            cfg['levelRewardsByID'] = {level:LEVEL_REWARD_ID_TEMPLATE.format(YEARS_INFO.CURRENT_YEAR_STR, level) for level in xrange(MIN_ATMOSPHERE_LVL, MAX_ATMOSPHERE_LVL + 1)}
            cfg['collectionRewardsByCollectionID'] = collectionRewardsByCollectionID = {}
            for year in YEARS.ALL:
                yearStr = YEARS.getYearStrFromYearNum(year)
                for setting in YEARS_INFO.getCollectionSettingIDsByYear(year).iterkeys():
                    collectionRewardsByCollectionID[YEARS_INFO.getCollectionSettingID(setting, yearStr)] = COLLECTION_REWARD_ID_TEMPLATE.format(yearStr, setting.lower() if setting[0].isupper() else setting)

            cfg['collectionIDByCollectionRewards'] = {rewardID:collectionID for collectionID, rewardID in collectionRewardsByCollectionID.iteritems()}
            cfg['toyCountByCollectionID'] = _countToysByCollection(chain(*[ collectibles.g_cache[YEARS.getYearStrFromYearNum(year)].toys.itervalues() for year in YEARS_INFO.allYearsDecreasingIter() ]), collectingFunction=getToyCollectionID)
            cfg['variadicDiscounts'] = buildVariadicDiscountsCache(VARIADIC_DISCOUNTS_XML_PATH)
            if IS_CLIENT:
                cfg['toysTransformations'] = readToysTransformations(TOYS_TRANSFORMATIONS_XML_PATH)
            if IS_BASEAPP:
                cfg['collectionIDs'] = dictlike(getToyCollectionID)
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


def getObjectByToyType(toyType):
    for customizationType, toyTypes in TOY_TYPES_BY_OBJECT.iteritems():
        if toyType in toyTypes:
            return customizationType

    return None


def getToyGroupID(typeID=None, settingID=None, rank=None, toyDescr=None):
    typeID = TOY_TYPE_IDS_BY_NAME[toyDescr.type] if toyDescr is not None else typeID
    settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyDescr.setting] if toyDescr is not None else settingID
    rank = toyDescr.rank if toyDescr else rank
    return typeID << 16 | settingID << 8 | rank


def getToyObjectID(toyID=None, toyDescr=None):
    if toyDescr is None:
        toyDescr = g_cache.toys[toyID]
    myType = toyDescr.type
    for o, types in TOY_TYPES_BY_OBJECT.iteritems():
        if myType in types:
            return TOY_OBJECTS_IDS_BY_NAME.get(o, -1)

    return -1


def getToySettingID(toyID=None, toyDescr=None):
    if toyDescr is None:
        toyDescr = g_cache.toys[toyID]
    return YEARS_INFO.getCollectionSettingID(toyDescr.setting, toyDescr.collection)


def getToyMask(toyID, year):
    offset = YEARS_INFO.getToyCollectionOffsetForYear(year)
    bytePos = offset + toyID / 8
    mask = 1 << toyID % 8
    return (bytePos, mask)


def getCollectionByStrID(collectionStrID):
    year, settingID = YEARS_INFO.splitCollectionStrID(collectionStrID)
    if settingID < 0:
        return (None, None)
    else:
        collectionName = YEARS_INFO.getCollectionTypesByYear(year)[settingID]
        return (year, collectionName)


def getCollectionByIntID(collectionIntID):
    collectionStrID = g_cache.collectionStrIDs[collectionIntID]
    return getCollectionByStrID(collectionStrID)


def init(nofail=True):
    if not g_cache:
        g_cache.init(nofail)
