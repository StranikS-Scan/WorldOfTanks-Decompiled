# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HangarDog.py
import BigWorld
import AnimationSequence
from ClientSelectableObject import ClientSelectableObject
from vehicle_systems.stricted_loading import makeCallbackWeak
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
_INACTIVE_STATES = {'StartEmptyNode',
 'Reveal01',
 'RunAway01',
 'Sleep Node0',
 'bowlClick',
 'Drinking01'}
_READY_FOR_CLICK_STATES = {'Idle01',
 'LyingIdle01',
 'LyingIdle02',
 'Watching01',
 'Itching01'}
_READY_FOR_BOWL_CLICK_STATES = {'Idle01', 'Watching01', 'Itching01'}

class HangarDog(ClientSelectableObject):

    def __init__(self):
        super(HangarDog, self).__init__()
        self.__animator = None
        self.__checkAnimStatesCallbackID = None
        self.__currState = None
        self.__isReadyForClick = False
        self.enable(False)
        return

    def _getCollisionModelsPrereqs(self):
        if not self.collisionModel:
            return super(HangarDog, self)._getCollisionModelsPrereqs()
        collisionModels = ((0, self.collisionModel),)
        return collisionModels

    def onEnterWorld(self, prereqs):
        super(HangarDog, self).onEnterWorld(prereqs)
        if self.animation:
            self.__createAnimation(self.animation)
        g_eventBus.addListener(events.HangarDogEvent.ON_BOWL_CLICKED, self.__onBowlClicked, scope=EVENT_BUS_SCOPE.LOBBY)

    def onLeaveWorld(self):
        super(HangarDog, self).onLeaveWorld()
        g_eventBus.removeListener(events.HangarDogEvent.ON_BOWL_CLICKED, self.__onBowlClicked, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__checkAnimStatesCallbackID is not None:
            BigWorld.cancelCallback(self.__checkAnimStatesCallbackID)
            self.__checkAnimStatesCallbackID = None
        if self.__animator is not None:
            self.__animator.stop()
            self.__animator = None
        return

    def onMouseDown(self):
        if not self.__isReadyForClick:
            return
        elif not self.enabled:
            return
        elif self.__animator is None:
            return
        else:
            self.__animator.setTrigger('Click')
            self.__isReadyForClick = False
            return

    def __createAnimation(self, resourceName):
        loader = AnimationSequence.Loader(resourceName, self.spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimatorLoaded, resourceName))

    def __onAnimatorLoaded(self, resourceName, resourceList):
        self.__animator = resourceList[resourceName]
        self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, self.spaceID))
        self.__animator.start()
        self.__checkAnimStatesCallbackID = BigWorld.callback(0.0, self.__tick)

    def __tick(self):
        self.__checkAnimStatesCallbackID = None
        self.__checkAnimationState()
        self.__checkAnimStatesCallbackID = BigWorld.callback(0.0, self.__tick)
        return

    def __checkAnimationState(self):
        state = self.__animator.getCurrNodeName()
        if self.__currState != state:
            self.__currState = state
            self.__onStateChanged(state)

    def __onStateChanged(self, newState):
        if newState in _INACTIVE_STATES:
            self.enable(False)
        else:
            self.enable(True)
        if newState in _READY_FOR_CLICK_STATES:
            self.__isReadyForClick = True

    def __onBowlClicked(self, _):
        if not self.__isReadyForClick:
            return
        elif not self.enabled:
            return
        elif self.__animator is None:
            return
        elif self.__currState not in _READY_FOR_BOWL_CLICK_STATES:
            return
        else:
            self.__animator.setTrigger('BowlClick')
            self.__isReadyForClick = False
            return
