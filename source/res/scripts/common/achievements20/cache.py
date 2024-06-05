# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/achievements20/cache.py
from functools import partial
from time import time
from enum import Enum
from typing import TYPE_CHECKING, Union, Set, List, Dict, Optional, Any, Iterable
from account_shared import getCustomizationItem
from bonus_readers import readBonusSection, SUPPORTED_BONUSES
from constants import IS_CLIENT, IS_WEB, MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from dossiers2.custom.cache import getCache as getHelperCache
from dossiers2.custom.dependencies import VEHICLE_ACHIEVEMENTS_DEPENDENCIES, CUSTOMIZATION_ACHIEVEMENTS_DEPENDENCIES, VEHICLE_ACHIEVEMENTS_POP_UPS, CUSTOMIZATION_ACHIEVEMENTS_POP_UPS, _processAchievementDependency
from items import vehicles, ITEM_TYPES, ITEM_TYPE_NAMES, parseIntCompactDescr
from items.components.c11n_constants import CustomizationType
from nations import NAMES, INDICES
from realm_utils import ResMgr as rmgr
from soft_exception import SoftException
from wotdecorators import singleton
if TYPE_CHECKING:
    from items.components.c11n_components import BaseCustomizationItem
    from dossiers2.common.DossierDescr import DossierDescr
    from items.vehicles import VehicleType
    from ResMgr import DataSection
DEPRECATED_BONUSES = {'xp',
 'tankmenXP',
 'xpFactor',
 'creditsFactor',
 'vehicleXP',
 'freeXPFactor',
 'tankmenXPFactor',
 'vehicleXPFactor'}
ACHIEVEMENTS20_SUPPORTED_BONUSES = SUPPORTED_BONUSES - DEPRECATED_BONUSES
ALLOWED_CUSTOMIZATION_TAGS = frozenset(('c11n2D', 'c11n3D'))
ITEM_CONDITION_KEYS = frozenset(('vehicle', 'customizationItem'))
ITEM_FILTER_CONDITION_KEYS = frozenset(('vehicleFilter', 'customizationItemFilter'))
VEHICLE_FILTER_CONDITION_KEYS = frozenset(('nations', 'vehClasses', 'levels'))
ALLOWED_ACHIEVEMENT_TYPES = frozenset(('vehicleAchievements', 'customizationAchievements'))
ALLOWED_CONDITIONS_BY_ACHIEVEMENT_TYPE = {'vehicleAchievements': {'vehicle', 'vehicleFilter', 'requiredAchievementIDs'},
 'customizationAchievements': {'customizationItem', 'customizationItemFilter', 'requiredAchievementIDs'}}

class ProgressiveTypes(Enum):
    PROGRESSIVE = 'progressive'
    NOT_PROGRESSIVE = 'notProgressive'


_VALID_PROGRESSIVE_TYPES = {k.value for k in ProgressiveTypes}

class UIConfigFields(Enum):
    TYPE = 'type'
    BACKGROUND = 'background'
    STRING_KEY = 'stringKey'
    ICON_POSITION = 'iconPosition'
    ORDER = 'order'
    THEME = 'theme'
    ICON_SIZE_MAP = 'iconSizeMap'
    VEHICLE = 'vehicle'


_VALID_UI_CONFIG_KEYS = {k.value for k in UIConfigFields}

class IconPositions(Enum):
    TOP = 'top'
    CENTER = 'center'
    BOTTOM = 'bottom'


_VALID_ICON_POSITIONS = {k.value for k in IconPositions}

class IconSizeMap(Enum):
    DEFAULT = ''
    PERSONAL_MISSIONS = 'personal_missions'


_VALID_ICON_SIZE_MAPS = {k.value for k in IconSizeMap}
ROOT_ACHIEVEMENT_IDS = (('vehicleAchievements', 1), ('vehicleAchievements', 2), ('customizationAchievements', 1))
_CONFIG_FILE = 'scripts/item_defs/advanced_achievements/advanced_achievements.xml'

def getCache():
    return g_cache


