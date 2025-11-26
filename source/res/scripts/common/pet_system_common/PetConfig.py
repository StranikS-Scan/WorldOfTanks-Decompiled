# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/PetConfig.py
import typing
from pet_constants import PetsConsts as pc
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Iterable
INVALID_ID = -1

class PetConfig(object):

    def __init__(self, config):
        self._config = config

    def getPets(self):
        return self._config

    def getPet(self, petID):
        return self.getPets().get(petID, {})

    def getPetType(self, petID):
        return self.getPet(petID).get(pc.PET_TYPE, '')

    def getPetBreed(self, petID):
        return self.getPet(petID).get(pc.PET_BREED, '')

    def getPetUniqueEvents(self, petID):
        return self.getPet(petID).get(pc.PET_EVENTS, set())

    def getPetNames(self, petID):
        return self.getPet(petID).get(pc.PET_NAMES, {})

    def getDefaultNameId(self, petID):
        return self.getPetNames(petID).get(pc.PET_NAMES_DEFAULT, INVALID_ID)

    def getIsDefaultNameLocked(self, petID):
        return self.getPetNames(petID).get(pc.PET_NAMES_DEFAULT_LOCKED, False)

    def getPetUnlockedNamesIDs(self, petID):
        return self.getPetNames(petID).get(pc.PET_NAMES_UNLOCKED, set())

    def getPetPrice(self, petID):
        return self.getPet(petID).get(pc.PET_PRICE, {})

    def getPetUnlockedBonuses(self, petID):
        return self.getPet(petID).get(pc.PET_BONUSES, set())

    def getPetSynergyGroupID(self, petID):
        return self.getPet(petID).get(pc.PET_SYNERGY_GROUP_ID, INVALID_ID)

    def getStockNames(self):
        return self._config.get(pc.STOCK_NAMES, set())

    def getAvailableNames(self, unlockedPetIDs):
        result = set()
        for petID in unlockedPetIDs:
            result |= self.getPetUnlockedNamesIDs(petID)

        result |= self.getStockNames()
        return result

    def getAvailableBonuses(self, unlockedPetIDs):
        result = set()
        for petID in unlockedPetIDs:
            result |= self.getPetUnlockedBonuses(petID)

        return result
