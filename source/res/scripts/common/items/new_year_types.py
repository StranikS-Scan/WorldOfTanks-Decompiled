# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/new_year_types.py
import ResMgr
import nations
import random
from constants import IS_CLIENT, IS_BASEAPP
from itertools import chain, product
from collections import namedtuple
from debug_utils import *
TOYS_XML_PATH = 'scripts/item_defs/new_year/toys.xml'
SLOTS_XML_PATH = 'scripts/item_defs/new_year/slots.xml'
CHESTS_XML_PATH = 'scripts/item_defs/new_year/chests.xml'
BOXES_XML_PATH = 'scripts/item_defs/new_year/boxes.xml'
VARIADIC_DISCOUNTS_XML_PATH = 'scripts/item_defs/new_year/variadic_discounts.xml'
VARIADIC_TANKMEN_XML_PATH = 'scripts/item_defs/new_year/variadic_tankmen.xml'
COLLECTION_REWARDS_XML_PATH = 'scripts/item_defs/new_year/collection_rewards.xml'
NATIONAL_SETTINGS = ('soviet', 'traditionalWestern', 'modernWestern', 'asian')
NATIONAL_SETTINGS_IDS_BY_NAME = dict(((name, index) for index, name in enumerate(NATIONAL_SETTINGS)))
NATIONS_BY_SETTING = {'soviet': ('ussr',),
 'traditionalWestern': ('germany', 'czech', 'france', 'poland'),
 'modernWestern': ('usa', 'uk', 'sweden', 'japan'),
 'asian': ('china',)}
SETTING_BY_NATION = dict(chain.from_iterable((product(ns, (s,)) for s, ns in NATIONS_BY_SETTING.iteritems())))
SETTING_BY_NATION_ID = dict(((nations.INDICES[n], s) for n, s in SETTING_BY_NATION.iteritems()))
SETTING_ID_BY_NATION_ID = dict(((nid, NATIONAL_SETTINGS_IDS_BY_NAME[n]) for nid, n in SETTING_BY_NATION_ID.iteritems()))
TOY_TYPES = ('top', 'hanging', 'garland', 'gift', 'snowman', 'house_decoration', 'house_lamp', 'street_garland')
TOY_TYPES_IDS_BY_NAME = dict(((name, index) for index, name in enumerate(TOY_TYPES)))
MAX_TOY_RANK = 5
INVALID_TOY_ID = -1
MAX_CHEST_LEVEL = 10

class CRAFT:
    FRAGMENTS_BY_RANK = (10, 20, 30, 70, 250)
    COST_BY_RANK = (20, 40, 60, 140, 480)
    RANDOM_TOY_COST = 100
    NATIONAL_SETTING_COST_FACTOR = 1.0
    TYPE_COST_FACTOR = 1.0
    PROBABILITY_FOR_RANK = ((1, 0.5344),
     (2, 0.27),
     (3, 0.12),
     (4, 0.065),
     (5, 0.0106))
    PROBABILITY_FOR_SETTING = (('soviet', 0.25),
     ('traditionalWestern', 0.25),
     ('modernWestern', 0.25),
     ('asian', 0.25))
    PROBABILITY_FOR_SETTING_ID = tuple(((NATIONAL_SETTINGS_IDS_BY_NAME[nm], p) for nm, p in PROBABILITY_FOR_SETTING))
    PROBABILITY_FOR_TYPE = (('top', 0.08),
     ('hanging', 0.3),
     ('garland', 0.11),
     ('gift', 0.11),
     ('snowman', 0.1),
     ('house_decoration', 0.1),
     ('house_lamp', 0.1),
     ('street_garland', 0.1))
    PROBABILITY_FOR_TYPE_ID = tuple(((TOY_TYPES_IDS_BY_NAME[nm], p) for nm, p in PROBABILITY_FOR_TYPE))


