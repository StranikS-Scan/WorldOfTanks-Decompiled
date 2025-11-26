# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/BonusConfig.py
import typing
from pet_constants import PetBonusesConsts as pc
if typing.TYPE_CHECKING:
    from typing import Dict

class BonusConfig(object):

    def __init__(self, config):
        self._config = config

    def getBonuses(self):
        return self._config

    def getBonusById(self, bonusID):
        return self._config.get(bonusID, {})

    def getBonusResources(self, bonusID):
        return self.getBonusById(bonusID).get(pc.BONUS_RESOURCE, pc.EMPTY_BONUS)
