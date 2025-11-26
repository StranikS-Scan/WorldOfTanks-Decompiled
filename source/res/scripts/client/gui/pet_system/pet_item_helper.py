# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/pet_item_helper.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.pet_system.constants import PET_NAME_FORMAT
from skeletons.gui.lobby_context import ILobbyContext
from helpers import dependency
from skeletons.gui.pet_system import IPetSystemController
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.pet_system.requester import PetID

class PetItem(object):
    petController = dependency.descriptor(IPetSystemController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    @classmethod
    def getActivePetID(cls):
        return cls.petController.getActivePet()

    @classmethod
    def getPetsConfig(cls):
        return cls.lobbyContext.getServerSettings().getPetSystemConfig().getPetsConfig()

    @classmethod
    def getDefaultNameId(cls, petId=None):
        petId = petId or cls.getActivePetID()
        return cls.getPetsConfig().getDefaultNameId(petId)

    @classmethod
    def getCurrentNameId(cls, petId=None):
        petId = petId or cls.getActivePetID()
        return cls.petController.getCurrentName(petId)

    @classmethod
    def getIsDefaultNameLocked(cls, petId):
        petId = petId or cls.getActivePetID()
        return cls.getPetsConfig().getIsDefaultNameLocked(petId)

    @classmethod
    def getPetType(cls, petId=None):
        petId = petId or cls.getActivePetID()
        return cls.getPetsConfig().getPetType(petId)

    @classmethod
    def getPetBreed(cls, petId=None):
        petId = petId or cls.getActivePetID()
        return cls.getPetsConfig().getPetBreed(petId)

    @classmethod
    def getPetName(cls, nameID):
        return backport.text(R.strings.pet_names.dyn(PET_NAME_FORMAT.format(nameID))())


class PromoPetItem(PetItem):

    @classmethod
    def getPetsPromoConfig(cls):
        return cls.lobbyContext.getServerSettings().getPetSystemConfig().getPetPromoConfig()

    @classmethod
    def getCurrentNameId(cls, petId=None):
        return cls.getDefaultNameId(petId)

    @classmethod
    def getPromoUrl(cls, petId):
        return cls.getPetsPromoConfig().getUrl(petId)

    @classmethod
    def getPromoShopUrl(cls, petId):
        return cls.getPetsPromoConfig().getShopUrl(petId)
