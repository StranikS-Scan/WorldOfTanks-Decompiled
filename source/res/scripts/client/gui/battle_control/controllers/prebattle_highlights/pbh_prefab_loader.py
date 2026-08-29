# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/prebattle_highlights/pbh_prefab_loader.py
from __future__ import absolute_import
import logging
import CGF
import Math
from enum import Enum
from gui.battle_control.controllers.prebattle_highlights.pbh_helpers import getPbhAnchorData, getPbhPetAnchorGo, getPbhSpacePrefab
from helpers.CallbackDelayer import CallbackDelayer
from helpers import dependency
from pet_system_common.pet_constants import PetsConsts
from skeletons.gui.pet_system import IPetSystemController
from skeletons.gui.battle_session import IBattleSessionProvider
_logger = logging.getLogger(__name__)

class PrefabLoaderStatus(Enum):
    INITIAL = 'initial'
    LOADING = 'loading'
    LOADED = 'loaded'
    FAILED = 'failed'


class PBHPrefabLoader(object):
    __petController = dependency.descriptor(IPetSystemController)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, winnersGetter, sizeGetter):
        self.__winnersGetter = winnersGetter
        self.__sizeGetter = sizeGetter
        self.__callback = None
        self.__prefabStatus = PrefabLoaderStatus.INITIAL
        self.__loadedGo = None
        self.__callbackDelayer = CallbackDelayer()
        return

    @property
    def status(self):
        return self.__prefabStatus

    def loadPBHPrefab(self, callback):
        self.__callback = callback
        anchorData = getPbhAnchorData()
        if anchorData:
            self.__prefabStatus = PrefabLoaderStatus.LOADING
            CGF.loadAndCreatePrefabWithParent(anchorData.prefabPath, anchorData.go, Math.Vector3(0, 0, 0), self.__onPrefabLoaded)
        else:
            self.__prefabStatus = PrefabLoaderStatus.FAILED
            self.__callback()

    def reset(self):
        self.__callbackDelayer.clearCallbacks()
        self.__callback = None
        self.__prefabStatus = PrefabLoaderStatus.INITIAL
        self.__togglePBHSpacePrefab(False)
        if self.__loadedGo:
            self.__loadedGo.destroy()
        self.__loadedGo = None
        return

    def clear(self):
        self.__callback = None
        self.__prefabStatus = None
        self.__winnersGetter = None
        self.__sizeGetter = None
        self.__callbackDelayer.destroy()
        self.__callbackDelayer = None
        self.__togglePBHSpacePrefab(False)
        if self.__loadedGo:
            self.__loadedGo.destroy()
        self.__loadedGo = None
        return

    def __loadPets(self):
        arenaVehicles = self.__sessionProvider.arenaVisitor.getArenaVehicles()
        for idx, data in enumerate(self.__winnersGetter(), 1):
            petID = arenaVehicles.get(data['id']).get('activePetID', 0)
            petPrefabPath = self.__getPetBattlePrefabByID(petID)
            if not petPrefabPath:
                return
            go = getPbhPetAnchorGo(idx, self.__sizeGetter())
            if not go:
                return
            CGF.loadAndCreatePrefabWithParent(petPrefabPath, go, Math.Vector3(0, 0, 0))

    def __onPrefabLoaded(self, objects, queue):
        go = queue.gameObject(objects[0])

        def afterSubmit():

            def afterUpdate():
                self.__loadedGo = go
                self.__prefabStatus = PrefabLoaderStatus.LOADED
                self.__loadPets()
                self.__togglePBHSpacePrefab(True)
                if self.__callback is not None:
                    self.__callback()
                return

            self.__callbackDelayer.delayCallback(0.0, afterUpdate)

        self.__callbackDelayer.delayCallback(0.0, afterSubmit)

    def __getPetBattlePrefabByID(self, petID):
        config = self.__petController.getPetsConfig().getPet(petID)
        return config.get(PetsConsts.PET_BATTLE_PREFAB, '')

    def __togglePBHSpacePrefab(self, activate):
        go = getPbhSpacePrefab()
        if go is None:
            return
        else:
            queue = CGF.CommandQueue(go.spaceID)
            if activate:
                queue.activateGameObject(go)
            else:
                queue.deactivateGameObject(go)
            return
