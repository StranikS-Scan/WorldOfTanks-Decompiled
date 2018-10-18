# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/sandbox/pre_queue/entity.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import DEFAULT_QUEUE
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.sandbox.pre_queue.actions_validator import SandboxActionsValidator
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.ctx import DequeueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.sandbox.pre_queue.ctx import SandboxQueueCtx
from gui.prb_control.entities.sandbox.pre_queue.vehicles_watcher import SandboxVehiclesWatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException

class SandboxSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedSandbox += entity.onEnqueued
        g_playerEvents.onDequeuedSandbox += entity.onDequeued
        g_playerEvents.onEnqueuedSandboxFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromSandboxQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedSandbox -= entity.onEnqueued
        g_playerEvents.onDequeuedSandbox -= entity.onDequeued
        g_playerEvents.onEnqueuedSandboxFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromSandboxQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class SandboxEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(SandboxEntryPoint, self).__init__(FUNCTIONAL_FLAG.SANDBOX, QUEUE_TYPE.SANDBOX)


class SandboxEntity(PreQueueEntity):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(SandboxEntity, self).__init__(FUNCTIONAL_FLAG.SANDBOX, QUEUE_TYPE.SANDBOX, SandboxSubscriber())
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.SANDBOX)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = SandboxVehiclesWatcher()
        self.__watcher.start()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        return super(SandboxEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        return super(SandboxEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def isInQueue(self):
        return prb_getters.isInSandboxQueue()

    def leave(self, ctx, callback=None):
        if not ctx.hasFlags(FUNCTIONAL_FLAG.TUTORIAL) and not ctx.hasFlags(FUNCTIONAL_FLAG.SANDBOX):
            self.storage.suspend()
        super(SandboxEntity, self).leave(ctx, callback)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(SandboxEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.SANDBOX else super(SandboxEntity, self).doSelectAction(action)

    def getConfirmDialogMeta(self, ctx):
        if not self.hasLockedState() and not ctx.hasFlags(FUNCTIONAL_FLAG.TUTORIAL) and AccountSettings.getSettings(DEFAULT_QUEUE) == QUEUE_TYPE.SANDBOX:
            meta = rally_dialog_meta.createLeavePreQueueMeta(ctx, self.getQueueType(), self.canSwitch(ctx))
        else:
            meta = super(SandboxEntity, self).getConfirmDialogMeta(ctx)
        return meta

    def _createActionsValidator(self):
        return SandboxActionsValidator(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueSandbox(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the PvE tutorial battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueSandbox()
        LOG_DEBUG('Sends request on dequeuing from the PvE tutorial battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return SandboxQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadSandboxQueue()
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def _exitFromQueueUI(self):
        g_eventDispatcher.unloadSandboxQueue()

    def __onServerSettingChanged(self, diff):
        if not self.lobbyContext.getServerSettings().isSandboxEnabled():

            def __leave(_=True):
                g_prbCtrlEvents.onPreQueueLeft()

            if self.isInQueue():
                self.dequeue(DequeueCtx(waitingID='prebattle/leave'), callback=__leave)
            else:
                __leave()