def _readConfig():
    section = rmgr.openSection(_CONFIG_FILE)['achievements']
    config = {}
    for name, value in section.items():
        if name in config:
            raise SoftException('Duplicate achievement section name: {}'.format(name))
        try:
            config[name] = __readAchievements(name, value)
        except SoftException as e:
            raise SoftException("Error: '{}', achievement type '{}'".format(e.message, name))

    return config


def __readUIConfig(section, achievementID):
    uiConfig = {}
    if section.has_key('UI'):
        for pName, pValue in section['UI'].items():
            if pName not in _VALID_UI_CONFIG_KEYS:
                raise SoftException('Wrong UI parameter {} for achievement {}'.format(pName, achievementID))
            if pName in uiConfig:
                raise SoftException('Duplicated UI parameter {} for achievement {}'.format(pName, achievementID))
            if pName == UIConfigFields.ICON_SIZE_MAP.value and pValue.asString not in _VALID_ICON_SIZE_MAPS:
                raise SoftException('Invalid iconSizeMap {} parameter {} for achievement {}'.format(pValue.asString, pName, achievementID))
            if pName == UIConfigFields.ORDER.value:
                uiConfig[pName] = list(map(int, pValue.asString.split()))
            uiConfig[pName] = pValue.asString

    return uiConfig


def __readAchievements(achievementsType, achievementsSection):
    if achievementsSection is None:
        return {}
    else:
        requiredAchievementIDs = set()
        availableAchievementIDs = set()
        deprecatedAchievementIDs = set()
        achievements = {}
        for name, value in achievementsSection.items():
            if name != 'achievement':
                raise SoftException("Unexpected name '{}'".format(name))
            achievementID = value.readInt('id', -1)
            if achievementID < 0:
                raise SoftException("Achievement id should be non-negative '{}'".format(value.readString('id')))
            if achievementID in achievements:
                raise SoftException("Duplicate achievement id '{}'".format(achievementID))
            try:
                conditions = __readConditions(value['conditions'])
                if set(conditions.iterkeys()) - ALLOWED_CONDITIONS_BY_ACHIEVEMENT_TYPE[achievementsType]:
                    raise SoftException('Unexpected conditions for achievement type: {}'.format(set(conditions.iterkeys()) - ALLOWED_CONDITIONS_BY_ACHIEVEMENT_TYPE[achievementsType]))
                if 'requiredAchievementIDs' in conditions:
                    if achievementID in conditions['requiredAchievementIDs']:
                        raise SoftException("Own achievement id can't be at required achievements list")
                    requiredAchievementIDs |= conditions['requiredAchievementIDs']
                stages = __readStages(value['stages'], conditions)
                isDeprecated = value.readBool('deprecated', False)
                if isDeprecated:
                    deprecatedAchievementIDs.add(achievementID)
                else:
                    availableAchievementIDs.add(achievementID)
                openByUnlock = value.has_key('openByUnlock')
                if openByUnlock and achievementsType != 'vehicleAchievements':
                    raise SoftException("Only vehicleAchievements could have openByUnlock achivement '{}'".format(value.readString('id')))
                achievementData = {'id': achievementID,
                 'stages': stages,
                 'conditions': conditions,
                 'type': achievementsType,
                 'deprecated': isDeprecated,
                 'openByUnlock': openByUnlock}
                if IS_CLIENT or IS_WEB:
                    achievementData['UI'] = __readUIConfig(value, achievementID)
            except SoftException as e:
                raise SoftException(e.message + ", achievement id: '{}'".format(achievementID))

            achievements[achievementID] = Achievement(achievementData)

        if deprecatedAchievementIDs & requiredAchievementIDs:
            raise SoftException('Deprecated achievement can not be required: {}'.format(deprecatedAchievementIDs & requiredAchievementIDs))
        if requiredAchievementIDs - availableAchievementIDs:
            raise SoftException('Missed some required achievements: {}'.format(requiredAchievementIDs - availableAchievementIDs))
        return achievements


