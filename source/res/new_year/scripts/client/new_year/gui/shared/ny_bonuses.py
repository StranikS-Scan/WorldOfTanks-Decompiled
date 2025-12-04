# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/shared/ny_bonuses.py
import logging
import typing
from gui.impl import backport
from helpers import dependency
from NewYearBonusesClient import ToyBonus
from new_year.helpers.server_settings import getNewYearBonusConfig
from new_year_common.items import new_year
from new_year_common.items.components.ny_constants import MAX_ATMOSPHERE_LVL, YEARS_INFO, CurrentNYConstants, MIN_TOY_RANK, MAX_TOY_RANK
from new_year.ny_constants import FormulaInfo, PERCENT
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.shared.ny_toy_info import NewYearCurrentToyInfo
from new_year_common.setting_bonus import SettingBonus
from shared_utils import inPercents
from skeletons.gui.shared import IItemsCache
from new_year.skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from typing import List, Tuple
CREDITS_BONUS = 'creditsFactor'
XP_BONUS = 'xpFactor'
FREE_XP_BONUS = 'freeXPFactor'
TANKMEN_XP_BONUS = 'tankmenXPFactor'
BONUSES_GUI_CONFIG_PATH = 'new_year/gui/ny_bonuses_gui_config.xml'
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getToyRewardPresentPriority(toy, itemsCache=None):
    if toy.getName() == CurrentNYConstants.TOYS:
        toyID = toy.getToyBonusValues()[CurrentNYConstants.TOYS][0].keys()[0]
        toys = itemsCache.items.festivity.getToys()
        toyInfo = toys.get(toyID)
        if not toyInfo:
            return toyID
        userName = toyInfo.getName()
        return backport.text(userName)
    _, _, rank = toy.getToyBonusValues()[CurrentNYConstants.ANY_OF][0]
    return -rank


class BonusesSortTags(object):
    TOYS = CurrentNYConstants.TOYS
    MANDARINS = CurrentNYConstants.MANDARINS
    MANDARINS_COMPENSATION = CurrentNYConstants.MANDARINS + 'Compensation'
    RANGE = (TOYS, MANDARINS, MANDARINS_COMPENSATION)


BONUS_TAG_HANDLER_MAP = {CurrentNYConstants.TOYS: lambda b: BonusesSortTags.TOYS,
 CurrentNYConstants.ANY_OF: lambda b: BonusesSortTags.TOYS,
 CurrentNYConstants.MANDARINS: lambda b: BonusesSortTags.MANDARINS_COMPENSATION if b.isCompensation() else BonusesSortTags.MANDARINS}
BONUSES_KEY_FUNC = {CurrentNYConstants.TOYS: _getToyRewardPresentPriority,
 CurrentNYConstants.ANY_OF: _getToyRewardPresentPriority}

def isMandarinCompensation(bonus):
    return bonus.getName() == CurrentNYConstants.MANDARINS and bonus.isCompensation()


def aggregateToys(bonuses):
    result = []
    masterToy = None
    for b in bonuses:
        if b.getName() in (CurrentNYConstants.TOYS, CurrentNYConstants.ANY_OF) or isMandarinCompensation(b):
            if not masterToy:
                if isMandarinCompensation(b):
                    masterToy = ToyBonus.createEmptyToy()
                    masterToy.aggregateToy(b)
                else:
                    masterToy = b
            else:
                masterToy.aggregateToy(b)
        result.append(b)

    if masterToy is not None:
        result = [masterToy] + result
    return result


