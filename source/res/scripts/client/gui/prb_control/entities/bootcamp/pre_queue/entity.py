# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bootcamp/pre_queue/entity.py
from PlayerEvents import g_playerEvents
from bootcamp.BootCampEvents import g_bootcampEvents
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control import prb_getters, prbDispatcherProperty
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.ctx import DequeueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import BootcampEvent
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IBootcampController
from adisp import process
from gui.prb_control.entities.base.pre_queue.ctx import QueueCtx

class BootcampSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onBootcampEnqueued += entity.onEnqueued
        g_playerEvents.onBootcampDequeued += entity.onDequeued
        g_playerEvents.onBootcampEnqueueFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromBootcampQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        g_bootcampEvents.onBootcampBecomeNonPlayer += entity.onBootcampBecomeNonPlayer
        g_eventBus.addListener(BootcampEvent.QUEUE_DIALOG_CANCEL, entity.onQueueCancel, EVENT_BUS_SCOPE.LOBBY)

    def unsubscribe(self, entity):
        g_playerEvents.onBootcampEnqueued -= entity.onEnqueued
        g_playerEvents.onBootcampDequeued -= entity.onDequeued
        g_playerEvents.onBootcampEnqueueFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromBootcampQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        g_bootcampEvents.onBootcampBecomeNonPlayer -= entity.onBootcampBecomeNonPlayer
        g_eventBus.removeListener(BootcampEvent.QUEUE_DIALOG_CANCEL, entity.onQueueCancel, EVENT_BUS_SCOPE.LOBBY)


class BootcampEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(BootcampEntryPoint, self).__init__(FUNCTIONAL_FLAG.BOOTCAMP, QUEUE_TYPE.BOOTCAMP)


class BootcampEntity(PreQueueEntity):
    lobbyContext = dependency.descriptor(ILobbyContext)
    bootcampController = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(BootcampEntity, self).__init__(FUNCTIONAL_FLAG.BOOTCAMP, QUEUE_TYPE.BOOTCAMP, BootcampSubscriber())
        if self.bootcampController.getLessonNum() == 0 or not self.bootcampController.isInBootcamp():
            self._modeFlags |= FUNCTIONAL_FLAG.LOAD_PAGE

    def init(self, ctx=None):
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        if not self.bootcampController.isInBootcampAccount():
            self.bootcampController.startBootcamp(False)
        return super(BootcampEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        return super(BootcampEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def isInQueue(self):
        return prb_getters.isInBootcampQueue()

    def queue(self, ctx, callback=None):
        self.bootcampController.showActionWaitWindow()
        super(BootcampEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.BOOTCAMP else super(BootcampEntity, self).doSelectAction(action)

    def getConfirmDialogMeta(self, ctx):
        if not self.hasLockedState() and ctx.getCtrlType() == CTRL_ENTITY_TYPE.UNIT and ctx.getEntityType() in (PREBATTLE_TYPE.SQUAD, PREBATTLE_TYPE.EVENT):
            meta = rally_dialog_meta.createLeavePreQueueMeta(ctx, self.getQueueType(), self.canSwitch(ctx))
        else:
            meta = super(BootcampEntity, self).getConfirmDialogMeta(ctx)
        return meta

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _doQueue(self, ctx):
        self.bootcampController.enqueueBootcamp()
        LOG_DEBUG('Sends request to enqueue to the bootcamp battle')

    def _doDequeue(self, ctx):
        self.bootcampController.hideActionWaitWindow()
        self.bootcampController.dequeueBootcamp()
        LOG_DEBUG('Sends request on dequeuing from the bootcamp battle')

    def _makeQueueCtxByAction(self, action=None):
        return QueueCtx(entityType=QUEUE_TYPE.BOOTCAMP, waitingID='')

    def _goToQueueUI(self):
        self.bootcampController.hideActionWaitWindow()
        g_eventDispatcher.loadBootcampQueue()
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    def _exitFromQueueUI(self):
        g_eventDispatcher.unloadBootcampQueue()

    @process
    def onQueueCancel(self, _):
        if self.isInQueue():
            self.exitFromQueue()
        elif self.prbDispatcher is not None:
            yield self.prbDispatcher.doLeaveAction(LeavePrbAction())
        return

    def onBootcampBecomeNonPlayer(self):
        LOG_DEBUG('onBootcampBecomeNonPlayer')
        self._exitFromQueueUI()

    def __onServerSettingChanged(self, diff):
        if not self.lobbyContext.getServerSettings().isBootcampEnabled():

            def __leave(_=True):
                g_prbCtrlEvents.onPreQueueLeft()

            if self.isInQueue():
                self.dequeue(DequeueCtx(waitingID='prebattle/leave'), callback=__leave)
            else:
                __leave()

    def _validateParentControl(self):
        return False
