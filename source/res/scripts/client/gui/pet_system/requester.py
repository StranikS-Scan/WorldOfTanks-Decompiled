# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/requester.py
import logging
import typing
import BigWorld
from gui.pet_system.constants import PS_PDATA_KEYS
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from pet_system_common.pet_constants import PETS_SYSTEM_PDATA_KEY, PetStateBehavior
from skeletons.gui.shared.utils.requesters import IPetSystemRequester
if typing.TYPE_CHECKING:
    from typing import List, Dict, Any, Set
    PetID = int
    EventID = int
    NameID = int
    BonusID = int
    Synergy = int
    SynergyLevel = int
_logger = logging.getLogger(__name__)
INVALID_PET_ID = 0
INVALID_EVENT_ID = 0

class PetRequesterRequester(AbstractSyncDataRequester, IPetSystemRequester):
    dataKey = PETS_SYSTEM_PDATA_KEY

    def isPetUnlocked(self, petID):
        return petID in self.getCacheValue(PS_PDATA_KEYS.UNLOCKED_PETS_IDS, list())

    def getActivePetID(self):
        return self.getCacheValue(PS_PDATA_KEYS.ACTIVE_PETID, INVALID_PET_ID)

    def getActiveEventID(self):
        eventsData = self.getCacheValue(PS_PDATA_KEYS.EVENTS_DATA, {})
        return eventsData.get(PS_PDATA_KEYS.ACTIVE_EVENT, INVALID_EVENT_ID)

    def getUnlockedPetIDs(self):
        return self.getCacheValue(PS_PDATA_KEYS.UNLOCKED_PETS_IDS, list())

    def getStateBehavior(self):
        return self.getCacheValue(PS_PDATA_KEYS.ACTIVE_STATE_BEHAVIOR, PetStateBehavior.BASIC)

    def getSelectedName(self, petID):
        return self.getCacheValue(PS_PDATA_KEYS.STORAGE, {}).get(petID, {}).get(PS_PDATA_KEYS.SELECTED_NAME, 0)

    def getBonuses(self):
        return self.getCacheValue(PS_PDATA_KEYS.BONUS, {})

    def getActiveBonus(self):
        return self.getBonuses().get(PS_PDATA_KEYS.ACTIVE_BONUS, 0)

    def getAppliedBonusCount(self):
        return self.getBonuses().get(PS_PDATA_KEYS.APPLIED_BONUSES, 0)

    def getSynergyPoints(self, petID):
        return self.__getSynergyStorage(petID).get(PS_PDATA_KEYS.SYNERGY_POINTS, 0)

    def getSynergyLevel(self, petID):
        return self.__getSynergyStorage(petID).get(PS_PDATA_KEYS.SYNERGY_LEVEL, 0)

    def getFirstClickedSynergyPets(self):
        return self.getCacheValue(PS_PDATA_KEYS.SYNERGY_FIRST_CLICK, set())

    def __getSynergyStorage(self, petID):
        return self.getCacheValue(PS_PDATA_KEYS.STORAGE, {}).get(petID, {}).get(PS_PDATA_KEYS.SYNERGY_STORAGE, {})

    def _requestCache(self, callback=None):
        BigWorld.player().petSystem.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        petData = data.get(self.dataKey, {})
        result = dict(petData)
        return result
