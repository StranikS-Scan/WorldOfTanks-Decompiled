# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/rts_battles/pre_queue/entity.py
import logging
import typing
import BigWorld
from actions_validator import RTSActionsValidator
from adisp import process
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from gui.prb_control import prb_getters
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntity
from gui.prb_control.entities.rts_battles.pre_queue.ctx import RTSBattleQueueCtx
from gui.prb_control.entities.rts_battles.pre_queue.permissions import RTSPermissions
from gui.prb_control.entities.rts_battles.pre_queue.vehicles_watcher import RTSVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.prb_control.entity import PeriodicEntryPoint
from gui.periodic_battles.prb_control.scheduler import PeriodicScheduler
from gui.shared.utils import functions
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
logger = logging.getLogger(__name__)

class RTSScheduler(PeriodicScheduler):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)

    def __show(self, isInit=False):
        pass


class _RTSBattleSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRTS += entity.onEnqueued
        g_playerEvents.onDequeuedRTS += entity.onDequeued
        g_playerEvents.onEnqueuedRTSFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromRTSQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRTS -= entity.onEnqueued
        g_playerEvents.onDequeuedRTS -= entity.onDequeued
        g_playerEvents.onEnqueuedRTSFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRTSQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class RTSBattleEntryPoint(PeriodicEntryPoint):
    _RES_ROOT = R.strings.system_messages.rts
    _controller = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        super(RTSBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.RTS, QUEUE_TYPE.RTS)


class RTSBattleEntity(PreQueueEntity):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self):
        super(RTSBattleEntity, self).__init__(FUNCTIONAL_FLAG.RTS, QUEUE_TYPE.RTS, _RTSBattleSubscriber())
        self.__watcher = None
        self.__queueReloaded = False
        return

    @prequeue_storage_getter(QUEUE_TYPE.RTS)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = RTSVehiclesWatcher(self.__rtsController.isCommander())
        self.__watcher.start()
        return super(RTSBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_eventDispatcher.loadHangar()
        return super(RTSBattleEntity, self).fini(ctx, woEvents)

    @process
    def queue(self, ctx, callback=None):
        goBattle = isRTSCommander = self.__rtsController.isCommander()
        if not isRTSCommander:
            vehiclesToCheck = (g_currentVehicle.item,)
            goBattle = yield functions.checkAmmoLevel(vehiclesToCheck)
        if not goBattle:
            if callback is not None:
                callback(False)
            return
        else:
            super(RTSBattleEntity, self).queue(ctx, callback=callback)
            return

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.RTS else super(RTSBattleEntity, self).doSelectAction(action)

    def isInQueue(self):
        return prb_getters.isInRTSQueue()

    def getPermissions(self, pID=None, **kwargs):
        return RTSPermissions(self.isInQueue())

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(RTSBattleEntity, self).leave(ctx, callback=callback)

    def reloadQueue(self, changeToCommander=True):
        if not changeToCommander:
            raise SoftException('Changing of queue as a tankman is not supported')
        self.__rtsController.changeControlMode(isCommander=True)
        self.__queueReloaded = True
        self.exitFromQueue()

    def _createActionsValidator(self):
        return RTSActionsValidator(self)

    def _createScheduler(self):
        return RTSScheduler(self)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return RTSBattleQueueCtx(invID, waitingID='prebattle/join')

    def _doQueue(self, ctx):
        logger.debug('Sends request on queuing to the RTS battles')
        BigWorld.player().enqueueRTSBattles(ctx.getVehicleInventoryID(), self.__rtsController.isCommander())

    def _doDequeue(self, ctx):
        logger.debug('Sends request on dequeuing from the RTS battles')
        BigWorld.player().dequeueRTSBattles()

    def _goToQueueUI(self):
        g_eventDispatcher.loadRTSBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if self.__queueReloaded:
            self.__queueReloaded = False
            self.__rtsController.runRTSQueue()
        else:
            g_eventDispatcher.loadHangar()

    def __getRosterVehicles(self):
        vehiclesCDs = self.__rtsController.getRoster(ARENA_BONUS_TYPE.RTS).vehicles
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.SPECIFIC_BY_CD(vehiclesCDs)
        return self.__itemsCache.items.getVehicles(criteria).values()
