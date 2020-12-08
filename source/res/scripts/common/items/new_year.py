# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/new_year.py
import typing
from constants import IS_BASEAPP, IS_CLIENT
from debug_utils import LOG_CURRENT_EXCEPTION
from items import collectibles
from wotdecorators import singleton
from soft_exception import SoftException
from itertools import chain
from items.components import ny_constants as CONSTS
from items.readers.ny_readers import readLevelRewards, readSlots, readCollectionRewards, readTalisman, readToysTransformations, buildVariadicDiscountsCache

def _countToysByCollection(toysDescrs, collectingFunction=None):
    counts = {}
    for toy in toysDescrs:
        cid = collectingFunction(toyDescr=toy)
        counts.setdefault(cid, 0)
        counts[cid] += 1

    return list((counts[cid] for cid in sorted(counts.keys(), key=CONSTS.YEARS_INFO.getCollectionIntID)))


def _buildToyGroups(toysDescrs):
    groups = {}
    for toy in toysDescrs:
        groupID = getToyGroupID(toyDescr=toy)
        groups.setdefault(groupID, [])
        groups[groupID].append(toy.id)

    if any((len(gv) < 1 for gk, gv in groups.iteritems())):
        raise SoftException('Inconsistent toys description. Degenerate group size < 1')
    if len(groups) != CONSTS.MAX_TOY_RANK * len(CONSTS.ToySettings.NEW) * len(CONSTS.TOY_USUAL_TYPES) + len(CONSTS.ToySettings.MEGA) * len(CONSTS.MEGA_TOY_TYPES):
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
            ny20Toys = collectibles.g_cache.ny20.toys
            ny21Toys = collectibles.g_cache.ny21.toys
            cfg['toys'] = ny21Toys
            collections = set((getToyCollectionID(toyDescr=toyDescr) for toyDescr in chain(ny21Toys.itervalues(), ny20Toys.itervalues(), ny19Toys.itervalues(), ny18Toys.itervalues())))
            cfg['collections'] = {name:CONSTS.YEARS_INFO.getCollectionIntID(name) for name in collections}
            cfg['collectionStrIDs'] = sorted(cfg['collections'].keys(), key=CONSTS.YEARS_INFO.getCollectionIntID)
            cfg['slots'] = readSlots(CONSTS.COLLECTION2021_SLOTS_XML_PATH)
            cfg['levels'] = readLevelRewards(CONSTS.COLLECTION2021_LEVEL_REWARDS_XML_PATH)
            cfg['collectionRewardsByCollectionID'] = dict(chain(readCollectionRewards(CONSTS.COLLECTION2021_REWARDS_XML_PATH).iteritems(), readCollectionRewards(CONSTS.COLLECTION2020_REWARDS_XML_PATH).iteritems(), readCollectionRewards(CONSTS.COLLECTION2019_REWARDS_XML_PATH).iteritems(), readCollectionRewards(CONSTS.COLLECTION2018_REWARDS_XML_PATH).iteritems()))
            cfg['toyCountByCollectionID'] = _countToysByCollection(chain(ny21Toys.itervalues(), ny20Toys.itervalues(), ny19Toys.itervalues(), ny18Toys.itervalues()), collectingFunction=getToyCollectionID)
            cfg['talismans'] = readTalisman(CONSTS.COLLECTION2021_TALISMANS_XML_PATH)
            cfg['variadicDiscounts'] = buildVariadicDiscountsCache(CONSTS.VARIADIC_DISCOUNTS_XML_PATH)
            if IS_CLIENT:
                cfg['toysTransformations'] = readToysTransformations(CONSTS.TOYS_TRANSFORMATIONS_XML_PATH)
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


def getObjectByToyType(toyType):
    for customizationType, toyTypes in CONSTS.TOY_TYPES_BY_OBJECT.iteritems():
        if toyType in toyTypes:
            return customizationType

    return None


def getToyGroupID(typeID=None, settingID=None, rank=None, toyDescr=None):
    typeID = CONSTS.TOY_TYPE_IDS_BY_NAME[toyDescr.type] if toyDescr is not None else typeID
    settingID = CONSTS.YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[toyDescr.setting] if toyDescr is not None else settingID
    rank = toyDescr.rank if toyDescr else rank
    return typeID << 16 | settingID << 8 | rank


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
    return CONSTS.YEARS_INFO.getCollectionSettingID(toyDescr.setting, toyDescr.collection)


def getToyMask(toyID, year):
    offset = CONSTS.YEARS_INFO.getToyCollectionOffsetForYear(year)
    bytePos = offset + toyID / 8
    mask = 1 << toyID % 8
    return (bytePos, mask)


def getCollectionByStrID(collectionStrID):
    year, settingID = CONSTS.YEARS_INFO.splitCollectionStrID(collectionStrID)
    if settingID < 0:
        return (None, None)
    else:
        collectionName = CONSTS.YEARS_INFO.getCollectionTypesByYear(year)[settingID]
        return (year, collectionName)


def getCollectionByIntID(collectionIntID):
    collectionStrID = g_cache.collectionStrIDs[collectionIntID]
    return getCollectionByStrID(collectionStrID)


def init(nofail=True):
    if not g_cache:
        g_cache.init(nofail)
