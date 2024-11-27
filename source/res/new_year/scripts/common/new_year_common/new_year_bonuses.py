# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/new_year_bonuses.py
from constants import ALL_EVENT_TYPES_FOR_BONUSES
from constants_utils import AbstractExtensionBonuses
from functools import partial
from new_year_common.items import collectibles
from new_year_common.items.components.ny_constants import CurrentNYConstants, TOY_TYPE_IDS_BY_NAME, YEARS_INFO, YEARS, PREV_NY_TOYS_COLLECTIONS, TOY_PARAMETER
from optional_bonuses import __mergeItems as mergeItems, __mergeValue as mergeValue
from soft_exception import SoftException

class NewYearBonuses(AbstractExtensionBonuses):

    def _getSupportedQuests(self):
        return {ALL_EVENT_TYPES_FOR_BONUSES: {CurrentNYConstants.TOY_FRAGMENTS,
                                       CurrentNYConstants.FILLERS,
                                       CurrentNYConstants.TOY_BONUS,
                                       CurrentNYConstants.ANY_OF,
                                       CurrentNYConstants.ATMOSPHERE_POINTS,
                                       CurrentNYConstants.ALL_OF}}

    def _getReaders(self):
        result = {CurrentNYConstants.TOY_FRAGMENTS: NewYearBonuses.__readBonusNYToyFragments,
         CurrentNYConstants.ANY_OF: NewYearBonuses.__readBonusNYAnyOf,
         CurrentNYConstants.FILLERS: NewYearBonuses.__readBonusNYFillers,
         CurrentNYConstants.ATMOSPHERE_POINTS: NewYearBonuses.__readBonusNYAtmospherePoints,
         CurrentNYConstants.ALL_OF: NewYearBonuses.__readBonusNYAllOf}
        result.update({'ny{}Toy'.format(year):partial(NewYearBonuses.__readBonusNYToy, year) for year in YEARS.ALL})
        return result

    def _getMergers(self):
        result = {CurrentNYConstants.TOYS: mergeItems,
         CurrentNYConstants.TOY_FRAGMENTS: mergeValue,
         CurrentNYConstants.ANY_OF: NewYearBonuses.__mergeNYAnyOf,
         CurrentNYConstants.FILLERS: mergeValue,
         CurrentNYConstants.ATMOSPHERE_POINTS: mergeValue,
         CurrentNYConstants.ALL_OF: mergeItems}
        result.update({collection:mergeItems for collection in PREV_NY_TOYS_COLLECTIONS})
        return result

    def _getItemInventoryCheckers(self):
        return {CurrentNYConstants.TOYS: lambda account, key: account.AccountNewYearComponent.isToyPresentInCollection(key, YEARS_INFO.CURRENT_YEAR_STR)}

    def _getUniqueBonusCheckers(self):
        return {CurrentNYConstants.TOYS: NewYearBonuses.__nyToysExistanceChecker}

    def _getUniqueBonusCacheUpdater(self):
        return {CurrentNYConstants.TOYS: NewYearBonuses.__nyToysCacheUpdater}

    @staticmethod
    def __readBonusNYToy(year, bonus, name, section, eventType, checkLimit):
        if section.has_key('id'):
            tid = section['id'].asInt
            cache = collectibles.g_cache[YEARS.getYearStrFromYearNum(year)].toys
            if tid not in cache:
                raise SoftException('Unknown NY{} toyID: {}'.format(year, tid))
            count = section['count'].asInt if section.has_key('count') else 0
            toysCollectionKey = YEARS_INFO.getCollectionKeyForYear(year)
            nyToys = bonus.setdefault(toysCollectionKey, {})
            nyToys[tid] = count

    @staticmethod
    def __nyToysExistanceChecker(bonusValue, cache):
        for itemID in bonusValue.iterkeys():
            if cache.isItemExists(CurrentNYConstants.TOYS, itemID):
                return True

        return False

    @staticmethod
    def __nyToysCacheUpdater(bonusValue, cache):
        for itemID in bonusValue.iterkeys():
            cache.onItemAccepted(CurrentNYConstants.TOYS, itemID)

    @staticmethod
    def __readBonusNYToyFragments(bonus, name, section, eventType, checkLimit):
        count = section.asInt
        bonus[CurrentNYConstants.TOY_FRAGMENTS] = bonus.get(CurrentNYConstants.TOY_FRAGMENTS, 0) + count

    @staticmethod
    def __readBonusNYAnyOf(bonus, name, section, eventType, checkLimit):
        if section.has_key('setting'):
            settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[section.readString('setting')]
            if settingID not in TOY_PARAMETER.CURRENT_USUAL_RANGE:
                raise SoftException('Unavailable toy setting - {}'.format(settingID))
        else:
            settingID = -1
        if section.has_key('type'):
            typeID = TOY_TYPE_IDS_BY_NAME[section.readString('type')]
            if typeID not in TOY_PARAMETER.TOY_USUAL_TYPES_RANGE:
                raise SoftException('Unavailable toy type - {}'.format(typeID))
        else:
            typeID = -1
        if section.has_key('rank'):
            rank = section['rank'].asInt
        else:
            rank = -1
        bonus.setdefault(CurrentNYConstants.ANY_OF, []).append((typeID, settingID, rank))

    @staticmethod
    def __mergeNYAnyOf(total, key, value, isLeaf=False, count=1, *args):
        result = total.setdefault(key, [])
        result.extend(value if isinstance(value, list) else [value])

    @staticmethod
    def __readBonusNYAllOf(bonus, name, section, eventType, checkLimit):
        if section.has_key('setting'):
            settingID = YEARS_INFO.CURRENT_SETTING_IDS_BY_NAME[section.readString('setting')]
        else:
            settingID = -1
        if section.has_key('type'):
            typeID = TOY_TYPE_IDS_BY_NAME[section.readString('type')]
        else:
            typeID = -1
        if section.has_key('rank'):
            rank = section['rank'].asInt
        else:
            rank = -1
        if section.has_key('count'):
            count = section['count'].asInt
        else:
            count = 1
        bonus.setdefault(CurrentNYConstants.ALL_OF, {}).setdefault((typeID, settingID, rank), 0)
        bonus[CurrentNYConstants.ALL_OF][(typeID, settingID, rank)] += count

    @staticmethod
    def __readBonusNYFillers(bonus, name, section, eventType, checkLimit):
        count = section.asInt
        bonus[CurrentNYConstants.FILLERS] = bonus.get(CurrentNYConstants.FILLERS, 0) + count

    @staticmethod
    def __readBonusNYAtmospherePoints(bonus, name, section, eventType, checkLimit):
        count = section.asInt
        bonus[CurrentNYConstants.ATMOSPHERE_POINTS] = bonus.get(CurrentNYConstants.ATMOSPHERE_POINTS, 0) + count
