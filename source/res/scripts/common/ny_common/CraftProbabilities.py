# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/CraftProbabilities.py
from typing import Tuple
from ny_common.settings import CraftProbabilitiesConsts

class CraftProbabilitiesConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def getProbabilitiesForTypes(self):
        return self._config.get(CraftProbabilitiesConsts.TYPE_PROBABILITIES, ())

    def getProbabilitiesForSettings(self):
        return self._config.get(CraftProbabilitiesConsts.SETTING_PROBABILITIES, ())

    def getProbabilitiesForRanks(self):
        return self._config.get(CraftProbabilitiesConsts.RANK_PROBABILITIES, ())
