# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/synergy_helper.py
import typing
from collections import namedtuple
from helpers import dependency
from skeletons.gui.pet_system import IPetSystemController
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
    PetID = int
    Synergy = int
    SynergyLevel = int
SynergyProgress = namedtuple('SynergyProgress', ('cPoints', 'maxPoints'))

class SynergyItem(object):
    petController = dependency.descriptor(IPetSystemController)

    @classmethod
    def getSynergyLevels(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        synergyGroupID = cls.petController.getPetsConfig().getPetSynergyGroupID(petID)
        return cls.petController.getPetSynergyConfig().getSynergyLevels(synergyGroupID)

    @classmethod
    def getSynergyPoints(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        return cls.petController.requester.getSynergyPoints(petID)

    @classmethod
    def getSynergyLevel(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        return cls.petController.requester.getSynergyLevel(petID)

    @classmethod
    def getSynergyProgression(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        return SynergyProgress(cls.getSynergyPoints(petID), cls.getSynergyLevels(petID)[-1])

    @classmethod
    def isMaxSynergyLevel(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        return cls.getSynergyLevel(petID) >= len(cls.getSynergyLevels(petID)) - 1

    @classmethod
    def isFirstClickSynergyAvailable(cls, petID=None):
        petID = petID or cls.petController.getActivePet()
        return petID not in cls.petController.requester.getFirstClickedSynergyPets()