class NY_STATE:
    NOT_STARTED = 0
    IN_PROGRESS = 1
    SUSPENDED = 2
    FINISHED = 3
    ENABLED = (IN_PROGRESS, SUSPENDED)
    ALL = (NOT_STARTED,
     IN_PROGRESS,
     SUSPENDED,
     FINISHED)


TOY_COLLECTION_BYTES = 40
_MAX_TOY_ID = TOY_COLLECTION_BYTES * 8 - 1
TOY_ATMOSPHERE_BY_RANK = (1, 2, 4, 7, 25)
BOUND_ATMOSPHERE_BY_LEVEL = (0, 8, 22, 41, 64, 91, 137, 186, 249, 325)
_BONUS_FACTOR_BY_ATMOSPHERE_LEVEL = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 12.0)
_MAX_ATMOSPHERE_LEVEL = 10
TOY_RATING_BY_RANK = (1, 1, 1, 1, 1)
BOUND_COLLECTION_RATING_BY_LEVEL = (0, 8, 19, 37, 55)
CollectionBonus = namedtuple('CollectionBonus', ('xp', 'tmenXp', 'freeXp', 'credits'))
COLLECTION_BONUSES_BY_LEVEL = (CollectionBonus(0.0, 0.0, 0.0, 0.0),
 CollectionBonus(0.01, 0.01, 0.0, 0.01),
 CollectionBonus(0.02, 0.02, 0.0, 0.02),
 CollectionBonus(0.03, 0.03, 0.0, 0.03),
 CollectionBonus(0.04, 0.04, 0.0, 0.04))
_MAX_COLLECTION_LEVEL = 5
assert len(BOUND_ATMOSPHERE_BY_LEVEL) == _MAX_ATMOSPHERE_LEVEL
assert len(_BONUS_FACTOR_BY_ATMOSPHERE_LEVEL) == _MAX_ATMOSPHERE_LEVEL
assert len(BOUND_COLLECTION_RATING_BY_LEVEL) == _MAX_COLLECTION_LEVEL
assert len(COLLECTION_BONUSES_BY_LEVEL) == _MAX_COLLECTION_LEVEL
for params in (TOY_ATMOSPHERE_BY_RANK,
 TOY_RATING_BY_RANK,
 CRAFT.FRAGMENTS_BY_RANK,
 CRAFT.COST_BY_RANK):
    assert len(params) == MAX_TOY_RANK

for setting, ns in NATIONS_BY_SETTING.iteritems():
    assert setting in NATIONAL_SETTINGS
    for nation in ns:
        assert nation in nations.NAMES

for choises in (CRAFT.PROBABILITY_FOR_RANK, CRAFT.PROBABILITY_FOR_SETTING_ID, CRAFT.PROBABILITY_FOR_TYPE_ID):
    assert abs(sum((p for _, p in choises)) - 1.0) < 1e-08

g_cache = None

class SlotDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


class ToyDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg
        rank = cfg['rank']
        self.atmosphere = TOY_ATMOSPHERE_BY_RANK[rank - 1]
        self.rating = TOY_RATING_BY_RANK[rank - 1]
        self.fragments = CRAFT.FRAGMENTS_BY_RANK[rank - 1]
        self.settingID = NATIONAL_SETTINGS_IDS_BY_NAME[cfg['setting']]

    def __getattr__(self, name):
        return self.__cfg[name]


class ChestDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


