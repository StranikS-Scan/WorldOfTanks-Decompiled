# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HalloweenSupplyDrop.py
from ClientSelectableCameraObject import ClientSelectableCameraObject, CameraMovementStates
from halloween_shared import EVENT_STATE, SUPPLY_DROP_TOKEN_PREFIX, SUPPLY_DROP_LEVEL_BASIC, SUPPLY_DROP_LEVEL_ELITE, HALLOWEEN_SUPPLY_DROP_SELECTIONID_PREFIX
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from gui import DialogsInterface
from HangarVehicle import HangarVehicle
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR
import ResMgr
import SoundGroups
import BigWorld
from functools import partial
from gui.Scaleform.Waiting import Waiting
import AccountCommands
from gui.shared.utils.HangarSpace import g_hangarSpace
from skeletons.gui.game_control import IEventBattlesController
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
_HALLOWEEN_CONFIG_FILE = 'scripts/halloweenhangar.xml'

class HSDBoxState:
    HIDDEN = 1
    APPEARANCE = 2
    ON_SCENE = 4
    OPENING = 8
    AWAITING_CLAIM_RESPONSE = 16
    AWARD_UI_SHOWN = 32
    CLAIM_SUCCESS = 64
    DONE = 128


class HalloweenSupplyDrop(ClientSelectableCameraObject):
    CLAIM_TIMEOUT_SECS = 18.0
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(HalloweenSupplyDrop, self).__init__()
        self.__action = None
        self.__cachedSounds = {}
        self.__vfxModelName = None
        self.__vfxModel = None
        self.customBspModelName = ''
        self.__searchStr = ''
        self.__readSupplyDropData()
        self.__boxState = HSDBoxState.HIDDEN
        self.__animLengths = None
        self.__effectsTimeLine = None
        self.__effectsPlayers = []
        self.__readEffects()
        self.__readAnims()
        self.__isAvailable = False
        self.__inProgress = False
        self.__inSquad = False
        self.__eventActive = False
        self.clientHalloween = None
        self.dropID = -1
        self.highestdropID = -1
        return

    def onEnterWorld(self, prereqs):
        super(HalloweenSupplyDrop, self).onEnterWorld(prereqs)
        if self.__vfxModelName is not None:
            prereqs = [self.__vfxModelName]
            loadFunc = partial(self.__vfxModelLoaded, modelName=self.__vfxModelName)
            BigWorld.loadResourceListBG(list(prereqs), loadFunc)
        self.clientHalloween = BigWorld.player().halloween
        self.clientHalloween.onInventoryChanged += self.__delayedUpdateSupplyDropStatus
        self.eventBattlesCtrl.onSquadStatusChanged += self.__updateSquadSettings
        self.clientHalloween.onGlobalDataChanged += self.__onEventsDataChanged
        self.__onEventsDataChanged()
        self.__hideAndDisable()
        self.__fireSupplyDropLeavingEvent()
        return

    def goBackToTank(self, callbackSuccess=False):
        self.toggleCameraMovement(True)
        for v in ClientSelectableCameraObject.allCameraObjects:
            if isinstance(v, HangarVehicle):
                ClientSelectableCameraObject.switchCamera(v, self.__updateAtTank)
                self.__fireSupplyDropLeavingEvent()
                return

        ClientSelectableCameraObject.switchCamera(None, self.__updateAtTank)
        self.__fireSupplyDropLeavingEvent()
        return

    def receivedSupplyDrop(self, success):
        if self.__boxState == HSDBoxState.AWARD_UI_SHOWN:
            self.setBoxState(HSDBoxState.CLAIM_SUCCESS)

    def stopWaiting(self):
        Waiting.hide(self.__searchStr)
        self.__searchStr = ''

    def isWaiting(self):
        return bool(self.__searchStr)

    def shownAwardPopup(self):
        self.stopWaiting()
        self.setBoxState(HSDBoxState.AWARD_UI_SHOWN)
        self.__playSFX('supply_drop_claim')

    def onLeaveWorld(self):
        if self.isWaiting():
            self.stopWaiting()
        self.clientHalloween.onInventoryChanged -= self.__delayedUpdateSupplyDropStatus
        self.eventBattlesCtrl.onSquadStatusChanged -= self.__updateSquadSettings
        self.clientHalloween.onGlobalDataChanged -= self.__onEventsDataChanged
        for effect in self.__effectsPlayers:
            effect[1].stop()

        self.__effectsPlayers = None
        if self.__vfxModel:
            BigWorld.delModel(self.__vfxModel)
            self.__vfxModel = None
        super(HalloweenSupplyDrop, self).onLeaveWorld()
        return

    def setBoxState(self, newState):
        LOG_DEBUG_DEV('CAHSD: Update box state from ' + str(self.__boxState) + ' to ' + str(newState))
        oldState = self.__boxState
        self.__boxState = newState
        if oldState == newState:
            return
        if newState == HSDBoxState.APPEARANCE:
            self.__startAppearance()
        elif newState == HSDBoxState.ON_SCENE:
            self.__showAndEnable()
        elif newState == HSDBoxState.OPENING:
            self.__startOpening()
        elif newState == HSDBoxState.AWAITING_CLAIM_RESPONSE:
            self.__waitingState()
        elif newState == HSDBoxState.DONE:
            self.__startDone()
        elif newState == HSDBoxState.CLAIM_SUCCESS:
            self.__updateSupplyDropStatus()

    def onClicked(self, cameraCallback=None):
        loadFunc = partial(self.claimSupplyDrop)
        if self.enabled:
            super(HalloweenSupplyDrop, self).onClicked(loadFunc)
            self.__fireEvent(events.SupplyDropEvent(events.SupplyDropEvent.SUPPLY_DROP_CLICKED))

    def delayClick(self):
        self.delayCallback(1.0, self.onClicked)

    def claimSupplyDrop(self):
        self.toggleCameraMovement(False)
        self.setBoxState(HSDBoxState.OPENING)

    def enable(self, enabled, clear=False):
        if self.state == CameraMovementStates.ON_OBJECT or self.__boxState & (HSDBoxState.DONE | HSDBoxState.CLAIM_SUCCESS) and enabled:
            return
        if not (enabled and self.__inSquad):
            super(HalloweenSupplyDrop, self).enable(enabled)

    def clientOpenDropCallback(self, requestID, resultID, errorStr, ext):
        if resultID is not AccountCommands.RES_SUCCESS:
            self.stopWaiting()
            self.setBoxState(HSDBoxState.ON_SCENE)
            DialogsInterface.showI18nInfoDialog('halloween/supply_drop/claim/failed', self.goBackToTank, None)
            LOG_DEBUG_DEV('CAHSD: OPEN ERROR - ' + str(resultID) + ' - ' + errorStr)
        else:
            LOG_DEBUG_DEV('CAHSD: OPEN RESPONSE - SUCCESS')
        return

    def highlight(self, show, colorOverride=0):
        super(HalloweenSupplyDrop, self).highlight(show)
        if show:
            self.__playSFX('supply_drop_mouseover')

    def onDeselect(self, newSelectedObject=None):
        super(HalloweenSupplyDrop, self).onDeselect(newSelectedObject)
        self.__updateSupplyDropStatus()
        self.__fireSupplyDropLeavingEvent()
        return False

    def __fireEvent(self, event):
        g_eventBus.handleEvent(event, scope=EVENT_BUS_SCOPE.LOBBY)

    def __fireSupplyDropLeavingEvent(self):
        self.__fireEvent(events.SupplyDropEvent(events.SupplyDropEvent.SUPPLY_DROP_LEAVING))

    def __onEventsDataChanged(self):
        """
            Run once at startup of the box and again whenevever player's client is updated, we ensure the box is
            only operable when the event state is active.
        
            If the event deactivates when the box is already up, hide it.
        
            If the event reactivates when the player is already in the lobby, re-check whether the box should appear.
        """
        wasActive = self.__eventActive
        self.__eventActive = self.eventsCache.isEventEnabled()
        if not self.__eventActive and self.__boxState != HSDBoxState.HIDDEN:
            self.setBoxState(HSDBoxState.DONE)
            self.__isAvailable = False
            self.__refreshState()
            if self.state == CameraMovementStates.ON_OBJECT:
                self.goBackToTank()
        elif self.__eventActive and not wasActive:
            self.__updateSupplyDropStatus()

    def __readEffects(self):
        self.__effectsTimeLine = {}
        configSection = ResMgr.openSection(_HALLOWEEN_CONFIG_FILE)
        if configSection is not None:
            effects = configSection['boxEffects']
            if effects is not None:
                for effect in effects.values():
                    name = effect.name
                    self.__effectsTimeLine[name] = effectsFromSection(effect)

        return

    def __readAnims(self):
        self.__animLengths = {}
        configSection = ResMgr.openSection(_HALLOWEEN_CONFIG_FILE)
        if configSection is not None:
            anims = configSection['boxAnims']
            if anims is not None:
                for anim in anims.values():
                    name = anim.name
                    length = anim.readFloat('length')
                    self.__animLengths[name] = length

        return

    def __updateEffect(self, newEffectName, keepEffects=()):
        updatedEffects = []
        for effect in self.__effectsPlayers:
            if effect[0] in keepEffects:
                updatedEffects.append(effect)
            effect[1].stop()

        self.__effectsPlayers = updatedEffects
        if newEffectName is None:
            return
        else:
            effect = self.__effectsTimeLine[newEffectName]
            if effect is not None:
                effectPlayer = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                effectPlayer.play(self.model)
                self.__effectsPlayers.append((newEffectName, effectPlayer))
            return

    def __playAnimationWithCallBack(self, actionName, callback=None):
        LOG_DEBUG_DEV('CAHSD: Playing box animation action: ' + actionName)
        if not actionName:
            return
        else:
            self.__action = None
            action = self.model.action(actionName)
            if action is not None:
                self.__action = action(0, callback)
            if self.__vfxModel is not None:
                action = self.__vfxModel.action(actionName)
                if action is not None:
                    action(0, callback)
            return

    def __vfxModelLoaded(self, resourceRefs, modelName):
        if resourceRefs.failedIDs:
            LOG_ERROR('Failed to load resources %s' % (resourceRefs.failedIDs,))
        else:
            theModel = resourceRefs[modelName]
            BigWorld.addModel(theModel)
            self.__vfxModel = theModel
            self.__vfxModel.addMotor(BigWorld.Servo(self.matrix))
            self.__vfxModel.visible = False

    def remote_requestUIStateValidation(self):
        """
            Request UI state check with delay, intended for remote use. Delay guarantees popups have time to close.
        """
        LOG_DEBUG_DEV('CAHSD: Remote UI state validation was requested.')
        self.delayCallback(0.5, self.__requestUIStateValidation)

    def __requestUIStateValidation(self):
        """
        Confirm that popup windows for end of battle and awards are not visible on-screen before we display the
        box rising up.
        """
        LOG_DEBUG_DEV('CAHSD: Calling validation function on Hangar.')
        if not self.hasDelayedCallback(self.__requestUIStateValidation):
            self.delayCallback(1, self.__requestUIStateValidation)
        g_hangarSpace.onRequestOpenWindowsUpdate(self.__handleUIStateValidation)

    def __handleUIStateValidation(self, validatedUIState):
        """
            Receive event response confirming whether popup windows for end of battle and awards are not visible
            on-screen before we display the box rising up. If we didn't receive a good state, kick off a callback
            to keep checking every second (purely UI; does not use a network call) until we are ready.
        
            If we received a good state, proceed with box appearance by running __updateSupplyDropStatus once more.
        """
        if not validatedUIState:
            LOG_DEBUG_DEV('CAHSD: Received Hangar validation response. State was not validated.')
        else:
            LOG_DEBUG_DEV('CAHSD: Received Hangar validation response. State was validated.')
            self.stopCallback(self.__requestUIStateValidation)
            self.__updateSupplyDropStatus(True)

    def __delayedUpdateSupplyDropStatus(self):
        """
            For hooking up to the halloween tokens sync event. Ensures that we don't check our status until 3s
            after we sync up a new status. This gives the UI time to display any award or battle results windows,
            which should block us from rising out of the ground until they disappear.
        """
        self.delayCallback(4, self.__updateSupplyDropStatus)

    def __updateSupplyDropStatus(self, validatedUIState=False):
        if self.__boxState & (HSDBoxState.AWAITING_CLAIM_RESPONSE | HSDBoxState.OPENING | HSDBoxState.AWARD_UI_SHOWN):
            return
        drops = {dropID:state for dropID, state in self.clientHalloween.getMyDrops().iteritems()}
        hasDrops = sum(drops.values()) > 0
        if hasDrops:
            minID = min(drops.keys())[len(SUPPLY_DROP_TOKEN_PREFIX):]
            maxID = max(drops.keys())[len(SUPPLY_DROP_TOKEN_PREFIX):]
        if not self.__boxState & (HSDBoxState.HIDDEN | HSDBoxState.DONE | HSDBoxState.CLAIM_SUCCESS) and self.enabled:
            if self.clientHalloween.getState() != EVENT_STATE.IN_PROGRESS or not hasDrops:
                self.__hideAndDisable()
            else:
                self.__setDropID(minID, maxID)
            return
        if self.__boxState == HSDBoxState.HIDDEN and self.clientHalloween.getState() == EVENT_STATE.IN_PROGRESS and hasDrops:
            self.__setDropID(minID, maxID)
            if not validatedUIState:
                LOG_DEBUG_DEV('CAHSD: Requesting UI state validation after drop sync.')
                self.__requestUIStateValidation()
            elif self.__eventActive:
                self.setBoxState(HSDBoxState.APPEARANCE)
        if self.__boxState == HSDBoxState.CLAIM_SUCCESS:
            if hasDrops:
                self.__setDropID(minID, maxID)
                self.__finishOpening(True)
            else:
                self.goBackToTank()
                self.setBoxState(HSDBoxState.DONE)

    def __updateAtTank(self):
        self.__updateSupplyDropStatus()

    def __setDropID(self, minStringID, maxStringID):
        self.dropID = int(minStringID)
        self.highestdropID = int(maxStringID)
        self.selectionId = HALLOWEEN_SUPPLY_DROP_SELECTIONID_PREFIX + maxStringID

    def __waitingState(self):
        self.__pauseOpened()
        assert self.__effectsTimeLine['halloween_2017_box_open_hold'] is not None
        self.__updateEffect('halloween_2017_box_open_hold')
        return

    def __startDone(self):
        self.__doAnimWithFunctionCall('sink', self.__hideAndDisable)
        if self.model.visible:
            self.__playSFX('supply_drop_disappearing')
            assert self.__effectsTimeLine['halloween_2017_box_sink'] is not None
            self.__updateEffect('halloween_2017_box_sink')
        return

    def __hideAndDisable(self):
        self.setBoxState(HSDBoxState.HIDDEN)
        self.__isAvailable = False
        self.__refreshState()
        self.__updateEffect(None)
        if self.model is not None:
            self.model.visible = False
        if self.__vfxModel is not None:
            self.__vfxModel.visible = False
        self.__updateSupplyDropStatus()
        return

    def __showAndEnable(self):
        if self.model is None:
            return
        else:
            self.model.visible = True
            self.__pause()
            if self.__vfxModel is not None:
                self.__vfxModel.visible = True
            assert self.__effectsTimeLine['halloween_2017_box_on_scene'] is not None
            self.__updateEffect('halloween_2017_box_on_scene')
            return

    def __startAppearance(self):
        if self.model is None:
            return
        else:
            self.model.visible = True
            if self.__vfxModel is not None:
                self.__vfxModel.visible = True
            self.__doAnimWithFunctionCall('rise', self.__finishAppearance)
            self.__isAvailable = True
            self.__refreshState()
            assert self.__effectsTimeLine['halloween_2017_box_come'] is not None
            self.__updateEffect('halloween_2017_box_come')
            if self.highestdropID > SUPPLY_DROP_LEVEL_ELITE:
                self.__playSFX('supply_drop_appears_redemption')
            elif self.highestdropID > SUPPLY_DROP_LEVEL_BASIC:
                self.__playSFX('supply_drop_appears_elite')
            else:
                self.__playSFX('supply_drop_appears')
            return

    def __doAnimWithFunctionCall(self, animName, functionCallback):
        """
        If an early-out time is set for this anim, trigger callback then, otherwise wait to complete.
        Prevents popping at the end of an anim which needs to transition to another, e.g. rise to pause.
        
        :param animName: action name key used in .model, also used in __animLengths array of anim times
        :param functionCallback: mandatory callback function parameter
        """
        if self.__animLengths.get(animName, None) is not None:
            self.__playAnimationWithCallBack(animName, None)
            self.delayCallback(self.__animLengths[animName] - 0.3, functionCallback)
        else:
            self.__playAnimationWithCallBack(animName, functionCallback)
        return

    def __finishAppearance(self):
        if self.__boxState == HSDBoxState.APPEARANCE:
            self.setBoxState(HSDBoxState.ON_SCENE)

    def __startWaitForOpening(self):
        self.__inProgress = True
        self.__refreshState()
        self.model.visible = True
        if self.__vfxModel is not None:
            self.__vfxModel.visible = True
        assert self.__effectsTimeLine['halloween_2017_box_wait'] is not None
        self.__updateEffect('halloween_2017_box_wait', ('halloween_2017_box_on_scene',))
        return

    def __pause(self):
        self.__playAnimationWithCallBack('pause')

    def __pauseOpened(self):
        self.__playAnimationWithCallBack('pause_opened')

    def __startOpening(self):
        self.__inProgress = True
        self.__refreshState()
        self.model.visible = True
        if self.__vfxModel is not None:
            self.__vfxModel.visible = True
        self.__playSFX('supply_drop_opening')
        assert self.__effectsTimeLine['halloween_2017_box_open'] is not None
        self.__updateEffect('halloween_2017_box_open')
        self.__action.stop()
        self.__doAnimWithFunctionCall('open', self.__finishOpening)
        return

    def __finishOpening(self, doReopen=False):
        self.__inProgress = False
        if self.__inSquad:
            self.setBoxState(HSDBoxState.ON_SCENE)
            DialogsInterface.showI18nInfoDialog('halloween/supply_drop/claim/platoon', self.goBackToTank, None)
            return
        else:
            dropStr = str(self.dropID)
            self.__searchStr = 'halloweenSearching_' + dropStr
            if self.__boxState == HSDBoxState.OPENING or doReopen:
                self.setBoxState(HSDBoxState.AWAITING_CLAIM_RESPONSE)
            Waiting.show(self.__searchStr)
            self.delayCallback(0.3, self.__doOpenDrop)
            self.delayCallback(HalloweenSupplyDrop.CLAIM_TIMEOUT_SECS, self.__claimTimeout)
            return

    def __claimTimeout(self):
        if self.__boxState == HSDBoxState.AWAITING_CLAIM_RESPONSE:
            self.stopWaiting()
            self.setBoxState(HSDBoxState.ON_SCENE)
            DialogsInterface.showI18nInfoDialog('halloween/supply_drop/claim/failed', self.goBackToTank, None)
        return

    def __doOpenDrop(self):
        self.clientHalloween.openDrop(self.dropID, self.clientOpenDropCallback)

    def __playSFX(self, soundName):
        """
        Check for cached sound effect and play it.
        
        :param soundName: name of the sound to search for
        """
        sound = self.__cachedSounds[soundName]
        if sound is not None:
            LOG_DEBUG_DEV('CAHSD: Playing cached SFX: ' + soundName)
            if sound.isPlaying:
                sound.stop()
            sound.play()
        return

    def __readSupplyDropData(self):
        """
        Read the XML file defining metadata on supply drops and store data relevant to this drop instance locally.
        """
        configSection = ResMgr.openSection(_HALLOWEEN_CONFIG_FILE)
        if configSection is not None:
            sounds = configSection['sounds']
            if sounds is not None:
                for soundData in sounds.values():
                    sound = SoundGroups.g_instance.getSound2D(soundData.asString)
                    if sound is not None:
                        self.__cachedSounds[soundData.name] = sound

            otherModels = configSection['otherModels']
            if otherModels is not None:
                self.__vfxModelName = otherModels.readString('supply_drop_vfx_model', '')
                self.customBspModelName = otherModels.readString('custom_bsp_model', '')
        return

    def __updateSquadSettings(self, inSquad):
        self.__inSquad = inSquad
        self.__refreshState()

    def __refreshState(self):
        self.enable(self.__isAvailable and not self.__inProgress and not self.__inSquad)