def __stageAllValueGetterByVehicleFilter(filterData):
    vehicleCache = getHelperCache()
    vehiclesByFilter = vehicleCache['vehiclesInTrees']
    if 'nations' in filterData and filterData['nations'] != set(INDICES.itervalues()):
        nationVehicles = set()
        for nationID in filterData['nations']:
            nationVehicles |= vehicleCache['vehiclesInTreesByNation'][nationID]

        vehiclesByFilter &= nationVehicles
    if 'vehClasses' in filterData and filterData['vehClasses'] != vehicles.VEHICLE_CLASS_TAGS:
        classVehicles = set()
        for vehClass in filterData['vehClasses']:
            classVehicles |= vehicleCache['vehiclesByClass'][vehClass]

        vehiclesByFilter &= classVehicles
    if 'levels' in filterData and filterData['levels'] != set(xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1)):
        levelVehicles = set()
        for level in filterData['levels']:
            levelVehicles |= vehicleCache['vehiclesByLevel'].get(level, set())

        vehiclesByFilter &= levelVehicles
    return len(vehiclesByFilter)


def __stageAllValueGetterByCustomizationItemFilter(filterData):
    customizationItemTypesCache = vehicles.g_cache.customization20().itemTypes
    allValue = 0
    if 'custTypes' in filterData:
        for custType in filterData['custTypes']:
            allValue += len(customizationItemTypesCache[custType])

    return allValue


__stageAllValueGetterByCondition = {'vehicleFilter': __stageAllValueGetterByVehicleFilter,
 'customizationItemFilter': __stageAllValueGetterByCustomizationItemFilter}

def __readStages(stagesSection, conditions):
    if stagesSection is None:
        return []
    else:
        stages = []
        for name, value in stagesSection.items():
            if name != 'stage':
                raise SoftException('')
            stageValue = value.readString('value')
            if not stageValue:
                raise SoftException("Missed stage '{}' value".format(len(stages)))
            if stageValue == 'all':
                stageValue = 0
                for conditionName, conditionData in conditions.iteritems():
                    if conditionName not in __stageAllValueGetterByCondition:
                        raise SoftException("Unexpected condition '{}' for 'all' value, stage index: {}".format(conditionName, len(stages)))
                    stageValue += __stageAllValueGetterByCondition[conditionName](conditionData)

            else:
                stageValue = int(stageValue)
            if stageValue < 1:
                raise SoftException('Stage value should be greater than 0: {}, stage index: {}'.format(stageValue, len(stages)))
            points = value.readInt('points', 0)
            rewards = readBonusSection(ACHIEVEMENTS20_SUPPORTED_BONUSES, value['rewards'])
            if stages and stages[-1]['value'] >= stageValue:
                raise SoftException('Stages should be increased sequence by stage value: {}, stage index: {}'.format(stageValue, len(stages)))
            stages.append({'id': len(stages) + 1,
             'value': stageValue,
             'points': points,
             'rewards': rewards})

        return stages


def __readVehicleFilterConditions(filterSection):
    if filterSection is None:
        return {}
    else:
        unexpectedFilterKeys = set(filterSection.keys()) - VEHICLE_FILTER_CONDITION_KEYS
        if unexpectedFilterKeys:
            raise SoftException('Unexpected filter keys: {}'.format(unexpectedFilterKeys))
        if filterSection.has_key('nations'):
            nations = set(filterSection.readString('nations').split())
            invalidNations = nations - set(NAMES)
            if invalidNations:
                raise SoftException('Invalid nations: {}'.format(invalidNations))
            nationsIDs = {INDICES[nation] for nation in nations}
        else:
            nationsIDs = set(INDICES.itervalues())
        if filterSection.has_key('vehClasses'):
            vehClasses = set(filterSection.readString('vehClasses').split())
            invalidVehClasses = vehClasses - vehicles.VEHICLE_CLASS_TAGS
            if invalidVehClasses:
                raise SoftException('Invalid vehicle types: {}'.format(invalidVehClasses))
        else:
            vehClasses = vehicles.VEHICLE_CLASS_TAGS
        if filterSection.has_key('levels'):
            levels = set((int(level) for level in filterSection.readString('levels').split()))
            if any((level < MIN_VEHICLE_LEVEL or level > MAX_VEHICLE_LEVEL for level in levels)):
                raise SoftException('Invalid levels')
        else:
            levels = set(xrange(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL + 1))
        return {'nations': nationsIDs,
         'vehClasses': vehClasses,
         'levels': levels}


