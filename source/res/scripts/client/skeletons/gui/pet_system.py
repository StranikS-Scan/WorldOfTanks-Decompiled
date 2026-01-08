# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/pet_system.py
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from account_helpers.pet_system import PetSystem
    from gui.pet_system.requester import PetRequesterRequester
    from gui.pet_system.pet_animation_helper import PetPrefabProxy, StoragePrefabProxy
    from pet_system_common.EventConfig import EventConfig
    from pet_system_common.GeneralConfig import GeneralConfig
    from pet_system_common.PetConfig import PetConfig
    from pet_system_common.BonusConfig import BonusConfig
    from pet_system_common.PetPromoConfig import PetPromoConfig
    from pet_system_common.PetSynergyConfig import PetSynergyConfig
    from typing import List, Set, Optional
    from Event import Event
    EventID = str
    PetID = int
    NameID = int
    BonusID = int
    PlaceName = str
    StaticTrigger = int
    Synergy = int
    StateBehavior = int

class IPetSystemController(IGameController):
    onUpdateActivePet = None
    onUpdatePrefab = None
    onUpdateEventData = None
    onUpdateUnlockedPetsIDs = None
    onUpdateAppliedBonus = None
    onUpdateSynergy = None
    onUpdateCanInteractInHangar = None

    @property
    def petProxy(self):
        raise NotImplementedError

    @property
    def storageProxy(self):
        raise NotImplementedError

    @property
    def isInStorage(self):
        raise NotImplementedError

    @property
    def isInEventFulscreen(self):
        raise NotImplementedError

    @property
    def petInHangar(self):
        raise NotImplementedError

    @property
    def canInteractInHangar(self):
        raise NotImplementedError

    @property
    def commandSender(self):
        raise NotImplementedError

    @property
    def requester(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    def getActiveEvent(self):
        raise NotImplementedError

    def isFirstClickEnable(self):
        raise NotImplementedError

    def getPetsConfig(self):
        raise NotImplementedError

    def getBonusConfig(self):
        raise NotImplementedError

    def getGeneralConfig(self):
        raise NotImplementedError

    def getPetEventConfig(self):
        raise NotImplementedError

    def getPetsPromoConfig(self):
        raise NotImplementedError

    def getPetSynergyConfig(self):
        raise NotImplementedError

    def onStorageEntered(self):
        pass

    def onStorageExited(self):
        pass

    def addPetDev(self, petID):
        raise NotImplementedError

    def buyPet(self, petID):
        raise NotImplementedError

    def changePet(self, petID):
        raise NotImplementedError

    def selectActivePet(self, petID):
        raise NotImplementedError

    def selectPetStateBehavior(self, stateBehavior):
        raise NotImplementedError

    def selectPetName(self, petID, nameID):
        raise NotImplementedError

    def showEventView(self, isFullScreen=False):
        raise NotImplementedError

    def sendFirstClick(self):
        raise NotImplementedError

    def getActivePet(self):
        raise NotImplementedError

    def getUnlockedPets(self):
        raise NotImplementedError

    def getAvailableNames(self):
        raise NotImplementedError

    def getAvailableBonuses(self):
        raise NotImplementedError

    def getPetIDInHangar(self):
        raise NotImplementedError

    def isPetInHangarPromoting(self):
        raise NotImplementedError

    def getStateBehavior(self):
        raise NotImplementedError

    def addSynergyDev(self, synergyPoints, petID=None):
        raise NotImplementedError

    def haveActivePromotion(self):
        raise NotImplementedError

    def getUnlockedAndPromoPets(self):
        raise NotImplementedError

    def checkBonusCapsForPetBonus(self):
        raise NotImplementedError
