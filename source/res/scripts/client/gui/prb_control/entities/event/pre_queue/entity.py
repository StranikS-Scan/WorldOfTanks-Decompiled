# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/pre_queue/entity.py
import BigWorld
from constants import QUEUE_TYPE, QUEUE_TYPE_NAMES
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.event.pre_queue.vehicles_watcher import EventBattleVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.event.pre_queue.ctx import EventBattleQueueCtx
from CurrentVehicle import g_currentVehicle
from gui.prb_control.storages import RECENT_ARENA_STORAGE, storage_getter
from gui.prb_control.entities.event.pre_queue.scheduler import EventScheduler
from helpers import dependency
from skeletons.gui.game_control import IEventBattlesController
_R_HW_QUEUE_MESSENGER = R.strings.hw_messenger.queue

class EventBattleEntryPoint(PreQueueEntryPoint):
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        super(EventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, self.__eventBattlesCtrl.getCurrentQueueType())


class EventBattleEntity(PreQueueEntity):
    _QUEUE_DISABLED_KEY_FMT = '#halloween.hw_messenger:queue/disabled/{}'
    __eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        super(EventBattleEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, self.getCurrentQueueType, PreQueueSubscriber())
        self.__watcher = None
        return

    @property
    def getCurrentQueueType(self):
        return self.__eventBattlesCtrl.getCurrentQueueType()

    @storage_getter(RECENT_ARENA_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        g_currentVehicle.onChanged += self._onVehicleChanged
        self.storage.queueType = self.getCurrentQueueType
        self.__watcher = EventBattleVehiclesWatcher()
        self.__watcher.start()
        if self.__eventBattlesCtrl.isEventShutDown():
            self.pushMessageEventTermination()
        g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        g_currentVehicle.onChanged -= self._onVehicleChanged
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                g_eventDispatcher.loadHangar()
        return super(EventBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.EVENT_BATTLE else super(EventBattleEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        super(EventBattleEntity, self).leave(ctx, callback=callback)

    def onKickedFromQueue(self, queueType, *args):
        super(EventBattleEntity, self).onKickedFromQueue(queueType, *args)
        if not self.__eventBattlesCtrl.isQueueEnabled(queueType):
            SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[queueType])()), type=SystemMessages.SM_TYPE.Error)
        else:
            SystemMessages.pushI18nMessage(self._QUEUE_TIMEOUT_MSG_KEY, type=SystemMessages.SM_TYPE.Error)

    @staticmethod
    def pushMessageEventTermination():
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.arena_start_errors.join.EVENT_DISABLED()), type=SystemMessages.SM_TYPE.Error)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEventBattles(ctx.getVehicleInventoryID(), self.getCurrentQueueType)
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEventBattles(self.getCurrentQueueType)
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        return EventBattleQueueCtx(g_currentVehicle.item.invID, waitingID='prebattle/join', entityType=self.getCurrentQueueType)

    def _createScheduler(self):
        return EventScheduler(self)

    def _updateEntityType(self):
        self._queueType = self.getCurrentQueueType
        self.storage.queueType = self._queueType

    def _onVehicleChanged(self):
        self._updateEntityType()

    def _isNeedToShowSystemMessage(self):
        return False