def __readCustomizationItemConditions(customizationItemSection):
    custType, custID = customizationItemSection.asString.split(':')
    item, error = getCustomizationItem(custType, int(custID))
    if error:
        raise SoftException('Invalid customization item, error - {}'.format(error))
    return item.compactDescr


def __readCustomizationItemFilter(filterSection):
    if filterSection is None:
        return {}
    else:
        unexpectedFilterKeys = set(filterSection.keys()) - {'custTypes', 'tags', 'progressiveTypes'}
        if unexpectedFilterKeys:
            raise SoftException('Unexpected filter keys: {}'.format(unexpectedFilterKeys))
        if filterSection.has_key('custTypes'):
            custTypes = set(filterSection.readString('custTypes').split())
            custTypeIDs = {getattr(CustomizationType, custType.upper()) for custType in custTypes}
        else:
            custTypeIDs = CustomizationType.RANGE
        if filterSection.has_key('tags'):
            tags = set(filterSection.readString('tags').split())
        else:
            tags = set()
        unexpectedCustamizationTags = tags - ALLOWED_CUSTOMIZATION_TAGS
        if unexpectedCustamizationTags:
            raise SoftException('Unexpected customization tags: {}'.format(unexpectedCustamizationTags))
        if filterSection.has_key('progressiveTypes'):
            progressiveTypes = set(filterSection.readString('progressiveTypes').split())
            unexpectedProgressiveTypes = progressiveTypes - _VALID_PROGRESSIVE_TYPES
            if unexpectedProgressiveTypes:
                raise SoftException('Unexpected progressive types keys: {}'.format(unexpectedProgressiveTypes))
            progressive = progressiveTypes
        else:
            progressive = _VALID_PROGRESSIVE_TYPES
        return {'custTypes': custTypeIDs,
         'tags': tags,
         'progressiveTypes': progressive}


__conditionReaders = {'vehicle': lambda vehicleSection: vehicles.g_cache.vehicle(*vehicles.g_list.getIDsByName(vehicleSection.asString)).compactDescr,
 'customizationItem': __readCustomizationItemConditions,
 'vehicleFilter': __readVehicleFilterConditions,
 'customizationItemFilter': __readCustomizationItemFilter,
 'requiredAchievementIDs': lambda achievementsSection: set(map(int, achievementsSection.asString.split()))}

def __readConditions(conditionsSections):
    if conditionsSections is None:
        return {}
    else:
        conditions = {}
        for name, value in conditionsSections.items():
            if name in conditions:
                raise SoftException('Duplicate condition type: {}'.format(name))
            if name not in __conditionReaders:
                raise SoftException('Unexpected condition: {}'.format(name))
            if len(conditions) > 0:
                raise SoftException('Should be only 1 condition type')
            conditions[name] = __conditionReaders[name](value)

        return conditions


