# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/PianoMusician.py
import logging
import BigWorld
import AnimationSequence
from vehicle_systems.stricted_loading import makeCallbackWeak
from ClientSelectableObject import ClientSelectableObject
from helpers import dependency
from skeletons.new_year import IPianoController
_logger = logging.getLogger(__name__)

class _PianoStateMachineConstants(object):
    MUSIC_LEVEL_PARAM = 'music_level'
    SWITCH_NODE = 'switch_node'
    LEVEL_UP_TRIGGER = 'level_up'
    STOP_IDLE_TRIGGER = 'stop_idle'
    IDLE_LEVEL_01 = 'idle_level_01'
    IDLE_LEVEL_02 = 'idle_level_02'
    IDLE_LEVEL_03 = 'idle_level_03'
    IDLE_LEVELS = (IDLE_LEVEL_01, IDLE_LEVEL_02, IDLE_LEVEL_03)
    PLAY_LEVEL_01 = 'pianist_level_01'
    PLAY_LEVEL_02 = 'pianist_level_02'
    PLAY_LEVEL_03 = 'pianist_level_03'
    PLAY_LEVELS = (PLAY_LEVEL_01, PLAY_LEVEL_02, PLAY_LEVEL_03)
    PLAY_EVENT = 'Play'
    IDLE_EVENT = 'Idle'


class PianoMusician(ClientSelectableObject):
    __pianoController = dependency.descriptor(IPianoController)

    def __init__(self):
        super(PianoMusician, self).__init__()
        self.__animator = None
        self.__loadedEffects = None
        return

    def onEnterWorld(self, prereqs):
        if self.animationStateMachine:
            animationLoader = AnimationSequence.Loader(self.animationStateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded))
        effectNames = tuple((effectName for effectName in (self.effectFairytale,
         self.effectNewYear,
         self.effectChristmas,
         self.effectOriental) if effectName))
        if len(effectNames) != self.__pianoController.getStatesCount():
            _logger.error('Effects count differs from expected. Effects wont be loaded')
        else:
            effectList = tuple((AnimationSequence.Loader(effect, self.spaceID) for effect in effectNames))
            if effectList:
                BigWorld.loadResourceListBG(effectList, makeCallbackWeak(self.__onEffectListLoaded, effectNames))
        super(PianoMusician, self).onEnterWorld(prereqs)

    def onLeaveWorld(self):
        super(PianoMusician, self).onLeaveWorld()
        self.__pianoController.onLevelUp -= self.__onLevelUp
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator.unsubscribe(self.__animatorEvent)
            self.__animator = None
        if self.__loadedEffects:
            for effect in self.__loadedEffects:
                self.__enableEffect(effect, False)

        self.__loadedEffects = None
        return

    def onMouseClick(self):
        super(PianoMusician, self).onMouseClick()
        self.__pianoController.handlePianoClicked()
        self.__startPlayNow()
        self.__switchEffect()

    def _addEdgeDetect(self):
        BigWorld.wgAddEdgeDetectEntity(self, 2, self.edgeMode, False)

    @staticmethod
    def __enableEffect(effect, enable=True):
        effect.setEnabled(enable)
        if enable:
            effect.start()
        else:
            effect.stop()

    def __onAnimatorLoaded(self, resourceList):
        if self.animationStateMachine in resourceList.failedIDs:
            return
        elif self.model is None:
            _logger.error('Could not spawn animation "%s", because model is not loaded: "%s"', self.animationStateMachine, self.modelName)
            return
        else:
            self.__pianoController.setInitialState()
            self.__animator = resourceList[self.animationStateMachine]
            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
            self.__animator.subscribe(self.__animatorEvent)
            self.__animator.start()
            musicLevel = self.__pianoController.getCurrentMusicLevel()
            self.__animator.setIntParam(_PianoStateMachineConstants.MUSIC_LEVEL_PARAM, musicLevel)
            self.__pianoController.onLevelUp += self.__onLevelUp
            return

    def __packEffect(self, path, resourceList):
        effect = resourceList[path]
        effect.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        effect.setEnabled(False)
        self.__loadedEffects.append(effect)

    def __onEffectListLoaded(self, expectedEffectsNames, resourceList):
        if self.model is None:
            _logger.error('Could not spawn effects, because model is not loaded: "%s"', self.modelName)
            return
        else:
            for effect in expectedEffectsNames:
                if effect in resourceList.failedIDs:
                    _logger.error('Failed to load effect "%s". Effects wont be used', effect)
                    return

            self.__loadedEffects = []
            for effect in expectedEffectsNames:
                self.__packEffect(effect, resourceList)

            return

    def __onLevelUp(self):
        if self.__animator is None:
            return
        else:
            musicLevel = self.__pianoController.getCurrentMusicLevel()
            self.__animator.setIntParam(_PianoStateMachineConstants.MUSIC_LEVEL_PARAM, musicLevel)
            currentState = self.__animator.getCurrNodeName()
            if currentState != _PianoStateMachineConstants.SWITCH_NODE:
                self.__animator.setTrigger(_PianoStateMachineConstants.LEVEL_UP_TRIGGER)
            return

    def __startPlayNow(self):
        if self.__animator is None:
            return
        else:
            currentState = self.__animator.getCurrNodeName()
            if currentState in _PianoStateMachineConstants.IDLE_LEVELS:
                self.__animator.setTrigger(_PianoStateMachineConstants.STOP_IDLE_TRIGGER)
            return

    def __switchEffect(self):
        if not self.__loadedEffects or self.__animator is None:
            return
        else:
            for effect in self.__loadedEffects:
                self.__enableEffect(effect, False)

            currentEffect = self.__pianoController.getEffectState()
            self.__enableEffect(self.__loadedEffects[currentEffect])
            return

    def __animatorEvent(self, name, _):
        if name == _PianoStateMachineConstants.PLAY_EVENT:
            enableEffect = True
        elif name == _PianoStateMachineConstants.IDLE_EVENT:
            enableEffect = False
            if self.__pianoController.isNoMoreIdle():
                self.__animator.setTrigger(_PianoStateMachineConstants.STOP_IDLE_TRIGGER)
        if not self.__loadedEffects:
            return
        currentEffect = self.__pianoController.getEffectState()
        self.__enableEffect(self.__loadedEffects[currentEffect], enableEffect)
