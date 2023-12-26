# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/NYDogConfig.py
from typing import Optional, List, Dict, Tuple
from ny_common.settings import NYDogConsts

class NYDogConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getTokenName(self):
        return self._config.get(NYDogConsts.TOKEN_NAME)

    def getLevels(self):
        return self._config.get(NYDogConsts.LEVELS, [])

    def _getLevelOrNone(self, level):
        levels = self.getLevels()
        return None if level < 0 or level >= len(levels) else levels[level]

    def getLevelLootboxCategory(self, level):
        levelConfig = self._getLevelOrNone(level)
        return levelConfig.get(NYDogConsts.LEVEL_LOOTBOX) if levelConfig else None

    def getLevelPrice(self, level):
        levelConfig = self._getLevelOrNone(level)
        return levelConfig.get(NYDogConsts.LEVEL_PRICE) if levelConfig else None

    def getLevelToys(self, level):
        levelConfig = self._getLevelOrNone(level)
        return levelConfig.get(NYDogConsts.LEVEL_TOYS) if levelConfig else None
