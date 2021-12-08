# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearJukeboxObject.py
import logging
import AnimationSequence
import BigWorld
from shared_utils import nextTick
from NewYearVisualObject import NewYearVisualObject
from helpers import dependency
from new_year.ny_jukebox_controller import JukeboxStateMachineConstants
from skeletons.new_year import INewYearController, IJukeboxController
from uilogging.deprecated.decorators import loggerEntry
from vehicle_systems.stricted_loading import makeCallbackWeak
_logger = logging.getLogger(__name__)

class NewYearJukeboxObject(NewYearVisualObject):
    __nyController = dependency.descriptor(INewYearController)
    __jukeboxController = dependency.descriptor(IJukeboxController)

    def __init__(self):
        super(NewYearJukeboxObject, self).__init__()
        self.__animator = None
        self.__loadedEffects = None
        self.__highlightedSide = None
        return

    @loggerEntry
    def onEnterWorld(self, prereqs):
        super(NewYearJukeboxObject, self).onEnterWorld(prereqs)
        if self.stateMachine:
            animationLoader = AnimationSequence.Loader(self.stateMachine, self.spaceID)
            BigWorld.loadResourceListBG((animationLoader,), makeCallbackWeak(self.__onAnimatorLoaded))
        effectNames = tuple((effectName for effectName in ('', '') if effectName))
        effectList = tuple((AnimationSequence.Loader(effect, self.spaceID) for effect in effectNames))
        if effectList:
            BigWorld.loadResourceListBG(effectList, makeCallbackWeak(self.__onEffectListLoaded, effectNames))

    def onLeaveWorld(self):
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator.unsubscribe(self.__onAnimatorEvent)
            self.__animator = None
        if self.__loadedEffects:
            for effect in self.__loadedEffects:
                self.__enableEffect(effect, False)

        self.__highlightedSide = None
        self.__jukeboxController.onPlaylistSelected -= self.__onPlaylistSelected
        self.__jukeboxController.onTrackSuspended -= self.__onTrackSuspended
        self.__jukeboxController.onHighlighted -= self.__onHighlighted
        self.__jukeboxController.onFaded -= self.__onFaded
        super(NewYearJukeboxObject, self).onLeaveWorld()
        return

    def __setAnimatorTrigger(self, triggerName):
        if self.__animator is None:
            _logger.error('Failed to set animation state machine trigger: %s. Missing state machine for Jukebox Entity', triggerName)
            return
        else:
            self.__animator.setTrigger(triggerName)
            return

    def __onHighlighted(self, side):
        self.__setAnimatorTrigger(JukeboxStateMachineConstants.HIGHLIGHT_TRIGGER[side])
        self.__highlightedSide = side

    def __onFaded(self, side):
        self.__setAnimatorTrigger(JukeboxStateMachineConstants.FADE_TRIGGER[side])
        self.__highlightedSide = None
        return

    def __onAnimatorEvent(self, name, *_):
        if name in (JukeboxStateMachineConstants.IDLE_EVENT, JukeboxStateMachineConstants.PLAY_EVENT):
            if self.__highlightedSide:
                self.__onHighlighted(self.__highlightedSide)
        nextTick(self.__jukeboxController.onAnimatorEvent)(name)

    def __onPlaylistSelected(self, side):
        currentState = self.__animator.getCurrNodeName()
        if currentState == JukeboxStateMachineConstants.IDLE_NODE:
            self.__setAnimatorTrigger(JukeboxStateMachineConstants.START_TRIGGER)
        else:
            self.__setAnimatorTrigger(JukeboxStateMachineConstants.CLICK_TRIGGER[side])

    def __onTrackSuspended(self):
        self.__setAnimatorTrigger(JukeboxStateMachineConstants.SUSPEND_TRIGGER)

    def __onAnimatorLoaded(self, resourceList):
        if self.stateMachine in resourceList.failedIDs:
            _logger.error('Failed to load resource "%s". Effects wont be used', self.stateMachine)
            return
        elif self.model is None:
            _logger.error('Could not spawn animation "%s", because model is not loaded: "%s"', self.stateMachine, self.modelName)
            return
        else:
            self.__animator = resourceList[self.stateMachine]
            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
            self.__animator.subscribe(self.__onAnimatorEvent)
            self.__animator.start()
            self.__jukeboxController.setJukeboxPosition(self.position)
            self.__jukeboxController.onPlaylistSelected += self.__onPlaylistSelected
            self.__jukeboxController.onTrackSuspended += self.__onTrackSuspended
            self.__jukeboxController.onHighlighted += self.__onHighlighted
            self.__jukeboxController.onFaded += self.__onFaded
            return

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

    def __packEffect(self, path, resourceList):
        effect = resourceList[path]
        effect.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        effect.setEnabled(False)
        self.__loadedEffects.append(effect)

    @staticmethod
    def __enableEffect(effect, enable=True):
        effect.setEnabled(enable)
        if enable:
            effect.start()
        else:
            effect.stop()
