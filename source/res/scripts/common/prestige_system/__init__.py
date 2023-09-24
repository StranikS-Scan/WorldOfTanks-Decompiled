# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/prestige_system/__init__.py
from typing import TYPE_CHECKING
from copy import copy
from itertools import izip
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG
from dossiers2.custom.cache import getCache as getDossiers2Cache, buildCache as buildDossiers2Cache
if TYPE_CHECKING:
    from typing import Optional, Dict, List, Set

class PrestigeConstants(object):
    GRADE_MIN_LEVEL = 1
    GRADES_NUMBER = 20
    PRESTIGE_MAX_LEVEL = 1000
    MAX_GRADE_MARK_ID = -1


def getCache():
    return _g_cache


def computePrestigeCache(config, cache=None, dossiers2Cache=None):
    LOG_DEBUG_DEV('computePrestigeCache config', config)
    if cache is None:
        cache = getCache()
    if not config['enabled']:
        LOG_DEBUG('computePrestigeCache PrestigeSystem disabled, cache will be cleared')
        cache['prestigePoints'] = {}
        return
    else:
        if not getDossiers2Cache():
            buildDossiers2Cache()
        defaultMaxLevel = config['default']['maxLevel']
        defaultLevelCostArgs = config['default']['levelCostArgs']
        overrideItems = config['overrideItems']
        dossier2Cache = dossiers2Cache or getDossiers2Cache()
        allVehicleDescrs = set(dossier2Cache['vehiclesNameToDescr'].values())
        defaultLevels = computeLevelCost(defaultLevelCostArgs, range(1, defaultMaxLevel + 1))
        prestigePoints = computeAllPrestigePoints(defaultLevels, overrideItems, allVehicleDescrs, defaultLevelCostArgs)
        cache['prestigePoints'] = prestigePoints
        return


def computeAllPrestigePoints(defaultLevels, overrideItems, allVehicleDescrs, defaultLevelCostArgs):
    prestigePoints = {vehCD:copy(defaultLevels) for vehCD in allVehicleDescrs}
    for override in overrideItems:
        vehicles = override['vehicles']
        overridePoints, newMaxLevel = computePrestigePoints(override)
        applyOverridePoints(prestigePoints, overridePoints, vehicles, defaultLevelCostArgs, newMaxLevel)

    for vehCD, points in prestigePoints.iteritems():
        if points:
            points[0] = 0

    return prestigePoints


def computePrestigePoints(override):
    if not override.get('enabled', True):
        return ([], 0)
    else:
        points = [0] * PrestigeConstants.PRESTIGE_MAX_LEVEL
        levelsArgs = override.get('levels') or [1, PrestigeConstants.PRESTIGE_MAX_LEVEL]
        levels = preprocessLevels(levelsArgs)
        levelCostArgs = override.get('levelCostArgs')
        if levelCostArgs is not None:
            levelCosts = computeLevelCost(levelCostArgs, levels)
            for _level, _levelCost in izip(levels, levelCosts):
                points[_level - 1] = _levelCost

        newMaxLevel = override.get('maxLevel', None)
        if newMaxLevel is not None:
            points = points[:newMaxLevel]
        return (points, newMaxLevel)


def preprocessLevels(levels):
    if len(levels) == 1:
        return levels
    if len(levels) == 2:
        levels = range(levels[0], levels[1] + 1)
    return levels


def computeLevelCost(levelCostArgs, levels):
    if len(levelCostArgs) == 0:
        return []
    if len(levelCostArgs) == 1:
        return levelCostArgs * len(levels)
    if len(levelCostArgs) == 4:
        levelCostBaseValue, frequency, coefficient, formulaType = levelCostArgs
        if formulaType == 'exponent':
            return [ int(levelCostBaseValue * coefficient ** int(level / frequency)) for level in levels ]
        if formulaType == 'linear':
            return [ int(levelCostBaseValue + coefficient * int(level / frequency)) for level in levels ]


def applyOverridePoints(prestigePointsDict, overridePoints, vehicles, defaultLevelCostArgs, newMaxLevel=None):
    for vehicle in vehicles:
        currentPrestigeLevelForVeh = len(prestigePointsDict[vehicle])
        if newMaxLevel is not None:
            if currentPrestigeLevelForVeh > newMaxLevel:
                prestigePointsDict[vehicle] = prestigePointsDict[vehicle][:newMaxLevel]
            elif currentPrestigeLevelForVeh < newMaxLevel:
                additionalPointsFromDefault = computeLevelCost(defaultLevelCostArgs, range(currentPrestigeLevelForVeh, newMaxLevel))
                prestigePointsDict[vehicle] += additionalPointsFromDefault
        for i, point in enumerate(overridePoints[:len(prestigePointsDict[vehicle])]):
            if point == 0:
                continue
            prestigePointsDict[vehicle][i] = point

    return


_g_cache = {}
