# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/raccoon_customization_components.py
import CGF
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from GenericComponents import DynamicModelComponent, AnimatorComponent
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from shared_utils import CONST_CONTAINER
from new_year.skeletons.new_year import IRaccoonAnimationController, ITamagotchiDataProvider
from gui.impl.common.fade_manager import FadeManager
from th_async import th_await, th_async
from new_year.helpers.ny_fading_cover import NYFadingCover
from frameworks.wulf import WindowLayer
from debug_utils import LOG_ERROR
from Queue import Queue

class RaccoonCommands(CONST_CONTAINER):
    FOOD = 'food'
    ACTIVITY = 'activity'
    FUN = 'fun'
    LETTER = 'letter'
    MOOD = 'mood'
    TRIGGER_COMMANDS = (FOOD,
     ACTIVITY,
     FUN,
     LETTER)
    STATE_COMMANDS = (MOOD,)


class RaccoonHelperTriggers(CONST_CONTAINER):
    STAND_UP = 'stand_up'
    FOOD_END = 'food_end'
    LETTER_END = 'letter_end'
    MOOD_UPDATE = 'mood_update'


class RaccoonObjects(CONST_CONTAINER):
    SCISSORS = 'Scissors'
    TOOTHBRUSH = 'ToothBrush'
    MASSAGER = 'Massager'
    FRUITS = 'Fruits'
    RUSKS = 'Rusks'
    CEREALS = 'Cereals'
    CHUMBLEY = 'Chumbley'
    TANK = 'Tank'
    MOON_ROVER = 'MoonRover'


class StateMachineNodes(CONST_CONTAINER):
    SCISSORS = 'Care_Scissors'
    TOOTHBRUSH = 'Care_Toothbrush'
    MASSAGER = 'Care_Massager'
    FRUITS = 'Food_Fruits'
    RUSKS = 'Food_Rusks'
    CEREALS = 'Food_Cereals'
    CHUMBLEY = 'Play_Chumbley'
    TANK = 'Play_Tank'
    MOON_ROVER = 'Play_MoonRover'
    LETTER = 'Letter'
    SAD = 'Idle_Sad'
    NEUTRAL = 'Idle_Neutral'
    HAPPY = 'Idle_Happy'
    SAD_TRANSITION_NODE = 'Sad_Transition_StandUp'
    DYN_OBJECT_FOOD_NODES = (FRUITS, RUSKS, CEREALS)
    DYN_OBJECT_TOY_NODES = (CHUMBLEY, TANK, MOON_ROVER)
    NODES_WITH_FADE = (FRUITS, RUSKS)
    ACTION_NODES = (SCISSORS,
     TOOTHBRUSH,
     MASSAGER,
     FRUITS,
     RUSKS,
     CEREALS,
     CHUMBLEY,
     TANK,
     MOON_ROVER,
     LETTER)
    IDLE_NODES = (SAD, NEUTRAL, HAPPY)
    TRANSITABLE_NODES = IDLE_NODES + (SAD_TRANSITION_NODE,)


class RaccoonMoodStates(CONST_CONTAINER):
    SAD = 0
    NEUTRAL = 1
    HAPPY = 2


NODE_TO_OBJECT = {StateMachineNodes.FRUITS: RaccoonObjects.FRUITS,
 StateMachineNodes.RUSKS: RaccoonObjects.RUSKS,
 StateMachineNodes.CEREALS: RaccoonObjects.CEREALS,
 StateMachineNodes.CHUMBLEY: RaccoonObjects.CHUMBLEY,
 StateMachineNodes.TANK: RaccoonObjects.TANK,
 StateMachineNodes.MOON_ROVER: RaccoonObjects.MOON_ROVER}
FADE_DELAY_SHIFT = 0.7
SHOW_REWARD_DELAY_SHIFT = 0.7

class EffectType(CONST_CONTAINER):
    TOY = 'Toy'
    FOOD = 'Food'


@registerComponent
class RaccoonComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'NY Raccoon'
    category = 'New Year'
    toyEffect = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Toy effect', value=CGF.GameObject)
    foodEffect = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Food effect', value=CGF.GameObject)


