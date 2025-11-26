# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/PetSynergyConfig.py
import typing
from pet_constants import PetSynergyConsts as pc
if typing.TYPE_CHECKING:
    from typing import Dict

class PetSynergyConfig(object):

    def __init__(self, config):
        self._config = config

    def getSynergyById(self, synergyId):
        return self._config.get(synergyId, {})

    def getSynergyLevels(self, synergyId):
        return self.getSynergyById(synergyId).get(pc.SYNERGY_LEVELS, tuple())

    def getSynergyPoints(self, synergyPointType):
        return self._config.get(pc.POINTS, {}).get(synergyPointType, 0)

    def getSynergeyDecayDays(self):
        return self._config.get(pc.DECAY_DAYS, 0)

    def getSynergyDecayPoints(self):
        return self._config.get(pc.DECAY_POINTS, 0)
