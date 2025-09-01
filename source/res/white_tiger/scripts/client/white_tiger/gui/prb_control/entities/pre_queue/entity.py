# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from white_tiger.gui.prb_control.entities.pre_queue.actions_validator import WhiteTigerActionsValidator
from white_tiger.gui.prb_control.entities.pre_queue.ctx import WhiteTigerQueueCtx
from white_tiger.gui.prb_control.entities.pre_queue.scheduler import WhiteTigerBattleScheduler
from white_tiger.gui.prb_control.entities.vehicles_watcher import WhiteTigerVehiclesWatcher
from white_tiger.gui.white_tiger_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController
from white_tiger_common.wt_constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from white_tiger.gui.shared.event_dispatcher import showHangar
from CurrentVehicle import g_currentVehicle
from white_tiger.gui.prb_control.entities.vehicle_switcher import WhiteTigerVehicleSwitcher
from soft_exception import SoftException
from shared_utils import nextTick
from helpers import dependency

class WhiteTigerEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(WhiteTigerEntryPoint, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, QUEUE_TYPE.WHITE_TIGER)


@dependency.replace_none_kwargs(ctrl=IWhiteTigerController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class WhiteTigerEntity(PreQueueEntity, WhiteTigerVehicleSwitcher):
    __whiteTigerCtrl = dependency.descriptor(IWhiteTigerController)

    def __init__(self):
        super(WhiteTigerEntity, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, QUEUE_TYPE.WHITE_TIGER, PreQueueSubscriber())
        self.__watcher = None
        self.__waitForRequeue = False
        return

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        self.__watcher = WhiteTigerVehiclesWatcher()
        self.__watcher.start()
        self.startSwitcher()
        return super(WhiteTigerEntity, self).init(ctx=ctx)

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.stopSwitcher()
        self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(WhiteTigerEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.WHITE_TIGER else super(WhiteTigerEntity, self).doSelectAction(action)

    def onEnqueued(self, *args):
        super(WhiteTigerEntity, self).onEnqueued(*args)
        self.__waitForRequeue = False

    def onDequeued(self, *args):
        super(WhiteTigerEntity, self).onDequeued(*args)
        if self.__waitForRequeue:
            self.__waitForRequeue = False
            nextTick(self.doAction)()

    def requeue(self, vehicle=None, vehInvID=None):
        if not self.isInQueue():
            raise SoftException('Player is not in the white tiger queue')
        if vehicle is not None:
            g_currentVehicle.selectVehicle(vehicle.invID)
        elif vehInvID is not None:
            g_currentVehicle.selectVehicle(vehInvID)
        else:
            raise SoftException('No vehicle data or vehicle inventory id provided')
        self.__waitForRequeue = True
        self.doAction()
        return

    @property
    def _accountComponent(self):
        return BigWorld.player().WhiteTigerAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(QUEUE_TYPE.WHITE_TIGER, ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the White Tiger battles', self._queueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(QUEUE_TYPE.WHITE_TIGER)
        LOG_DEBUG('Sends request on dequeuing from the White Tiger battles', self._queueType)

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if not self.__whiteTigerCtrl.isAvailable():
            self.__whiteTigerCtrl.selectRandomMode()
        else:
            showHangar()

    def _goToHangar(self):
        showHangar()

    def _makeQueueCtxByAction(self, action=None):
        return WhiteTigerQueueCtx(g_currentVehicle.item.invID, entityType=self._queueType, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return WhiteTigerActionsValidator(self)

    def _createScheduler(self):
        return WhiteTigerBattleScheduler(self)
