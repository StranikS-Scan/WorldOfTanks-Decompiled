# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wotlda/cache.py
import os
import logging
from typing import Dict, Any
from helpers.local_cache import FileLocalCache
from gui.game_control.wotlda.constants import LAST_UPDATE_TIMESTAMP, SupportedWTRRange
_logger = logging.getLogger(__name__)

class WotldaCache(FileLocalCache):
    _CACHE_TYPE = ''

    def __init__(self):
        super(WotldaCache, self).__init__('wotlda_cache', (self._CACHE_TYPE, 'loadouts'), async=True)
        self._filePath = self._buildLocalCachePath('wotlda_cache', (self._CACHE_TYPE, 'loadouts'))
        self._cache = {}

    def update(self, data):
        self._setCache(data)
        self.write()

    def clear(self):
        super(WotldaCache, self).clear()
        self.clearCache()

    def getUpdatedAtTimestamp(self):
        return self._cache.get(LAST_UPDATE_TIMESTAMP, 0)

    def isCacheEmpty(self):
        return not bool(self._cache)

    def clearCache(self):
        self._cache.clear()

    def getLoadout(self, vehicleID, *args, **kwargs):
        raise NotImplementedError

    def deleteCacheFile(self):
        try:
            os.remove(self._filePath)
        except OSError:
            _logger.debug('Deleting [%s] file failed.', self._filePath)

    def _getCache(self):
        return self._cache.copy()

    def _setCache(self, data):
        self._cache = data


class EasyTankEquipCache(WotldaCache):
    _CACHE_TYPE = 'easy_tank_equip'

    def getLoadout(self, vehicleID, *args, **kwargs):
        return self._cache.get(str(vehicleID), {})


class EquipmentForSubscribersCache(WotldaCache):
    _CACHE_TYPE = 'subscription'

    def getLoadout(self, vehicleID, *args, **kwargs):
        loadoutType = kwargs.get('loadoutType')
        wtrRange = kwargs.get('wtrRange')
        return self._cache.get(loadoutType, {}).get(wtrRange, {}).get(str(vehicleID), {})


class CrewCache(WotldaCache):
    _CACHE_TYPE = 'crew'

    def getLoadout(self, vehicleID, *args, **kwargs):
        result = {}
        role = kwargs.get('role')
        allSkills = set()
        for range in SupportedWTRRange.allRanges():
            skills = self._cache.get(range.value, {}).get(str(vehicleID), {}).get(role, {})
            if skills:
                allSkills = skills.keys()
                break

        for range in SupportedWTRRange.allRanges():
            skills = self._cache.get(range.value, {}).get(str(vehicleID), {}).get(role, {})
            for skill in allSkills:
                result.setdefault(skill, []).append(skills.get(skill, 0))

        return result
