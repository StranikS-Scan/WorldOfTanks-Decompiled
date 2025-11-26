# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/pet_ui_settings.py
import typing
from copy import deepcopy
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PetSystem
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events as events_constants
from gui.shared import g_eventBus
if typing.TYPE_CHECKING:
    from typing import Set
    PetID = int
    NameID = int
    SynergyLevel = int

class PetUISettings(object):

    @classmethod
    def getSeenPetNameIDs(cls):
        return cls._getSetting(PetSystem.SEEN_PET_NAME_IDS)

    @classmethod
    def setSeenPetNameIDs(cls, seenPetNames):
        cls._setSetting(PetSystem.SEEN_PET_NAME_IDS, seenPetNames)

    @classmethod
    def getLastSeenSynergyLevel(cls, petID):
        return cls._getSetting(PetSystem.SEEN_PET_LEVELS).get(petID, 0)

    @classmethod
    def setLastSeenSynergyLevel(cls, petID, level):
        seenPetLevels = cls._getSetting(PetSystem.SEEN_PET_LEVELS)
        if seenPetLevels.get(petID, 0) == level:
            return
        seenPetLevels[petID] = level
        cls._setSetting(PetSystem.SEEN_PET_LEVELS, seenPetLevels)
        g_eventBus.handleEvent(events_constants.PetSystemEvent(events_constants.PetSystemEvent.LAST_SEEN_SYNERGY_LEVEL_UPDATED), scope=EVENT_BUS_SCOPE.LOBBY)

    @classmethod
    def getSeenInStoragePetIDs(cls):
        return cls._getSetting(PetSystem.SEEN_IN_STORAGE_PET_IDS)

    @classmethod
    def setSeenInStoragePetIDs(cls, seenPetIDs):
        if cls._getSetting(PetSystem.SEEN_IN_STORAGE_PET_IDS) == seenPetIDs:
            return
        cls._setSetting(PetSystem.SEEN_IN_STORAGE_PET_IDS, seenPetIDs)
        g_eventBus.handleEvent(events_constants.PetSystemEvent(events_constants.PetSystemEvent.SEEN_IN_STORAGE_PET_IDS_UPDATED), scope=EVENT_BUS_SCOPE.LOBBY)

    @classmethod
    def getSeenPromoPetIDs(cls):
        return cls._getSetting(PetSystem.SEEN_PROMO_PET_IDS)

    @classmethod
    def addSeenPromoPetID(cls, seenPetID):
        seenPetIDs = cls._getSetting(PetSystem.SEEN_PROMO_PET_IDS)
        seenPetIDs.add(seenPetID)
        cls._setSetting(PetSystem.SEEN_PROMO_PET_IDS, seenPetIDs)

    @classmethod
    def _setSetting(cls, settingName, settingValue):
        settings = AccountSettings.getSettings(PetSystem.SETTINGS)
        settings.update({settingName: settingValue})
        AccountSettings.setSettings(PetSystem.SETTINGS, settings)

    @classmethod
    def _getSetting(cls, settingName):
        return AccountSettings.getSettings(PetSystem.SETTINGS).get(settingName, deepcopy(AccountSettings.getSettingsDefault(PetSystem.SETTINGS)[settingName]))