class BoxDescriptor(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


class VariadicTankman(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


class VariadicDiscount(object):

    def __init__(self, cfg):
        self.__cfg = cfg

    def __getattr__(self, name):
        return self.__cfg[name]


class NewYearCache(object):

    def __init__(self):
        self.toys = _buildToysCache()
        self.slots = _buildSlotsCache()
        self.chests = _buildChestsCache()
        self.boxes = _buildBoxesCache()
        self.variadicDiscounts = _buildVariadicDiscountsCache()
        self.variadicTankmen = _buildVariadicTankmenCache()
        self.collectionRewardsBySettingID = _buildCollectionRewardsCache()
        if IS_BASEAPP:
            self.toyGroups = _buildToyGroups(self.toys.itervalues())
            self.toyCountBySettingID = _countToysBySetting(self.toys.itervalues())
            self.chestIDByLevel = dict(((c.level, cid) for cid, c in self.chests.iteritems()))


def getTotalAtmosphere(toys):
    global g_cache
    toysDescrs = g_cache.toys
    atmosphere = 0
    for toyID in toys:
        if toyID != -1:
            atmosphere += toysDescrs[toyID].atmosphere

    return atmosphere


def getCollectionLevel(collectionRating):
    for level, bound in enumerate(BOUND_COLLECTION_RATING_BY_LEVEL):
        if collectionRating < bound:
            return level

    return _MAX_COLLECTION_LEVEL


def getAtmosphereLevel(totalAtmosphere):
    for level, bound in enumerate(BOUND_ATMOSPHERE_BY_LEVEL):
        if totalAtmosphere < bound:
            return level

    return _MAX_ATMOSPHERE_LEVEL


def getAtmosphereProgress(totalAtmosphere):
    for level, bound in enumerate(BOUND_ATMOSPHERE_BY_LEVEL):
        if totalAtmosphere < bound:
            prevBound = BOUND_ATMOSPHERE_BY_LEVEL[level - 1]
            return (totalAtmosphere - prevBound, bound - prevBound)

    finalDelta = BOUND_ATMOSPHERE_BY_LEVEL[-1] - BOUND_ATMOSPHERE_BY_LEVEL[-2]
    return (finalDelta, finalDelta)


def getBonuses(atmosphereLevel, collectionLevel):
    cb = COLLECTION_BONUSES_BY_LEVEL[collectionLevel - 1]
    factor = _BONUS_FACTOR_BY_ATMOSPHERE_LEVEL[atmosphereLevel - 1]
    return (cb.xp * factor,
     cb.tmenXp * factor,
     cb.freeXp * factor,
     cb.credits * factor)


def calculateCraftCost(isTypeSpecified, isSettingSpecified, rank):
    if rank is None or rank == -1:
        baseCost = CRAFT.RANDOM_TOY_COST
    elif 1 <= rank <= MAX_TOY_RANK:
        baseCost = CRAFT.COST_BY_RANK[rank - 1]
    else:
        return
    cost = baseCost
    if isTypeSpecified:
        cost += baseCost * CRAFT.TYPE_COST_FACTOR
    if isSettingSpecified:
        cost += baseCost * CRAFT.NATIONAL_SETTING_COST_FACTOR
    return int(cost)


def makeRandomChoice(choises):
    r = random.random()
    probability = 0.0
    for value, p in choises:
        probability += p
        if r <= probability:
            return value

    return choises[0][0]


def getToyGroupID(typeID, settingID, rank):
    return typeID << 16 | settingID << 8 | rank


def choiseToyUsingCraftRules(typeID, settingID, rank):
    if typeID == -1:
        typeID = makeRandomChoice(CRAFT.PROBABILITY_FOR_TYPE_ID)
    if settingID == -1:
        settingID = makeRandomChoice(CRAFT.PROBABILITY_FOR_SETTING_ID)
    if rank == -1:
        rank = makeRandomChoice(CRAFT.PROBABILITY_FOR_RANK)
    groupID = getToyGroupID(typeID, settingID, rank)
    groupOfChoice = g_cache.toyGroups.get(groupID, None)
    if not groupOfChoice:
        LOG_WARNING('choiseToyUsingCraftRules: missing toy group: type %d, setting %d, rank %d' % (typeID, settingID, rank))
        return
    else:
        return random.choice(groupOfChoice)


def _readSlot(section):
    cfg = {}
    cfg['id'] = section.readInt('id')
    cfg['type'] = slotType = section.readString('type')
    if slotType not in TOY_TYPES:
        raise Exception("Wrong slot type '%s'" % slotType)
    if IS_CLIENT:
        cfg['object'] = section.readString('object')
        cfg['nodes'] = section.readString('nodes')
        cfg['direction'] = section.readString('direction')
    return cfg


def _buildSlotsCache():
    section = ResMgr.openSection(SLOTS_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % SLOTS_XML_PATH)
    subsections = section.values()
    numSlots = len(subsections)
    cache = [None] * numSlots
    for slotSec in subsections:
        cfg = _readSlot(slotSec)
        slotID = cfg['id']
        if not 0 <= slotID < numSlots:
            raise Exception("Wrong slotID '%d'" % slotID)
        if cache[slotID] is not None:
            raise Exception("Repeated slotID '%d'" % slotID)
        cache[slotID] = SlotDescriptor(cfg)

    return cache


def _readToy(section):
    cfg = {}
    cfg['id'] = toyID = section.readInt('id')
    if not 0 <= toyID <= _MAX_TOY_ID:
        raise Exception("Wrong toy id '%d'" % toyID)
    cfg['type'] = slotType = section.readString('type')
    if slotType not in TOY_TYPES:
        raise Exception("Wrong toy type '%s'" % slotType)
    cfg['rank'] = rank = section.readInt('rank')
    if not 1 <= rank <= MAX_TOY_RANK:
        raise Exception("Wrong toy rank '%d'" % rank)
    cfg['setting'] = setting = section.readString('setting')
    if setting not in NATIONAL_SETTINGS:
        raise Exception("Wrong toy national setting '%s'" % setting)
    if IS_CLIENT:
        cfg['icon'] = section.readString('icon')
        cfg['slotIcon'] = section.readString('slotIcon')
        cfg['model'] = section.readString('model')
        cfg['name'] = section.readString('name')
        cfg['regularEffect'] = section.readString('regularEffect')
        cfg['hangingEffect'] = section.readString('hangingEffect')
    return cfg


def _buildToysCache():
    section = ResMgr.openSection(TOYS_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % TOYS_XML_PATH)
    cache = {}
    for toySec in section.values():
        cfg = _readToy(toySec)
        toyID = cfg['id']
        if cache.has_key(toyID):
            raise Exception("Repeated toyID '%d'" % toyID)
        cache[toyID] = ToyDescriptor(cfg)

    return cache


def _countToysBySetting(toysDescrs):
    counts = [0] * len(NATIONAL_SETTINGS)
    for toy in toysDescrs:
        counts[toy.settingID] += 1

    return counts


def _buildToyGroups(toysDescrs):
    groups = {}
    for toy in toysDescrs:
        typeID = TOY_TYPES_IDS_BY_NAME[toy.type]
        groupID = getToyGroupID(typeID, toy.settingID, toy.rank)
        groups.setdefault(groupID, []).append(toy.id)

    if len(groups) != MAX_TOY_RANK * len(NATIONAL_SETTINGS) * len(TOY_TYPES):
        missingToys = []
        for typeID in xrange(len(TOY_TYPES)):
            for settingID in xrange(len(NATIONAL_SETTINGS)):
                for rank in xrange(1, MAX_TOY_RANK + 1):
                    if getToyGroupID(typeID, settingID, rank) not in groups:
                        missingToys.append((TOY_TYPES[typeID], NATIONAL_SETTINGS[settingID], rank))

        raise Exception('Inconsistent toys description. Missing toys: ' + str(missingToys))
    return groups


def _readChest(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    cfg['level'] = level = section.readInt('level')
    if not 1 <= level <= MAX_CHEST_LEVEL:
        raise Exception("Wrong chest level '%d'" % level)
    return cfg


def _buildChestsCache():
    section = ResMgr.openSection(CHESTS_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % CHESTS_XML_PATH)
    cache = {}
    for chestSec in section.values():
        cfg = _readChest(chestSec)
        chestID = cfg['id']
        if cache.has_key(chestID):
            raise Exception("Repeated chestID '%s'" % chestID)
        cache[chestID] = ChestDescriptor(cfg)

    return cache


def _readBox(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    setting = section.readString('setting', '')
    if setting == '':
        cfg['setting'] = None
    else:
        if setting not in NATIONAL_SETTINGS:
            raise Exception("Wrong box setting '%s'" % setting)
        cfg['setting'] = setting
    cfg['present'] = section.readBool('present', False)
    return cfg


def _buildBoxesCache():
    section = ResMgr.openSection(BOXES_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % BOXES_XML_PATH)
    cache = {}
    for boxSec in section.values():
        cfg = _readBox(boxSec)
        boxID = cfg['id']
        if cache.has_key(boxID):
            raise Exception("Repeated boxID '%s'" % boxID)
        cache[boxID] = BoxDescriptor(cfg)

    return cache


def _readVariadicTankman(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    cfg['level'] = level = section.readInt('level')
    if not 1 <= level <= _MAX_ATMOSPHERE_LEVEL:
        raise Exception("Wrong variadic tankman level '%d'" % level)
    return cfg


def _buildVariadicTankmenCache():
    section = ResMgr.openSection(VARIADIC_TANKMEN_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % VARIADIC_TANKMEN_XML_PATH)
    cache = {}
    for vdSec in section.values():
        cfg = _readVariadicTankman(vdSec)
        vtID = cfg['id']
        if cache.has_key(vtID):
            raise Exception("Repeated variadic tankman ID '%s'" % vtID)
        cache[vtID] = VariadicTankman(cfg)

    return cache


def _readVariadicDiscount(section):
    cfg = {}
    cfg['id'] = section.readString('id')
    strRange = section.readString('goodiesRange')
    cfg['goodiesRange'] = intRange = map(int, strRange.strip(' ').split(' '))
    if len(intRange) != 2:
        raise Exception('Wrong goodies range %s' % strRange)
    return cfg


def _buildVariadicDiscountsCache():
    section = ResMgr.openSection(VARIADIC_DISCOUNTS_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % VARIADIC_DISCOUNTS_XML_PATH)
    cache = {}
    for vdSec in section.values():
        cfg = _readVariadicDiscount(vdSec)
        vdID = cfg['id']
        if cache.has_key(vdID):
            raise Exception("Repeated variadic discount ID '%s'" % vdID)
        cache[vdID] = VariadicDiscount(cfg)

    return cache


def _buildCollectionRewardsCache():
    section = ResMgr.openSection(COLLECTION_REWARDS_XML_PATH)
    if section is None:
        raise Exception("Can't open '%s'" % COLLECTION_REWARDS_XML_PATH)
    cache = [None] * len(NATIONAL_SETTINGS)
    for crSec in section.values():
        rewardID = crSec.readString('id')
        setting = crSec.readString('setting')
        if setting not in NATIONAL_SETTINGS:
            raise Exception("Wrong collection reward setting '%s'" % setting)
        settingID = NATIONAL_SETTINGS_IDS_BY_NAME[setting]
        if settingID in cache:
            raise Exception("Repeated setting '%s'" % setting)
        cache[settingID] = rewardID

    if None in cache:
        raise Exception("Missing collection reward setting in '%s'" % COLLECTION_REWARDS_XML_PATH)
    return cache


def init():
    global g_cache
    g_cache = NewYearCache()


def wipe(nycache, pdata, leaveGold):
    newYearData = pdata['newYear']
    newYearData['slots'] = [-1] * len(nycache.slots)
    newYearData['inventoryToys'] = {}
    newYearData['level'] = 0
    newYearData['toyFragments'] = 0
    newYearData['toyCollection'] = bytearray(TOY_COLLECTION_BYTES)
    newYearData['collectionDistributions'] = [ [0] * MAX_TOY_RANK for _ in NATIONAL_SETTINGS ]
    newYearData['selectedTankmen'] = {}
