# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/pet_animation_helper.py
from gui.pet_system.synergy_helper import SynergyItem
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.shared.utils import IHangarSpace
from helpers import dependency
from Event import Event, EventManager
from gui.pet_system.constants import PetPlaceName
from pet_system_common.pet_constants import AnimationStateName, PetStateBehavior, PetStaticTrigger, PetTrigger, StorageStaticTrigger
from skeletons.gui.pet_system import IPetSystemController
PET_MOVE_TO_STORAGE_TIME_DELAY = 1
PET_LOGIN_TIME_DELAY = 0

class PetPrefabProxy(CallbackDelayer):
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, ctrl):
        super(PetPrefabProxy, self).__init__()
        self._ctrl = ctrl
        self.__em = EventManager()
        self.onUpdatePetPlace = Event(self.__em)
        self.onUpdatePetPrefabState = Event(self.__em)
        self.onTrigger = Event(self.__em)
        self.onUpdatePetStaticTrigger = Event(self.__em)
        self.onUpdatePetSynergy = Event(self.__em)
        self.__isAFKState = False

    def clear(self):
        self.__em.clear()
        self.clearCallbacks()
        self.__isAFKState = False

    @property
    def placeName(self):
        return self.getPlaceName()

    @property
    def petPrefabState(self):
        if self._ctrl.isPetInHangarPromoting():
            return AnimationStateName.PROMOTION
        if self._ctrl.getStateBehavior() == PetStateBehavior.BASIC and not self._ctrl.isInStorage:
            return AnimationStateName.DEFAULT
        return AnimationStateName.HIDDEN if self._ctrl.getStateBehavior() == PetStateBehavior.HIDDEN else AnimationStateName.DISABLED

    @property
    def petStaticTrigger(self):
        if not self._ctrl.isInStorage:
            if self._ctrl.getActiveEvent():
                return PetStaticTrigger.EVENT
            if self.__isAFKState:
                return PetStaticTrigger.AFK
        return PetStaticTrigger.IDLE

    @property
    def petSynergyLevel(self):
        return SynergyItem.getSynergyLevel(self._ctrl.getPetIDInHangar())

    def cameraIdle(self, isAFK):
        self.__isAFKState = isAFK
        self.setPetStaticTrigger(self.petStaticTrigger)

    def getPlaceName(self, isInStorage=None):
        if isInStorage is None:
            isInStorage = self._ctrl.isInStorage
        return PetPlaceName.STORAGE if isInStorage or self._ctrl.getStateBehavior() == PetStateBehavior.HIDDEN else PetPlaceName.DEFAULT

    def setPlaceName(self, placeName):
        self.onUpdatePetPlace(placeName)

    def setPrefabStateName(self, state):
        self.onUpdatePetPrefabState(state)

    def setPetStaticTrigger(self, staticTrigger):
        self.onUpdatePetStaticTrigger(staticTrigger)

    def setSynergyLevel(self, synergyLevel):
        self.onUpdatePetSynergy(synergyLevel)

    def triggerAnimation(self, event):
        self.onTrigger(event)

    def login(self):

        def onLoginFunc():
            if self.petStaticTrigger != PetStaticTrigger.EVENT:
                self.triggerAnimation(PetTrigger.LOGIN)

        self.delayCallback(PET_LOGIN_TIME_DELAY, onLoginFunc)

    def gotMedal(self):
        if not self._ctrl.isInStorage:
            self.triggerAnimation(PetTrigger.MEDAL)

    def firstClick(self):
        self.triggerAnimation(PetTrigger.FIRST_CLICK)

    def moveToStorage(self):
        self.setPetStaticTrigger(self.petStaticTrigger)
        self.setPrefabStateName(self.petPrefabState)
        prevPlaceName = self.getPlaceName(False)
        if prevPlaceName != self.placeName:
            self.delayCallback(PET_MOVE_TO_STORAGE_TIME_DELAY, self.__onMoveToStorage)

    def exitStorage(self):
        if not self._ctrl.isEnabled:
            return
        self.setPetStaticTrigger(self.petStaticTrigger)
        self.setPrefabStateName(self.petPrefabState)
        prevPlaceName = self.getPlaceName(True)
        self.triggerAnimation(PetTrigger.FROM_STORAGE)
        if prevPlaceName != self.placeName:
            self.setPlaceName(self.placeName)

    def stopMoveToStorage(self):
        self.stopCallback(self.__onMoveToStorage)

    def __onMoveToStorage(self):
        self.triggerAnimation(PetTrigger.TO_STORAGE)
        self.setPlaceName(self.placeName)

    def openEventScreen(self):
        self.triggerAnimation(PetTrigger.TO_EVENT_SCREEN)

    def closeEventScreen(self):
        if not self._ctrl.isEnabled:
            return
        self.triggerAnimation(PetTrigger.FROM_EVENT_SCREEN)

    def updateClientDiff(self):
        self.setPrefabStateName(self.petPrefabState)
        self.setPlaceName(self.placeName)
        self.setPetStaticTrigger(self.petStaticTrigger)
        self.setSynergyLevel(self.petSynergyLevel)

    def onServerSettingsChanged(self):
        if self._ctrl.isEnabled:
            self.setPrefabStateName(self.petPrefabState)
            self.setPlaceName(self.placeName)
            self.setPetStaticTrigger(self.petStaticTrigger)
            self.setSynergyLevel(self.petSynergyLevel)


class StoragePrefabProxy(object):

    def __init__(self, ctrl):
        self._ctrl = ctrl
        self.__em = EventManager()
        self.onUpdateStorageStaticTrigger = Event(self.__em)

    def clear(self):
        self.__em.clear()

    @property
    def storageStaticTrigger(self):
        if not self._ctrl.isEnabled:
            return StorageStaticTrigger.EMPTY
        return StorageStaticTrigger.DISABLED if not self._ctrl.haveActivePromotion() and not self._ctrl.getActivePet() else StorageStaticTrigger.IDLE

    def setStorageStaticTrigger(self, staticTrigger):
        self.onUpdateStorageStaticTrigger(staticTrigger)

    def updateClientDiff(self):
        self.setStorageStaticTrigger(self.storageStaticTrigger)

    def onServerSettingsChanged(self):
        self.setStorageStaticTrigger(self.storageStaticTrigger)
