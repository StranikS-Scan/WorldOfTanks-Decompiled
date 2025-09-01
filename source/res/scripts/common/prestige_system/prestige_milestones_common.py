# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/prestige_system/prestige_milestones_common.py
from typing import Optional, Dict, Set, Any, Union
from copy import copy
from constants import IS_CLIENT
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG
from dossiers2.custom.cache import getCache as getDossiers2Cache, buildCache as buildDossiers2Cache
VehCDType = int
PrestigeLevelType = int
InvoiceStatusType = int
ErrorStrType = str
MilestoneData = Dict[str, Any]
MilestonesType = Dict[PrestigeLevelType, MilestoneData]
MilestonesCacheType = Dict[VehCDType, Dict[PrestigeLevelType, MilestonesType]]
OverrideItem = Dict[str, Union[MilestonesType, Set[VehCDType], bool]]

class PrestigeMilestonesConfig(object):

    def __init__(self, config):
        self._config = config
        if IS_CLIENT:
            self.__cache = {}
            if self._config:
                computePrestigeMilestonesCache(config, self.__cache)
        else:
            self.__cache = getCache()

    @property
    def milestones(self):
        return self.__cache['prestigeMilestones']


def getCache():
    return _g_cache


def computePrestigeMilestonesCache(config, cache=None, dossiers2Cache=None):
    LOG_DEBUG_DEV('computePrestigeMilestonesCache config', config)
    if cache is None:
        cache = getCache()
    if not config['enabled']:
        LOG_DEBUG('computePrestigeMilestonesCache PrestigeMilestonesSystem disabled, cache will be cleared')
        cache['prestigeMilestones'] = {}
        cache['enabled'] = False
        return
    else:
        cache['enabled'] = True
        _dossier2Cache = dossiers2Cache
        if _dossier2Cache is None:
            if not getDossiers2Cache():
                buildDossiers2Cache()
            _dossier2Cache = getDossiers2Cache()
        cache['prestigeMilestones'] = computeMilestonesCache(config['defaultMilestones'], config['milestonesOverrides'], config['enabledVehLevels'], _dossier2Cache['vehiclesByLevel'])
        return


def computeMilestonesCache(defaultMilestones, overrideItems, enabledVehicleLevels, vehiclesByLevel):
    vehicleMilestones = {}
    for level in enabledVehicleLevels:
        vehicleMilestones.update({vehCD:copy(defaultMilestones) for vehCD in vehiclesByLevel[level]})

    for override in overrideItems:
        applyOverrideMilestones(vehicleMilestones, override)

    return vehicleMilestones


def applyOverrideMilestones(vehicleMilestones, override):
    for vehicleCD in override['vehicles']:
        if override['enabled']:
            for prestigeLevel, milestone_data in override['milestones'].items():
                vehicleMilestones[vehicleCD][prestigeLevel] = milestone_data

        if vehicleCD in vehicleMilestones:
            vehicleMilestones.pop(vehicleCD)


_g_cache = {}
