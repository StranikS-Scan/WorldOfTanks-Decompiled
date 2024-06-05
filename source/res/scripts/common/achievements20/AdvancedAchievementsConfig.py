# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/achievements20/AdvancedAchievementsConfig.py
from typing import TYPE_CHECKING
from achievements20.settings import AdvancedAchievementsConst
if TYPE_CHECKING:
    from typing import Optional

class AdvancedAchievementsConfig(object):
    __slots__ = ('_config',)

    def __init__(self, config):
        self._config = config

    def isAdvancedAchievementEnabled(self):
        return self._config[AdvancedAchievementsConst.ENABLED]

    def isVehicleAchievementsEnabled(self):
        return self.isAdvancedAchievementEnabled() and self._config[AdvancedAchievementsConst.VEHICLE_ACHIEVEMENTS_ENABLED]

    def isCustomizationAchievementsEnabled(self):
        return self.isAdvancedAchievementEnabled() and self._config[AdvancedAchievementsConst.CUSTOMIZATION_ACHIEVEMENTS_ENABLED]

    def getExcludedVehicles(self):
        return self._config[AdvancedAchievementsConst.EXCLUDED_VEHICLES]

    def getExcludedCustomizations(self):
        return self._config[AdvancedAchievementsConst.EXCLUDED_CUSTOMIZATIONS]
