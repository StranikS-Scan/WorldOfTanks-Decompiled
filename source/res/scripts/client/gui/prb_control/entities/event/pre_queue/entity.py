# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/entity.py
import BigWorld
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite, BaseActionsValidator, TutorialActionsValidator
from gui.prb_control.entities.base.pre_queue.actions_validator import InQueueValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
from gui.prb_control.items import ValidationResult, SelectResult
from gui.prb_control.prb_getters import isInEventBattlesQueue
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PREBATTLE_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from skeletons.gui.game_event_controller import IGameEventController
from helpers import dependency

class EventBattleSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles += entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles += entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedEventBattles -= entity.onEnqueued
        g_playerEvents.onDequeuedEventBattles -= entity.onDequeued
        g_playerEvents.onEnqueueEventBattlesFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromEventBattles -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class EventBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(EventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, QUEUE_TYPE.EVENT_BATTLES)


class EventBattleEntity(PreQueueEntity):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(EventBattleEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, QUEUE_TYPE.EVENT_BATTLES, EventBattleSubscriber())

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        g_eventDispatcher.loadEventHangar()
        return super(EventBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.EVENT_BATTLE else super(EventBattleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return isInEventBattlesQueue()

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(EventBattleEntity, self).leave(ctx, callback=callback)

    def _createActionsValidator(self):
        return PreQueueEventActionsValidator(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getGeneralID())
        general = self.gameEventController.getSelectedGeneral()
        BigWorld.player().changeSelectedGeneral(general.getID(), general.getCurrentProgressLevel(), general.getFrontID())
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles()
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _makeQueueCtxByAction(self, action=None):
        return EventBattleQueueCtx(self.gameEventController.getSelectedGeneralID(), waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadEventBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadEventHangar()


class PreQueueEventActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        self._stateValidator = self._createStateValidator(entity)
        self._energyValidator = self._createEnergyValidator(entity)
        self._tutorialValidator = self._createTutorialValidator(entity)
        self._generalValidator = self._createGeneralValidator(entity)
        validators = [self._stateValidator,
         self._energyValidator,
         self._tutorialValidator,
         self._generalValidator]
        super(PreQueueEventActionsValidator, self).__init__(entity, validators)

    def _createStateValidator(self, entity):
        return InQueueValidator(entity)

    def _createEnergyValidator(self, entity):
        return GameEnergyValidator(entity)

    def _createTutorialValidator(self, entity):
        return TutorialActionsValidator(entity)

    def _createGeneralValidator(self, entity):
        return GeneralAvailableValidator(entity)


class GameEnergyValidator(BaseActionsValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        energy = self.gameEventController.getEnergy()
        return ValidationResult(False, PREBATTLE_RESTRICTION.EVENT_NOT_ENOUGHT_ENERGY) if energy.getCurrentCount() == 0 else super(GameEnergyValidator, self)._validate()


class GeneralAvailableValidator(BaseActionsValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        general = self.gameEventController.getSelectedGeneral()
        return ValidationResult(False, PREBATTLE_RESTRICTION.EVENT_GENERAL_LOCKED) if general.isLocked() else super(GeneralAvailableValidator, self)._validate()
