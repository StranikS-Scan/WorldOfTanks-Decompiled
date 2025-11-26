# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/GeneralConfig.py
import typing
from pet_constants import PetSystemGeneralConsts as pc
if typing.TYPE_CHECKING:
    from typing import Dict

class GeneralConfig(object):

    def __init__(self, config):
        self._config = config

    @property
    def isEnabled(self):
        return self._config.get(pc.ENABLED, False)

    @property
    def eventsPerDay(self):
        return self._config.get(pc.EVENT_PER_DAY, 0)

    @property
    def eventsMinBattles(self):
        return self._config.get(pc.EVENT_MIN_BATTLES, 0)

    @property
    def eventsMaxBattles(self):
        return self._config.get(pc.EVENT_MAX_BATTLES, 0)

    @property
    def bonusesPerDay(self):
        return self._config.get(pc.BONUSES_PER_DAY, 0)

    @property
    def showCaseEnabled(self):
        return self._config.get(pc.SHOW_CASE_ENABLED, False)
