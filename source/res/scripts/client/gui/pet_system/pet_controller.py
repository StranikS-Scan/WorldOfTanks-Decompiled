# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/pet_controller.py
from __future__ import absolute_import
import random
import BigWorld
import SoundGroups
from adisp import adisp_process
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from chat_shared import SYS_MESSAGE_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.lobby.pet_system.states import PetEventFullscreenWindowState, PetStorageObserver
from gui.pet_system.processor import FirstClickSynergyProcessor, PetEventOpenProcessor, PetPurchaseProcessor
from gui.pet_system.pet_animation_helper import PetPrefabProxy, StoragePrefabProxy
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.pet_system.requester import INVALID_EVENT_ID, INVALID_PET_ID
from messenger.proto.events import g_messengerEvents
from skeletons.gui.game_control import IFadingController, IHangarLoadingController, IHangarGuiController
from skeletons.gui.shared.utils import IHangarSpace
from gui.pet_system.constants import PS_PDATA_KEYS
from skeletons.gui.shared import IItemsCache
from gui.pet_system.synergy_helper import SynergyItem
from PlayerEvents import g_playerEvents
from gui.shared.event_dispatcher import openPetEventFullscreenWindow, showPetEventView
from pet_system_common import pet_constants
from pet_system_common.pet_constants import PETS_SYSTEM_PDATA_KEY, PetAchievementAnimation, PetPromoConsts, PetSystemGeneralConsts, PetHangarObject, PetSounds, PetStateBehavior
from skeletons.gui.lobby_context import ILobbyContext
from helpers import dependency
from Event import Event, EventManager
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.gui.pet_system import IPetSystemController
from wg_async import wg_async

