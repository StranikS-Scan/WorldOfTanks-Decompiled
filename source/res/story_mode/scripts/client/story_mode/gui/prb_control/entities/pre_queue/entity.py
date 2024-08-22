# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.Scaleform.Waiting import Waiting
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.pre_queue.ctx import DequeueCtx
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import REQUEST_TYPE
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from story_mode.gui.impl.battle.prebattle_window import getOpenedPrebattleView
from story_mode.gui.prb_control.entities.pre_queue import tasksAvailableCheck
from story_mode.gui.prb_control.entities.pre_queue.actions_validator import StoryModeActionsValidator
from story_mode.gui.prb_control.entities.pre_queue.ctx import StoryModeQueueCtx
from story_mode.gui.prb_control.entities.pre_queue.permissions import StoryModePermissions
from story_mode.gui.shared.event_dispatcher import showQueueWindow
from story_mode.gui.shared.utils import waitForLobby
from story_mode.gui.story_mode_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from story_mode.skeletons.story_mode_controller import IStoryModeController
from wg_async import wg_async, wg_await

class StoryModeEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(StoryModeEntryPoint, self).__init__(FUNCTIONAL_FLAG.STORY_MODE, QUEUE_TYPE.STORY_MODE)


class StoryModeEntity(PreQueueEntity):
    storyModeCtrl = dependency.descriptor(IStoryModeController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self):
        self._queueWindow = None
        super(StoryModeEntity, self).__init__(FUNCTIONAL_FLAG.STORY_MODE, QUEUE_TYPE.STORY_MODE, PreQueueSubscriber())
        return

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        self._modeFlags |= FUNCTIONAL_FLAG.LOAD_PAGE
        return super(StoryModeEntity, self).init(ctx=ctx)

    def doAction(self, action=None):
        if self._skippedShowGUI:
            if Waiting.isOpened('login'):
                Waiting.hide('login')
            self._requestCtx = self._makeQueueCtxByAction(action)
            self._requestCtx.startProcessing()
            self._doQueue(self._requestCtx)
        else:
            super(StoryModeEntity, self).doAction(action)

    def onEnqueued(self, *args):
        if self._requestCtx.getRequestType() == REQUEST_TYPE.QUEUE:
            self._requestCtx.stopProcessing(True)
        self._invokeListeners('onEnqueued', self.getQueueType(), *args)
        self._goToQueueUI()

    def exitFromQueue(self):
        if self._skippedShowGUI:
            self.dequeue(DequeueCtx(waitingID='prebattle/leave'))
        else:
            super(StoryModeEntity, self).exitFromQueue()

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                self._loadHangar()
                self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(StoryModeEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.STORY_MODE else super(StoryModeEntity, self).doSelectAction(action)

    def getConfirmDialogMeta(self, ctx):
        return None

    @tasksAvailableCheck
    def queue(self, ctx, callback=None):
        super(StoryModeEntity, self).queue(ctx, callback=callback)

    @wg_async
    def _loadHangar(self):
        yield wg_await(waitForLobby())
        g_eventDispatcher.loadHangar()

    @property
    def _guiCtx(self):
        return self.lobbyContext.getGuiCtx()

    @property
    def _skippedShowGUI(self):
        return self._guiCtx.get('skipHangar', False)

    @property
    def _accountComponent(self):
        return BigWorld.player().StoryModeAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle()
        LOG_DEBUG('Sends request on queuing to the  Story Mode battles', self._queueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle()
        LOG_DEBUG('Sends request on dequeuing from the Story Mode battles', self._queueType)

    def _goToHangar(self):
        pass

    def _goToQueueUI(self):
        prebattleWindow = getOpenedPrebattleView()
        if prebattleWindow is not None:
            self._queueWindow = prebattleWindow
            self._queueWindow.startWaitQueue()
        elif self._queueWindow is None:
            self._queueWindow = showQueueWindow()
        return super(StoryModeEntity, self)._goToQueueUI()

    def _exitFromQueueUI(self):
        if self._skippedShowGUI:
            self.storyModeCtrl.exitQueue()
        if self._queueWindow is not None:
            self._queueWindow.destroy()
            self._queueWindow = None
        return

    def _makeQueueCtxByAction(self, action=None):
        return StoryModeQueueCtx()

    def _createActionsValidator(self):
        return StoryModeActionsValidator(self)

    def getPermissions(self, *_, **__):
        return StoryModePermissions(self.isInQueue())

    def _validateParentControl(self):
        return False
