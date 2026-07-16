# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/cgf_components/pet_place_component.py
import typing
import WWISE
import Math
import CGF
from typing import List
from collections import namedtuple
from functools import partial
from cgf_script.registration import ComponentProperty, registerComponent
from gui.pet_system.constants import PetPlaceName
from helpers import dependency
from pet_system_common import pet_constants
from pet_system_common.pet_constants import PetsConsts, PET_RTPC_DOG_TYPE
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.pet_system import IPetSystemController
if typing.TYPE_CHECKING:
    from typing import Optional

@dependency.replace_none_kwargs(petContoller=IPetSystemController)
def getPetPrefabByID(petID, petContoller=None):
    config = petContoller.getPetsConfig().getPet(petID)
    return config.get(PetsConsts.PET_PREFAB, '')


@registerComponent
class PetPlaceComponent(object):
    domain = CGF.Domain.Client
    editorTitle = 'Pet Place Component'
    group = 'Pets'
    names = {name:name for name in PetPlaceName.ALL}
    placeName = ComponentProperty(type=CGF.PropertyType.String, editorName='place name', value='default', annotations={'comboBox': names})


_ActivePrefabInfo = namedtuple('_ActivePrefabInfo', ['petID', 'prefabGO'])
_LoadingPrefabInfo = namedtuple('_LoadingPrefabInfo', ['prefabPath', 'placeGO', 'petID'])

class PetPrefabSystem(CGF.System):
    petController = dependency.descriptor(IPetSystemController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _activePet = None
    _loadingPet = None
    PlacementActivated = CGF.ActivateReaction(CGF.GameObject, CGF.ReactRw(PetPlaceComponent))
    PlaceIterate = CGF.IterateReaction(CGF.ActiveOnly, CGF.GameObject, CGF.Rw(PetPlaceComponent))
    Reactions = CGF.Reactions(PlacementActivated, PlaceIterate)

    def onMappingLoaded(self):
        self.petController.onUpdatePrefab += self.updateActivePet
        self.petController.petProxy.onUpdatePetPlace += self.onUpdatePetPlace
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def onMappingUnloaded(self):
        self.petController.onUpdatePrefab -= self.updateActivePet
        self.petController.petProxy.onUpdatePetPlace -= self.onUpdatePetPlace
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self._activePet = None
        self._loadingPet = None
        return

    def update(self):
        for go, place in self.reaction(self.PlacementActivated):
            if self._activePet:
                return
            petID = self.petController.getPetIDInHangar()
            if petID is None:
                return
            prefab = getPetPrefabByID(petID)
            if place.placeName == self.petController.petProxy.placeName:
                self._createPet(prefab, go, petID)

        return

    def _createPet(self, prefabPath, placeGO, petID):
        loadingPet = _LoadingPrefabInfo(prefabPath, placeGO, petID)
        if self._loadingPet and self._loadingPet == loadingPet:
            return
        self._loadingPet = loadingPet
        CGF.loadAndCreatePrefabWithParent(prefabPath, placeGO, Math.Vector3(0, 0, 0), partial(self._onPrefabLoaded, loadingPet, petID))
        self._setRTPC(petID)

    def _removePet(self):
        if self._activePet:
            self._activePet.prefabGO.destroy()
            self._activePet = None
        return

    def _setRTPC(self, petID):
        WWISE.WW_setRTCPGlobal(PET_RTPC_DOG_TYPE, petID - 1)

    def _onPrefabLoaded(self, loadingPet, petID, objects, queue):
        if self._loadingPet:
            root = objects[0]
            self._activePet = _ActivePrefabInfo(petID, queue.gameObject(root))
            if self._loadingPet != loadingPet:
                self._activePet = None
                return False
            self._loadingPet = None
        else:
            return False
        return True

    def updateActivePet(self, petID):
        if self._activePet and self._activePet.petID == petID:
            return
        elif petID is None:
            self._removePet()
            return
        else:
            prefab = getPetPrefabByID(petID)
            if not prefab:
                return
            self._removePet()
            for placeGO, placeComp in self.reaction(self.PlaceIterate):
                if placeComp.placeName == self.petController.petProxy.placeName:
                    self._createPet(prefab, placeGO, petID)
                    return

            return

    def __onServerSettingsChanged(self, diff):
        if pet_constants.PETS_SYSTEM_CONFIG in diff:
            if not self.petController.isEnabled:
                self._removePet()
            elif not self.petController.haveActivePromotion() and not self.petController.getActivePet():
                self._removePet()
            else:
                self.updateActivePet(self.petController.getPetIDInHangar())

    def onUpdatePetPlace(self, petPlaceName):
        if not self._activePet or not self._activePet.prefabGO:
            return
        parent = self.hierarchy.getParent(self._activePet.prefabGO)
        for placeGO, placeComp in self.reaction(self.PlaceIterate):
            if placeComp.placeName == petPlaceName:
                if parent == placeGO:
                    return
                self._activePet.prefabGO.findWrite(CGF.HierarchyComponent).parent = self.gom.gameObjectUuid(placeGO)