class PetSystemController(IGlobalListener, IPetSystemController):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    hangarSpace = dependency.descriptor(IHangarSpace)
    __hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    fadeManager = dependency.descriptor(IFadingController)

    def __init__(self):
        super(PetSystemController, self).__init__()
        self.__em = EventManager()
        self.onUpdateActivePet = Event(self.__em)
        self.onUpdatePrefab = Event(self.__em)
        self.onUpdateEventData = Event(self.__em)
        self.onUpdateUnlockedPetsIDs = Event(self.__em)
        self.onUpdateAppliedBonus = Event(self.__em)
        self.onUpdateSynergy = Event(self.__em)
        self.onUpdateCanInteractInHangar = Event(self.__em)
        self.__petProxy = PetPrefabProxy(self)
        self.__storageProxy = StoragePrefabProxy(self)
        self.lsmObserver = None
        self.__petInHangar = None
        self.__medalReceived = False
        self.__isPetObjectPresenterOpen = 0
        return

    def init(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.handleChat

    def fini(self):
        self.__em.clear()
        self.__storageProxy.clear()
        self.__removeListeners()
        self.lsmObserver = None
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.handleChat
        return

    @property
    def petProxy(self):
        return self.__petProxy

    @property
    def storageProxy(self):
        return self.__storageProxy

    @property
    def isInStorage(self):
        return False if not self.lsmObserver else self.lsmObserver.currentState

    @property
    def isInEventFulscreen(self):
        lsm = getLobbyStateMachine()
        return lsm.getStateByCls(PetEventFullscreenWindowState).isEntered()

    @property
    def petInHangar(self):
        return self.__petInHangar

    @property
    def canInteractInHangar(self):
        return bool(self.__isPetObjectPresenterOpen)

    @classmethod
    def getSystemConfig(cls):
        return cls.lobbyContext.getServerSettings().getPetSystemConfig()

    @classmethod
    def getPetsConfig(cls):
        return cls.getSystemConfig().getPetsConfig()

    @classmethod
    def getBonusConfig(cls):
        return cls.getSystemConfig().getPetBonusConfig()

    @classmethod
    def getGeneralConfig(cls):
        return cls.getSystemConfig().getPetGeneralConfig()

    @classmethod
    def getPetEventConfig(cls):
        return cls.getSystemConfig().getPetEventConfig()

    @classmethod
    def getPetsPromoConfig(cls):
        return cls.getSystemConfig().getPetPromoConfig()

    @classmethod
    def getPetSynergyConfig(cls):
        return cls.getSystemConfig().getPetSynergyConfig()

    @property
    def isEnabled(self):
        return self.getGeneralConfig().isEnabled

    @property
    def commandSender(self):
        return BigWorld.player().petSystem

    def addPetDev(self, petID):
        if not self.isEnabled:
            return
        self.commandSender.addPetDev(petID)

    @adisp_process
    def buyPet(self, petID):
        if not self.isEnabled:
            return
        yield PetPurchaseProcessor(petID).request()

    def changePet(self, petID):
        if not self.isEnabled:
            return
        self.__petInHangar = petID
        self.onUpdatePrefab(petID)

    def selectActivePet(self, petID):
        if not self.isEnabled:
            return
        self.commandSender.selectActivePet(petID)

    def activateEvent(self, eventID):
        if not self.isEnabled:
            return
        self.commandSender.activateEventDev(eventID)

    def selectPetStateBehavior(self, stateBehavior):
        if not self.isEnabled:
            return
        self.commandSender.selectPetStateBehavior(stateBehavior)

    def selectPetName(self, petID, nameID):
        if not self.isEnabled:
            return
        self.commandSender.selectPetName(petID, nameID)

    @property
    def requester(self):
        return self.itemsCache.items.petSystem

    def getActivePet(self):
        if not self.isEnabled:
            return INVALID_PET_ID
        petID = self.requester.getActivePetID()
        return petID

    def getActiveEvent(self):
        return INVALID_EVENT_ID if not self.isEnabled else self.requester.getActiveEventID()

    def isFirstClickEnable(self):
        return False if not self.isEnabled else not self.isPetInHangarPromoting() and SynergyItem.isFirstClickSynergyAvailable()

    def getUnlockedPets(self):
        return list() if not self.isEnabled else self.requester.getUnlockedPetIDs()

    def getStateBehavior(self):
        return pet_constants.PetStateBehavior.BASIC if not self.isEnabled else self.requester.getStateBehavior()

    def getCurrentName(self, petID):
        return 0 if not self.isEnabled else self.requester.getSelectedName(petID)

    def addSynergyDev(self, synergyPoints, petID=None):
        if not self.isEnabled:
            return
        petID = petID or self.getActivePet()
        self.commandSender.addSynergyDev(petID, synergyPoints)

    def getAvailableNames(self):
        if not self.isEnabled:
            return set()
        unlockedPetIDs = self.getUnlockedPets()
        return self.getPetsConfig().getAvailableNames(unlockedPetIDs)

    def getAvailableBonuses(self):
        if not self.isEnabled:
            return set()
        unlockedPetIDs = self.getUnlockedPets()
        return self.getPetsConfig().getAvailableBonuses(unlockedPetIDs)

    def getPetIDInHangar(self, reset=False):
        if not self.isEnabled:
            self.__petInHangar = None
            return
        elif self.getActivePet() == INVALID_PET_ID:
            if not self.__petInHangar or reset:
                return self.__getRandomPromoPetID()
            return self.__petInHangar
        else:
            self.__petInHangar = self.getActivePet()
            return self.__petInHangar

    def isPetInHangarPromoting(self):
        return self.isEnabled and self.__petInHangar not in self.getUnlockedPets()

    def haveActivePromotion(self):
        return self.isEnabled and self.getPetsPromoConfig().isEnabled()

    def getUnlockedAndPromoPets(self):
        if not self.isEnabled:
            return list()
        petIDs = self.getUnlockedPets()
        return petIDs if not self.getPetsPromoConfig().isEnabled() else petIDs + self.getPetsPromoConfig().getAvailablePets(petIDs)

    def showEventView(self, isFullScreen=False):
        if not self.isEnabled:
            return
        eventID = self.getActiveEvent()
        if eventID:
            self.__openEvent(isFullScreen)

    @adisp_process
    def __openEvent(self, isFullScreen):
        result = yield PetEventOpenProcessor().request()
        if result:
            if result.success:
                ctx = {'eventID': result.auxData.get('eventID'),
                 'rewards': result.auxData.get('bonus')}
                if isFullScreen:
                    openPetEventFullscreenWindow(ctx)
                else:
                    showPetEventView(ctx)

    @adisp_process
    def sendFirstClick(self):
        if not self.isEnabled or not self.isFirstClickEnable():
            return
        result = yield FirstClickSynergyProcessor(self.getActivePet()).request()
        if result and result.success:
            self.petProxy.firstClick()

    def onLobbyInited(self, event):
        self.__addListeners()

    def checkBonusCapsForPetBonus(self):
        return self.__hangarGuiCtrl.dynamicEconomics.checkCurrentBonusCaps(ARENA_BONUS_TYPE_CAPS.PET_SYSTEM_BONUSES)

    def __showMedalAnimation(self, event):
        if not self.isEnabled:
            return
        if self.__medalReceived:
            self.petProxy.gotMedal()
            self.__medalReceived = False

    def _onHangarLoadedAfterLogin(self, *args):
        if not self.isEnabled:
            return
        self.petProxy.login()

    def onAccountBecomeNonPlayer(self):
        self.__removeListeners()
        self.__isPetObjectPresenterOpen = 0
        g_eventBus.removeListener(events.PetSystemEvent.PET_OBJECT_PRESENTER_LOADING, self.__onPetObjectPresenterLoading, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.PetSystemEvent.PET_OBJECT_PRESENTER_CLOSING, self.__onPetObjectPresenterClosing, scope=EVENT_BUS_SCOPE.LOBBY)

    def onAccountBecomePlayer(self):
        g_eventBus.addListener(events.PetSystemEvent.PET_OBJECT_PRESENTER_LOADING, self.__onPetObjectPresenterLoading, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.PetSystemEvent.PET_OBJECT_PRESENTER_CLOSING, self.__onPetObjectPresenterClosing, scope=EVENT_BUS_SCOPE.LOBBY)

    def onDisconnected(self):
        self.__medalReceived = False
        self.__petInHangar = None
        self.__removeListeners()
        return

    def onStorageEntered(self):
        self.petProxy.moveToStorage()

    @wg_async
    def onStorageExited(self):
        self.petProxy.stopMoveToStorage()
        yield self.fadeManager.show(WindowLayer.OVERLAY)
        try:
            self.petProxy.exitStorage()
            if self.isEnabled:
                self.changePet(self.getPetIDInHangar())
        finally:
            yield self.fadeManager.hide(WindowLayer.OVERLAY)

    def __addListeners(self):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.lsmObserver = PetStorageObserver()
        g_eventBus.addListener(events.PetSystemEvent.MEDAL_ANIMATION_SHOW, self.__showMedalAnimation, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.PetObjectHoverEvent.HOVER_IN, self.__playSound, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.addListener(CameraRelatedEvents.IDLE_CAMERA, self.__cameraIdle)
        lsm = getLobbyStateMachine()
        self.__hangarLoadingController.onHangarLoadedAfterLogin += self._onHangarLoadedAfterLogin
        if lsm:
            lsm.connect(self.lsmObserver)
            self.lsmObserver.onStorageEntered += self.onStorageEntered
            self.lsmObserver.onStorageExited += self.onStorageExited

    def handleChat(self, *ctx):
        if not self.isEnabled:
            return
        else:
            _, message = ctx
            if message is not None and message.type == SYS_MESSAGE_TYPE.battleResults.index() and message.data:
                popUpRecords = message.data.get('popUpRecords', {})
                for record in popUpRecords:
                    if record[0] == PetAchievementAnimation.Warrior:
                        self.__medalReceived = True
                        break

            return

    def __removeListeners(self):
        self.__petProxy.clear()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__hangarLoadingController.onHangarLoadedAfterLogin -= self._onHangarLoadedAfterLogin
        g_eventBus.removeListener(events.PetSystemEvent.MEDAL_ANIMATION_SHOW, self.__showMedalAnimation, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.PetObjectHoverEvent.HOVER_IN, self.__playSound, scope=EVENT_BUS_SCOPE.DEFAULT)
        g_eventBus.removeListener(CameraRelatedEvents.IDLE_CAMERA, self.__cameraIdle)
        lsm = getLobbyStateMachine()
        if lsm and self.lsmObserver:
            lsm.disconnect(self.lsmObserver)
            self.lsmObserver.clear()
            self.lsmObserver = None
        return

    def __onServerSettingsChanged(self, diff):
        if pet_constants.PETS_SYSTEM_CONFIG in diff:
            sysDiff = diff[pet_constants.PETS_SYSTEM_CONFIG]
            isEnabled = sysDiff.get(PetSystemGeneralConsts.CONFIG_NAME, {}).get(PetSystemGeneralConsts.ENABLED)
            if isEnabled is not None and not isEnabled:
                self.__petInHangar = None
                self.__medalReceived = False
            elif PetPromoConsts.CONFIG_NAME in sysDiff:
                if sysDiff[PetPromoConsts.CONFIG_NAME].get(PetPromoConsts.IS_ENABLED, False):
                    self.__petInHangar = None
            self.storageProxy.onServerSettingsChanged()
            self.petProxy.onServerSettingsChanged()
        return

    def __onClientUpdated(self, diff, _):
        if not self.isEnabled:
            return
        if PETS_SYSTEM_PDATA_KEY in diff:
            petSystemDiff = diff[PETS_SYSTEM_PDATA_KEY]
            if not {PS_PDATA_KEYS.UNLOCKED_PETS_IDS,
             PS_PDATA_KEYS.EVENTS_DATA,
             PS_PDATA_KEYS.ACTIVE_STATE_BEHAVIOR,
             PS_PDATA_KEYS.STORAGE}.isdisjoint(petSystemDiff.keys()):
                self.petProxy.updateClientDiff()
            if PS_PDATA_KEYS.ACTIVE_PETID in petSystemDiff:
                activePetId = petSystemDiff[PS_PDATA_KEYS.ACTIVE_PETID]
                self.changePet(self.getPetIDInHangar(reset=True))
                self.onUpdateActivePet(activePetId)
            if PS_PDATA_KEYS.UNLOCKED_PETS_IDS in petSystemDiff:
                self.onUpdateUnlockedPetsIDs()
            if PS_PDATA_KEYS.EVENTS_DATA in petSystemDiff or PS_PDATA_KEYS.ACTIVE_STATE_BEHAVIOR in petSystemDiff:
                self.storageProxy.updateClientDiff()
            if PS_PDATA_KEYS.EVENTS_DATA in petSystemDiff:
                self.onUpdateEventData()
            if PS_PDATA_KEYS.BONUS in petSystemDiff and PS_PDATA_KEYS.APPLIED_BONUSES in petSystemDiff[PS_PDATA_KEYS.BONUS]:
                self.onUpdateAppliedBonus()
            if PS_PDATA_KEYS.STORAGE in petSystemDiff:
                petStorages = petSystemDiff[PS_PDATA_KEYS.STORAGE].values()
                if any((PS_PDATA_KEYS.SYNERGY_STORAGE in petStorage for petStorage in petStorages if petStorage is not None)):
                    self.onUpdateSynergy()

    def __getRandomPromoPetID(self):
        if not self.haveActivePromotion():
            self.__petInHangar = None
            return
        else:
            validToBuyPets = self.getPetsPromoConfig().getAvailablePets(self.getUnlockedPets())
            self.__petInHangar = random.choice(validToBuyPets)
            return self.__petInHangar

    def __onPetObjectPresenterLoading(self, _):
        self.__isPetObjectPresenterOpen += 1
        self.onUpdateCanInteractInHangar(self.canInteractInHangar)

    def __onPetObjectPresenterClosing(self, _):
        self.__isPetObjectPresenterOpen -= 1
        self.onUpdateCanInteractInHangar(self.canInteractInHangar)

    def __playSound(self, event):
        hoveredObj = event.ctx.get('objectName')
        hasActiveEvent = self.getActiveEvent() != INVALID_EVENT_ID
        isPetHidden = self.getStateBehavior() == PetStateBehavior.HIDDEN
        if hoveredObj == PetHangarObject.STORAGE:
            if isPetHidden and hasActiveEvent:
                SoundGroups.g_instance.playSound2D(PetSounds.PET_EVENT_HIGHLIGHT)
            else:
                SoundGroups.g_instance.playSound2D(PetSounds.HIGHLIGHT)
        elif hoveredObj == PetHangarObject.PET:
            if hasActiveEvent and not isPetHidden:
                SoundGroups.g_instance.playSound2D(PetSounds.PET_EVENT_HIGHLIGHT)
            elif self.isPetInHangarPromoting():
                SoundGroups.g_instance.playSound2D(PetSounds.HIGHLIGHT)

    def __cameraIdle(self, event):
        isAFKState = event.ctx['started']
        self.petProxy.cameraIdle(isAFKState)
