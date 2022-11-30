# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/NYDogConfig.py
from typing import Dict
from ny_common.settings import NYDogConsts

class NYDogConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getDailyStrokeCountThreshold(self):
        return self._config.get(NYDogConsts.DAILY_STROKE_COUNT_THRESHOLD, 0)

    def getStrokeRandomResources(self):
        return self._config.get(NYDogConsts.STROKE_RANDOM_RESOURCES, 0)