class RaccoonManager(CGF.ComponentManager):
    __slots__ = ('__model', '__animator', '__moodState', '__moodNeedUpdate', '__letterNeedActivate', '__activeFoodObject', '__activeToyObject', '__toyEffect', '__foodEffect', '__inAnimation', '__commandQueue', '__inView', '__callbackDelayer')
    __raccoonCtrl = dependency.descriptor(IRaccoonAnimationController)
    __dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, *args):
        super(RaccoonManager, self).__init__(*args)
        self.__model = None
        self.__animator = None
        self.__moodState = RaccoonMoodStates.NEUTRAL
        self.__moodNeedUpdate = False
        self.__letterNeedActivate = False
        self.__activeFoodObject = None
        self.__activeToyObject = None
        self.__toyEffect = None
        self.__foodEffect = None
        self.__inAnimation = False
        self.__inView = False
        self.__commandQueue = Queue()
        self.__callbackDelayer = CallbackDelayer()
        return

    @property
    def isActive(self):
        return self.__model is not None and self.__animator is not None

    def activate(self):
        self.__dataProvider.onViewVisibilityChanged += self.__onViewVisibilityChanged

    def deactivate(self):
        self.__dataProvider.onViewVisibilityChanged -= self.__onViewVisibilityChanged
        self.__reset()

    @onAddedQuery(RaccoonComponent, DynamicModelComponent, AnimatorComponent)
    def onAddedRaccoon(self, raccoon, model, animator):
        self.__model = model
        self.__animator = animator
        self.__animator.setIntParam(RaccoonCommands.MOOD, self.__moodState)
        self.__animator.setOnStateNodeChanged(self.__onAnimatorNodeChanged)
        self.__toyEffect = raccoon.toyEffect
        self.__foodEffect = raccoon.foodEffect

    @onRemovedQuery(RaccoonComponent)
    def onRemovedRaccoon(self, _):
        self.__reset()

    def clearQueue(self):
        with self.__commandQueue.mutex:
            self.__commandQueue.queue.clear()

    def addCommand(self, command, optionalValue=None):
        if not self.isActive:
            return
        else:
            self.__commandQueue.put((command, optionalValue))
            self.__onAnimatorNodeChanged(None)
            return

    def setMoodState(self, moodState):
        if not self.isActive:
            return
        else:
            self.__moodNeedUpdate = self.__moodNeedUpdate or moodState != self.__moodState
            self.__moodState = moodState
            self.__onAnimatorNodeChanged(None)
            return

    def doLetterAction(self):
        if not self.isActive:
            self.__showReward()
            return
        else:
            currentNode = self.__animator.getStateNodeName()
            if not self.__commandQueue.empty() or currentNode not in StateMachineNodes.TRANSITABLE_NODES or self.__inAnimation:
                self.__showReward()
                return
            self.__letterNeedActivate = True
            self.__onAnimatorNodeChanged(None)
            return

    def releaseLetterAction(self):
        if not self.isActive:
            return
        currentNode = self.__animator.getStateNodeName()
        if currentNode == StateMachineNodes.LETTER:
            self.__executeCommand(RaccoonHelperTriggers.LETTER_END)

    def __onViewVisibilityChanged(self, enabled):
        self.__inView = enabled
        if not self.isActive:
            return
        currentNode = self.__animator.getStateNodeName()
        if currentNode == StateMachineNodes.LETTER:
            self.__executeCommand(RaccoonHelperTriggers.LETTER_END)
        if currentNode in StateMachineNodes.NODES_WITH_FADE:
            self.__executeCommand(RaccoonHelperTriggers.FOOD_END)
        self.__callbackDelayer.clearCallbacks()

    def __reset(self):
        self.__callbackDelayer.clearCallbacks()
        self.__resetGoCache()
        self.clearQueue()
        self.__activeToyObject = None
        self.__activeFoodObject = None
        self.__commandQueue = Queue()
        return

    def __resetGoCache(self):
        self.__model = None
        self.__animator = None
        self.__toyEffect = None
        self.__foodEffect = None
        return

    def __updateMoodState(self):
        self.__moodNeedUpdate = False
        self.__executeCommand(RaccoonCommands.MOOD, self.__moodState)
        currentNode = self.__animator.getStateNodeName()
        if currentNode in StateMachineNodes.TRANSITABLE_NODES:
            self.__executeCommand(RaccoonHelperTriggers.MOOD_UPDATE)

    def __activateLetterAction(self):
        self.__executeCommand(RaccoonCommands.LETTER)
        self.__letterNeedActivate = False

    def __executeCommand(self, command, optValue=None):
        if command in RaccoonCommands.TRIGGER_COMMANDS or command in RaccoonHelperTriggers.ALL():
            self.__animator.setTrigger(command)
            self.__inAnimation = True
        if command in RaccoonCommands.STATE_COMMANDS and optValue is not None:
            self.__animator.setIntParam(command, optValue)
        return

    def __update(self):
        currentNode = self.__animator.getStateNodeName()
        if currentNode == StateMachineNodes.SAD and (not self.__commandQueue.empty() or self.__moodNeedUpdate or self.__letterNeedActivate):
            self.__executeCommand(RaccoonHelperTriggers.STAND_UP)
            return
        if currentNode not in StateMachineNodes.TRANSITABLE_NODES:
            return
        if self.__letterNeedActivate:
            self.__activateLetterAction()
            return
        if self.__commandQueue.empty():
            self.__updateMoodState()
            self.__inAnimation = False
            return
        self.__executeCommand(*self.__commandQueue.get())

    def __onAnimatorNodeChanged(self, _):
        currentNode = self.__animator.getStateNodeName()
        if currentNode in StateMachineNodes.TRANSITABLE_NODES:
            self.__update()
            return
        if currentNode in StateMachineNodes.ACTION_NODES:
            self.__updateMoodState()
        if currentNode in StateMachineNodes.DYN_OBJECT_TOY_NODES:
            self.__activeToyObject = self.__updateDynObject(currentNode, self.__activeToyObject, self.__toyEffect)
        if currentNode in StateMachineNodes.DYN_OBJECT_FOOD_NODES:
            self.__activeFoodObject = self.__updateDynObject(currentNode, self.__activeFoodObject, self.__foodEffect)
        if currentNode in StateMachineNodes.NODES_WITH_FADE and not self.__callbackDelayer.hasDelayedCallback(self.__handleFoodEnd) and self.__inView:
            delay = self.__animator.getDuration() - FADE_DELAY_SHIFT
            self.__callbackDelayer.delayCallback(delay, self.__handleFoodEnd)
        if currentNode == StateMachineNodes.LETTER and not self.__callbackDelayer.hasDelayedCallback(self.__showReward) and self.__inView:
            delay = self.__animator.getDuration() - SHOW_REWARD_DELAY_SHIFT
            self.__callbackDelayer.delayCallback(delay, self.__showReward)

    def __updateDynObject(self, currentNode, activeObject, effectGO):
        objectToActivate = NODE_TO_OBJECT[currentNode]
        if objectToActivate != activeObject:
            if activeObject:
                self.__model.setPartVisibleByName(activeObject, False)
            if effectGO and effectGO.isValid():
                if effectGO.isActive():
                    effectGO.deactivate()
                effectGO.activate()
            else:
                LOG_ERROR('RaccoonManager: effect GO is empty or invalid for object {}'.format(objectToActivate))
            self.__model.setPartVisibleByName(objectToActivate, True)
        return objectToActivate

    @th_async
    def __fadeAfterFoodAnimation(self):
        with FadeManager(layer=WindowLayer.TOP_WINDOW, coverFactory=NYFadingCover) as fadeManager:
            yield th_await(fadeManager.show())
            self.__executeCommand(RaccoonHelperTriggers.FOOD_END)
            yield th_await(fadeManager.hide())

    def __handleFoodEnd(self):
        self.__fadeAfterFoodAnimation()

    def __showReward(self):
        self.__raccoonCtrl.onShowGift()