def leaveOneToyPerRank(bonuses):
    result = []
    toyRanks = set()
    for b in bonuses:
        if b.getName() not in (CurrentNYConstants.TOYS, CurrentNYConstants.ANY_OF):
            result.append(b)
            continue
        if b.getName() == CurrentNYConstants.ANY_OF:
            type, setting, rank = b.getValue()[0]
            if rank == -1:
                for r in xrange(MAX_TOY_RANK, MIN_TOY_RANK - 1, -1):
                    if r not in toyRanks:
                        anyOfToy = ToyBonus(b.getName(), [(type, setting, r)])
                        result.append(anyOfToy)
                        toyRanks.add(r)

                continue
        else:
            rank = NewYearCurrentToyInfo(b.getValue().keys()[0]).getRank()
        if rank not in toyRanks:
            result.append(b)
            toyRanks.add(rank)

    return result


class BonusHelper(object):
    _itemsCache = dependency.descriptor(IItemsCache)
    _nyController = dependency.descriptor(INewYearController)
    _ALL_BONUS_TYPES = (CREDITS_BONUS,
     XP_BONUS,
     FREE_XP_BONUS,
     TANKMEN_XP_BONUS)

    @classmethod
    def _getCommon(cls, method, *args):
        results = [ method(bonusType=bonusType, *args) for bonusType in cls._ALL_BONUS_TYPES ]
        if any((result != results[0] for result in results)):
            _logger.warning('DIFFERENT CONFIG FOR DIFFERENT BONUS TYPES')
        return results[0]

    @classmethod
    def getBonus(cls, bonusType):
        return SettingBonus.calculateBonusForType(bonusType=bonusType, atmosphereLevel=cls.getAtmosphereLevel(), collectionLevels=cls.getCollectionLevels(), toysLevel=cls.getUniqueToysLevel(), config=getNewYearBonusConfig())

    @classmethod
    def getCommonBonus(cls):
        return cls._getCommon(cls.getBonus)

    @classmethod
    def getBonusInPercents(cls, bonusType):
        return inPercents(cls.getBonus(bonusType))

    @classmethod
    def getCommonBonusInPercents(cls):
        return int(cls.getCommonBonus() * PERCENT)

    @classmethod
    def getMaxBonus(cls, bonusType):
        config = getNewYearBonusConfig()
        maxToysLevel = config.getMaxUniqueToysLevel()
        maxCollectionLevels = config.getMaxCollectionLevels()
        return SettingBonus.calculateBonusForType(bonusType=bonusType, atmosphereLevel=MAX_ATMOSPHERE_LVL, collectionLevels=maxCollectionLevels, toysLevel=maxToysLevel, config=config)

    @classmethod
    def getCommonMaxBonus(cls):
        return cls._getCommon(cls.getMaxBonus)

    @classmethod
    def getAtmosphereLevel(cls):
        return NewYearAtmospherePresenter.getLevel()

    @classmethod
    def getAtmosphereMultiplier(cls):
        return SettingBonus.getAtmosphereMultiplier(cls.getAtmosphereLevel(), getNewYearBonusConfig())

    @classmethod
    def getCollectionsFactor(cls, bonusType):
        result = 0
        for name in YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR, useMega=False, usePet=False):
            result += cls.getCollectionFactor(name, bonusType)

        return result

    @classmethod
    def getCommonCollectionsFactor(cls):
        return cls._getCommon(cls.getCollectionsFactor)

    @classmethod
    def getCollectionFactor(cls, collectionName, bonusType):
        level = cls.getCollectionLevelByName(collectionName)
        return SettingBonus.getCollectionFactor(bonusType, collectionName, level, getNewYearBonusConfig())

    @classmethod
    def getCommonCollectionFactor(cls, collectionName):
        return cls._getCommon(cls.getCollectionFactor, collectionName)

    @classmethod
    def getCollectionLevels(cls):
        result = {}
        for collectionName in YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR, useMega=False, usePet=False):
            result[collectionName] = cls.getCollectionLevelByName(collectionName)

        return result

    @classmethod
    def getCollectionLevelByName(cls, collectionName):
        config = getNewYearBonusConfig()
        requester = cls._itemsCache.items.festivity
        collectionDistrs = requester.getCollectionDistributions()
        collectionStrID = YEARS_INFO.getCollectionSettingID(collectionName, YEARS_INFO.CURRENT_YEAR_STR)
        collectionID = YEARS_INFO.getCollectionIntID(collectionStrID)
        return config.getCollectionLevel(collectionDistrs[collectionID]) if requester.isSynced() else 0

    @classmethod
    def getUniqueToysLevel(cls):
        config = getNewYearBonusConfig()
        requester = cls._itemsCache.items.festivity
        collectionDistrs = requester.getCollectionDistributions()
        begin, end = YEARS_INFO.getCollectionDistributionsRangeForYear(YEARS_INFO.CURRENT_YEAR)
        toysLen = len(YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR, useMega=False, usePet=False))
        return config.getUniqueToysLevel(collectionDistrs[begin:end][:toysLen]) if requester.isSynced() else 0

    @classmethod
    def getUniqueToyRating(cls):
        config = getNewYearBonusConfig()
        requester = cls._itemsCache.items.festivity
        collectionDistrs = requester.getCollectionDistributions()
        begin, end = YEARS_INFO.getCollectionDistributionsRangeForYear(YEARS_INFO.CURRENT_YEAR)
        toysLen = len(YEARS_INFO.getCollectionTypesByYear(YEARS_INFO.CURRENT_YEAR, useMega=False, usePet=False))
        return config.calculateUniqueToysRating(collectionDistrs[begin:end][:toysLen]) if requester.isSynced() else 0

    @classmethod
    def getCollectionBonusLevels(cls):
        levels = getNewYearBonusConfig().getCollectionLevelsRating()
        result = [ (levels[i], levels[i + 1] - 1) for i in xrange(len(levels) - 1) ]
        result.append((levels[-1], None))
        return result

    @classmethod
    def getCollectionBonuses(cls, collectionName, bonusType):
        return getNewYearBonusConfig().getCollectionBonuses(bonusType, collectionName)

    @classmethod
    def getCommonCollectionBonuses(cls, collectionName):
        return cls._getCommon(cls.getCollectionBonuses, collectionName)

    @classmethod
    def getUniqueToysBonuses(cls, bonusType):
        return getNewYearBonusConfig().getUniqueToysBonuses(bonusType)

    @classmethod
    def getCommonUniqueToysBonuses(cls):
        return cls._getCommon(cls.getUniqueToysBonuses)

    @classmethod
    def getCommonRangedUniqueToysBonuses(cls):
        maximumUniqueToysRating = len(new_year.g_cache.toys)
        uniqueToysBonuses = cls.getCommonUniqueToysBonuses()
        uniqueToysLevelsRating = getNewYearBonusConfig().getUniqueToysLevelsRating()
        return [ (bonus, uniqueToysLevelsRating[i], uniqueToysLevelsRating[i + 1] - 1 if i + 1 != len(uniqueToysLevelsRating) else maximumUniqueToysRating) for i, bonus in enumerate(uniqueToysBonuses) ]

    @classmethod
    def getPostEventBonus(cls, bonusType):
        return cls._itemsCache.items.festivity.getMaxReachedBonusValue(bonusType)

    @classmethod
    def getPostEventAtmosphereMultiplier(cls, bonusType):
        return cls._itemsCache.items.festivity.getMaxReachedBonusInfo(bonusType)[FormulaInfo.MULTIPLIER]

    @classmethod
    def getPostEventCollectionsBonus(cls, bonusType):
        return cls._itemsCache.items.festivity.getMaxReachedBonusInfo(bonusType)[FormulaInfo.COLLECTION_BONUS]

    @classmethod
    def getCommonPostEventBonus(cls):
        return cls._getCommon(cls.getPostEventBonus)

    @classmethod
    def getCommonPostEventAtmosphereMultiplier(cls):
        return cls._getCommon(cls.getPostEventAtmosphereMultiplier)

    @classmethod
    def getCommonPostEventCollectionsBonus(cls):
        return cls._getCommon(cls.getPostEventCollectionsBonus)
