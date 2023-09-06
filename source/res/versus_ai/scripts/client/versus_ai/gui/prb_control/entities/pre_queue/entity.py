# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/prb_control/entities/pre_queue/entity.py
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from versus_ai.gui.prb_control.entities.pre_queue.vehicles_watcher import VersusAIVehiclesWatcher
from versus_ai.gui.prb_control.entities.squad.entity import VersusAISquadEntryPoint
from versus_ai.gui.prb_control.entities.pre_queue.actions_validator import VersusAIActionsValidator
from versus_ai.skeletons.versus_ai_controller import IVersusAIController
_logger = logging.getLogger(__name__)

class VersusAIEntryPoint(PreQueueEntryPoint):
    __versusAICtrl = dependency.descriptor(IVersusAIController)

    def __init__(self):
        super(VersusAIEntryPoint, self).__init__(FUNCTIONAL_FLAG.VERSUS_AI, QUEUE_TYPE.VERSUS_AI)

    def select(self, ctx, callback=None):
        if not self.__versusAICtrl.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(VersusAIEntryPoint, self).select(ctx, callback)
            return


class VersusAIEntity(PreQueueEntity):

    def __init__(self):
        super(VersusAIEntity, self).__init__(FUNCTIONAL_FLAG.VERSUS_AI, QUEUE_TYPE.VERSUS_AI, PreQueueSubscriber())
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.VERSUS_AI)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = VersusAIVehiclesWatcher()
        self.__watcher.start()
        return super(VersusAIEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if not woEvents and not self.canSwitch(ctx):
            g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        return super(VersusAIEntity, self).fini(ctx, woEvents)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return VersusAIActionsValidator(self)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(VersusAIEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.VERSUS_AI_SQUAD, PREBATTLE_ACTION_NAME.SQUAD):
            squadEntryPoint = VersusAISquadEntryPoint(action.accountsToInvite)
            return SelectResult(True, squadEntryPoint)
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.VERSUS_AI else super(VersusAIEntity, self).doSelectAction(action)

    def _doQueue(self, ctx):
        BigWorld.player().AccountVersusAIComponent.enqueueVersusAI(ctx)
        _logger.debug('Sends request on queuing to the VersusAI - %r', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountVersusAIComponent.dequeueVersusAI()
        _logger.debug('Sends request on dequeuing from the VersusAI')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
