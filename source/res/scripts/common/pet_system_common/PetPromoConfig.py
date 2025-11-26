# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pet_system_common/PetPromoConfig.py
import typing
from pet_constants import PetPromoConsts
if typing.TYPE_CHECKING:
    from typing import List, Dict, Iterable
INVALID_PET_NAME_ID = -1

class PromoSource(object):
    QUEST_PROGRESSION = 'quest_progression'
    SHOP = 'shop'
    ALL = (QUEST_PROGRESSION, SHOP)


class PetPromoConfig(object):

    def __init__(self, config):
        self._config = config

    def getPets(self):
        return self._config.get(PetPromoConsts.PETS, {})

    def isEnabled(self):
        return self._config.get(PetPromoConsts.IS_ENABLED, False)

    def getUrl(self, petID):
        return self.getPets().get(petID, {}).get(PetPromoConsts.URL, '')

    def getSources(self, petID):
        return self.getPets().get(petID, {}).get(PetPromoConsts.SOURCES, set())

    def getShopUrl(self, petID):
        return self.getPets().get(petID, {}).get(PetPromoConsts.SHOP_URL, '')

    def getAvailablePets(self, unlockedPetsIDs):
        return [ petID for petID in self.getPets().iterkeys() if petID not in unlockedPetsIDs ]
