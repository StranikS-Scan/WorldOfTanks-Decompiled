# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/winback/pre_queue/entity.py
import logging
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import BaseVehiclesWatcher
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.entities.winback.pre_queue.permissions import WinbackPermissions
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class WinbackEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(WinbackEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.WINBACK)


class WinbackEntity(PreQueueEntity):

    def __init__(self):
        super(WinbackEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.WINBACK, PreQueueSubscriber())
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.WINBACK)()
        return

    def init(self, ctx=None):
        self.__watcher = BaseVehiclesWatcher()
        self.__watcher.start()
        self.storage.release()
        return super(WinbackEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        if not woEvents:
            g_eventDispatcher.loadHangar()
        return super(WinbackEntity, self).fini(ctx, woEvents)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(WinbackEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.WINBACK else super(WinbackEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        return WinbackPermissions(self.isInQueue())

    def _doQueue(self, ctx):
        BigWorld.player().enqueueWinback(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the winback battle %s', str(ctx))

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueWinback()
        _logger.debug('Sends request on dequeuing from the winback battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
