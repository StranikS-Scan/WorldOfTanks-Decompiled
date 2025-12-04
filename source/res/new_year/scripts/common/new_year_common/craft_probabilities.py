# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/common/new_year_common/craft_probabilities.py
from typing import Tuple
from new_year_common.settings import CraftProbsConsts, IS_ENABLED

class CraftProbabilitiesConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config=None):
        self._config = config or {}

    def isEnabled(self):
        return self._config.get(IS_ENABLED, False)

    def getProbabilitiesForTypes(self):
        return self._config.get(CraftProbsConsts.TYPE_PROBABILITIES, ())

    def getProbabilitiesForSettings(self):
        return self._config.get(CraftProbsConsts.SETTING_PROBABILITIES, ())

    def getProbabilitiesForRanks(self):
        return self._config.get(CraftProbsConsts.RANK_PROBABILITIES, ())