@singleton
class g_cache(object):

    def __init__(self):
        self.__data = {}
        self.__totalVehicleAchievement = None
        return

    def init(self):
        self.__data = data = _readConfig()
        achievementsByConditions = data.setdefault('achievementsByConditions', {})
        for achievementType, achievementsByType in data.iteritems():
            (VEHICLE_ACHIEVEMENTS_POP_UPS if achievementType == 'vehicleAchievements' else CUSTOMIZATION_ACHIEVEMENTS_POP_UPS).extend(achievementsByType.iterkeys())
            dependencies = VEHICLE_ACHIEVEMENTS_DEPENDENCIES if achievementType == 'vehicleAchievements' else CUSTOMIZATION_ACHIEVEMENTS_DEPENDENCIES
            for achievementID, achievement in achievementsByType.iteritems():
                rewards = achievement.getAllBonuses()
                if rewards and 'dogTagComponents' in rewards:
                    self.__totalVehicleAchievement = (achievementType, achievementID)
                for conditionKey, conditionData in achievement.conditions.iteritems():
                    if conditionKey in ITEM_CONDITION_KEYS:
                        achievementsByConditions.setdefault(conditionKey, {}).setdefault(conditionData, set()).add(achievement)
                    if conditionKey in ITEM_FILTER_CONDITION_KEYS:
                        itemFilter = achievementsByConditions.setdefault(conditionKey, {})
                        for filterName, filterValues in conditionData.iteritems():
                            filterData = itemFilter.setdefault(filterName, {})
                            for filterValue in filterValues:
                                filterData.setdefault(filterValue, set()).add(achievement)

                    if conditionKey == 'requiredAchievementIDs':
                        requiredAchievements = [ data[achievementType][requiredAchievementID] for requiredAchievementID in conditionData if not data[achievementType][requiredAchievementID].deprecated ]
                        for requiredAchievement in requiredAchievements:
                            dependencies.setdefault(requiredAchievement.id, []).append(partial(_processAchievementDependency, achievement, requiredAchievements))

                    raise SoftException('Unexpected condition key: {}, achievement type: {}, achievement id: {}'.format(conditionKey, achievementType, achievementID))

    def _getAchievementsByItem(self, itemTypeName, item):
        return self.__data.get('achievementsByConditions', {}).get(itemTypeName, {}).get(item.compactDescr, ())

    def _getAchievementsByVehicleFilter(self, itemTypeName, vehicleType):
        achievementsByConditions = self.__data.get('achievementsByConditions', {})
        achievementsByVehicleFilter = achievementsByConditions.get('vehicleFilter', None)
        if achievementsByVehicleFilter and vehicleType.compactDescr in getHelperCache().get('vehiclesByClass', {}).get(vehicleType.classTag, ()):
            achievements = achievementsByVehicleFilter.get('nations', {}).get(vehicleType.id[0], set()) & achievementsByVehicleFilter.get('vehClasses', {}).get(vehicleType.classTag, set()) & achievementsByVehicleFilter.get('levels', {}).get(vehicleType.level, set())
        else:
            achievements = ()
        return achievements

    def _getAchievementsByCustomizationItemFilter(self, itemTypeName, item):
        achievementsByConditions = self.__data.get('achievementsByConditions', {})
        achievementsByCustItemFilter = achievementsByConditions.get('customizationItemFilter', None)
        achievements = set()
        if achievementsByCustItemFilter:
            achievements.update(achievementsByCustItemFilter.get('custTypes', {}).get(item.itemType, set()))
            progressiveAchievements = achievementsByCustItemFilter.get('progressiveTypes', None)
            if progressiveAchievements:
                if item.isProgressive():
                    progressiveType = ProgressiveTypes.PROGRESSIVE.value
                else:
                    progressiveType = ProgressiveTypes.NOT_PROGRESSIVE.value
                achievements &= progressiveAchievements.get(progressiveType, set())
            for tag in item.tags:
                achievmenetsByTag = achievementsByCustItemFilter.get('tags', {}).get(tag, None)
                if achievmenetsByTag:
                    achievements &= achievmenetsByTag

        return tuple(achievements)

    _achievementsGettersByItemType = {ITEM_TYPES.vehicle: (_getAchievementsByItem, _getAchievementsByVehicleFilter),
     ITEM_TYPES.customizationItem: (_getAchievementsByItem, _getAchievementsByCustomizationItemFilter)}

    def getAchievementsByItem(self, item, receivedItems):
        achievements = []
        itemCompactDescr = item.compactDescr
        itemTypeID, _, __ = parseIntCompactDescr(itemCompactDescr)
        vehicleCache = getHelperCache()
        if not (itemTypeID == ITEM_TYPES.customizationItem and item.isProgressive()):
            if itemTypeID not in self._achievementsGettersByItemType or itemCompactDescr in receivedItems:
                return achievements
        itemTypeName = ITEM_TYPE_NAMES[itemTypeID]
        for getter in self._achievementsGettersByItemType.get(itemTypeID, ()):
            achievements.extend(getter(self, itemTypeName, item))

        if itemTypeID == ITEM_TYPES.vehicle and itemCompactDescr not in vehicleCache['vehiclesInTrees']:
            achievements = [ item for item in achievements if not item.isAchievedByUnlock() ]
        return achievements

    def getAchievementByID(self, achievementType, achievementID):
        return self.__data.get(achievementType, {}).get(achievementID, None)

    def getTotalVehicleAchievement(self):
        return self.__totalVehicleAchievement


