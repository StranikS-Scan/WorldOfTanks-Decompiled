# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from constants import QUEUE_TYPE_NAMES
from gui.prb_control.items import SelectResult
from CurrentVehicle import g_currentVehicle
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from halloween_common.halloween_constants import QUEUE_TYPE
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from skeletons.gui.game_control import IHalloweenController
from halloween.gui.prb_control.entities.pre_queue.sheduler import HalloweenScheduler
from halloween.gui.prb_control.entities.pre_queue.ctx import HalloweenBattleQueueCtx
from halloween.gui.prb_control.entities.pre_queue.vehicle_watcher import HalloweenBattleVehiclesWatcher
_R_HW_QUEUE_MESSENGER = R.strings.hw_messenger.queue

class HalloweenBattleEntryPoint(PreQueueEntryPoint):
    __controller = dependency.descriptor(IHalloweenController)

    def __init__(self):
        super(HalloweenBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.HALLOWEEN_BATTLE, self.getCurrentQueueType)

    @property
    def getCurrentQueueType(self):
        return self.__controller.getCurrentQueueType()


class HalloweenBattleEntity(PreQueueEntity):
    _QUEUE_DISABLED_KEY_FMT = '#halloween.hw_messenger:queue/disabled/{}'
    __controller = dependency.descriptor(IHalloweenController)

    def __init__(self):
        super(HalloweenBattleEntity, self).__init__(FUNCTIONAL_FLAG.HALLOWEEN_BATTLE, self.getCurrentQueueType, PreQueueSubscriber())
        self.storage = prequeue_storage_getter(QUEUE_TYPE.HALLOWEEN_BATTLES)()

    @property
    def getCurrentQueueType(self):
        return self.__controller.getCurrentQueueType()

    def init(self, ctx=None):
        self.storage.release()
        self._updateEntityType()
        if self.__controller.isEventShutDown():
            self.pushMessageEventTermination()
        g_currentVehicle.onChanged += self._onVehicleChanged
        self.__watcher = HalloweenBattleVehiclesWatcher()
        self.__watcher.start()
        g_eventDispatcher.loadHangar()
        return super(HalloweenBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_currentVehicle.onChanged -= self._onVehicleChanged
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                g_eventDispatcher.loadHangar()
        return super(HalloweenBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.HALLOWEEN_BATTLE else super(HalloweenBattleEntity, self).doSelectAction(action)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        super(HalloweenBattleEntity, self).leave(ctx, callback=callback)

    def onKickedFromQueue(self, queueType, *args):
        super(HalloweenBattleEntity, self).onKickedFromQueue(queueType, *args)
        if not self.__controller.isQueueEnabled(queueType):
            SystemMessages.pushMessage(backport.text(_R_HW_QUEUE_MESSENGER.disabled.dyn(QUEUE_TYPE_NAMES[queueType])()), type=SystemMessages.SM_TYPE.Error)
        else:
            SystemMessages.pushI18nMessage(self._QUEUE_TIMEOUT_MSG_KEY, type=SystemMessages.SM_TYPE.Error)

    @staticmethod
    def pushMessageEventTermination():
        SystemMessages.pushMessage(backport.text(R.strings.system_messages.arena_start_errors.join.EVENT_DISABLED()), type=SystemMessages.SM_TYPE.Error)

    @property
    def _accountComponent(self):
        return BigWorld.player().HWAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(ctx.getVehicleInventoryID(), self.getCurrentQueueType)
        LOG_DEBUG('Sends request on queuing to the event battles', ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(self.getCurrentQueueType)
        LOG_DEBUG('Sends request on dequeuing from the event battles')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        return HalloweenBattleQueueCtx(g_currentVehicle.item.invID, waitingID='prebattle/join', entityType=self.getCurrentQueueType)

    def _createScheduler(self):
        return HalloweenScheduler(self)

    def _updateEntityType(self):
        self._queueType = self.getCurrentQueueType
        self.storage.queueType = self._queueType

    def _onVehicleChanged(self):
        self._updateEntityType()

    def _isNeedToShowSystemMessage(self):
        return False
