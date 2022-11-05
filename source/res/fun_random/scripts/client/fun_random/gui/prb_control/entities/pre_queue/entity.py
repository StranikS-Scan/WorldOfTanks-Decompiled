# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/prb_control/entities/pre_queue/entity.py
import logging
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from fun_random_common.fun_constants import FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID
from fun_random.gui.feature.util.fun_helpers import notifyCaller
from fun_random.gui.fun_gui_constants import FunctionalFlag, PrebattleActionName
from fun_random.gui.prb_control.entities.pre_queue.actions_validator import FunRandomActionsValidator
from fun_random.gui.prb_control.entities.pre_queue.ctx import FunRandomQueueCtx, JoinFunPreQueueModeCtx
from fun_random.gui.prb_control.entities.pre_queue.permissions import FunRandomPermissions
from fun_random.gui.prb_control.entities.pre_queue.scheduler import FunRandomScheduler
from fun_random.gui.prb_control.entities.pre_queue.vehicles_watcher import FunRandomVehiclesWatcher
from fun_random.gui.prb_control.entities.squad.entity import FunRandomSquadEntryPoint
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueSubscriber, PreQueueEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
_logger = logging.getLogger(__name__)

class FunRandomEntryPoint(PreQueueEntryPoint):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def __init__(self):
        super(FunRandomEntryPoint, self).__init__(FunctionalFlag.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM)
        self.__desiredSubModeID = UNKNOWN_EVENT_ID

    def setExtData(self, extData):
        self.__desiredSubModeID = extData.get(FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID)

    def makeDefCtx(self):
        return JoinFunPreQueueModeCtx(self._queueType, self.__desiredSubModeID, flags=self.getFunctionalFlags())

    def select(self, ctx, callback=None):
        desiredSubModeID = ctx.getDesiredSubModeID()
        desiredSubMode = self.__funRandomController.subModesHolder.getSubMode(desiredSubModeID)
        if not self.__funRandomController.isEnabled():
            _logger.warning('Trying to get into fun random when FEP feature is disabled.')
            self.__abortSelection(PRE_QUEUE_JOIN_ERRORS.DISABLED, callback)
        elif desiredSubModeID == UNKNOWN_EVENT_ID or desiredSubMode is None:
            _logger.error('Trying to get into invalid fun random sub mode %s.', desiredSubModeID)
            self.__abortSelection(PRE_QUEUE_JOIN_ERRORS.DISABLED, callback)
        elif not desiredSubMode.isAvailable():
            _logger.debug('Trying to get into fun random sub mode %s when it is not available.', desiredSubModeID)
            self.__abortSelection(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE, callback)
        else:
            self.__funRandomController.subModesHolder.setDesiredSubModeID(desiredSubModeID)
            super(FunRandomEntryPoint, self).select(ctx, callback)
        return

    def __abortSelection(self, reason, callback=None):
        self.__desiredSubModeID = UNKNOWN_EVENT_ID
        self.__funRandomController.subModesHolder.setDesiredSubModeID(UNKNOWN_EVENT_ID)
        notifyCaller(callback, False)
        g_prbCtrlEvents.onPreQueueJoinFailure(reason)


class FunRandomEntity(PreQueueEntity):
    __funRandomController = dependency.descriptor(IFunRandomController)

    def __init__(self):
        super(FunRandomEntity, self).__init__(FunctionalFlag.FUN_RANDOM, QUEUE_TYPE.FUN_RANDOM, PreQueueSubscriber())
        self.__watcher = None
        return

    def init(self, ctx=None):
        self.__watcher = FunRandomVehiclesWatcher()
        self.__watcher.start()
        return super(FunRandomEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and not self.canSwitch(ctx) and (ctx is None or not ctx.hasFlags(FunctionalFlag.LOAD_PAGE)):
            g_eventDispatcher.loadHangar()
        return super(FunRandomEntity, self).fini(ctx, woEvents)

    def getPermissions(self, pID=None, **kwargs):
        return FunRandomPermissions(self.isInQueue())

    def doSelectAction(self, action):
        if action.actionName == PrebattleActionName.SQUAD:
            squadEntryPoint = FunRandomSquadEntryPoint(action.accountsToInvite)
            squadEntryPoint.setExtData({FUN_EVENT_ID_KEY: self.__funRandomController.subModesHolder.getDesiredSubModeID()})
            return SelectResult(True, squadEntryPoint)
        elif action.actionName == PrebattleActionName.FUN_RANDOM:
            desiredSubModeID = action.extData.get(FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID)
            self.__funRandomController.subModesHolder.setDesiredSubModeID(desiredSubModeID)
            g_eventDispatcher.loadHangar()
            return SelectResult(True, None)
        else:
            return super(FunRandomEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        self.__funRandomController.subModesHolder.setDesiredSubModeID(UNKNOWN_EVENT_ID)
        super(FunRandomEntity, self).leave(ctx, callback)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(FunRandomEntity, self).queue(ctx, callback=callback)

    def _createActionsValidator(self):
        return FunRandomActionsValidator(self)

    def _createScheduler(self):
        return FunRandomScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().AccountFunRandomComponent.enqueueFunRandom(ctx)
        _logger.debug('Sends request for queuing to the fun event battle %s', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountFunRandomComponent.dequeueFunRandom()
        _logger.debug('Sends request for dequeueing from the fun event battle')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FunctionalFlag.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        desiredSubModeID = self.__funRandomController.subModesHolder.getDesiredSubModeID()
        return FunRandomQueueCtx(invID, desiredSubModeID, waitingID='prebattle/join')