class Achievement(object):

    def __init__(self, achievementData):
        self.__data = achievementData

    def __getattr__(self, item):
        if item in self.__data:
            return self.__data[item]
        raise AttributeError

    def __getitem__(self, item):
        try:
            return self.__data[item]
        except KeyError:
            raise KeyError

    def __contains__(self, item):
        return item in self.__data

    def getActiveStage(self, currentValue, currentStage):
        stages = self.__data.get('stages', None)
        lastStage = len(stages)
        if not stages or currentStage > lastStage:
            return
        elif currentValue >= stages[-1]['value']:
            return stages[-1]
        else:
            for stageIndex in xrange(currentStage - 1 if currentStage else 0, lastStage):
                if currentValue < stages[stageIndex]['value']:
                    return stages[stageIndex]

            return

    def isAchievedByUnlock(self):
        return self.__data.get('openByUnlock', False)

    def isAchievementCompleted(self, currentValue):
        stages = self.__data.get('stages', None)
        return stages and currentValue >= stages[-1]['value']

    @staticmethod
    def isAnyStageCompleted(currentStage):
        return currentStage > 0

    def getCurrentDataFromDossier(self, dossierDescr):
        achievementType = self.__data.get('type', None)
        achievementID = self.__data.get('id', None)
        return (0, 0, 0) if achievementType not in dossierDescr or achievementID not in dossierDescr[achievementType] else dossierDescr[achievementType][achievementID]

    def updateValueInDossier(self, dossierDescr, currentValue=None, currentStage=None, currentTimestamp=None):
        data = self.__data
        if currentValue is None or currentStage is None or currentTimestamp is None:
            currentValue, currentStage, currentTimestamp = self.getCurrentDataFromDossier(dossierDescr)
        activeStage = self.getActiveStage(currentValue, currentStage)
        if not activeStage:
            return
        else:
            if currentStage < activeStage['id'] and currentValue + 1 >= activeStage['value']:
                currentStage = activeStage['id']
                currentTimestamp = int(time())
            dossierDescr[data['type']][data['id']] = (currentValue + 1, currentStage, currentTimestamp)
            return

    def initializeValueInDossier(self, dossierDescr, currentValue=None, currentStage=None):
        data = self.__data
        currentValue = currentValue or 0
        currentStage = currentStage or 0
        currentTimestamp = int(time())
        activeStage = self.getActiveStage(currentValue, currentStage)
        if activeStage:
            currentStage = activeStage['id']
            if currentValue < activeStage['value']:
                currentStage -= 1
        dossierDescr[data['type']][data['id']] = (currentValue, currentStage, currentTimestamp)
        return (currentValue, currentStage, currentTimestamp)

    def getStageBonusByValue(self, currentStage):
        stages = self.__data.get('stages', None)
        return {} if not stages or currentStage > len(stages) else stages[currentStage - 1].get('rewards', {})

    def getStagePointsByValue(self, currentStage):
        stages = self.__data.get('stages', None)
        return 0 if not stages or currentStage > len(stages) else stages[currentStage - 1]['points']

    def getAllBonuses(self):
        result = {}
        stages = self.__data.get('stages', None)
        if not stages:
            return result
        else:
            for stage in stages:
                rewards = stage.get('rewards')
                if rewards:
                    for rewardName, rewardValue in rewards.iteritems():
                        result.setdefault(rewardName, []).append(rewardValue)

            return result


def init():
    g_cache.init()
