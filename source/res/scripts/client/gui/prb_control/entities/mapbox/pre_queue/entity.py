# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/mapbox/pre_queue/entity.py
import typing
import BigWorld
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.entities.mapbox.pre_queue.vehicles_watcher import MapboxVehiclesWatcher
from gui.prb_control.entities.mapbox.pre_queue.actions_validator import MapboxActionsValidator
from gui.prb_control.entities.mapbox.pre_queue.permissions import MapboxPermissions
from gui.prb_control.entities.mapbox.scheduler import MapboxScheduler
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.models import PrimeTimeStatus
from helpers import dependency
from skeletons.gui.game_control import IMapboxController
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.mapbox_storage import MapboxStorage

class MapboxEntryPoint(PreQueueEntryPoint):
    __mapboxController = dependency.descriptor(IMapboxController)

    def __init__(self):
        super(MapboxEntryPoint, self).__init__(FUNCTIONAL_FLAG.MAPBOX, QUEUE_TYPE.MAPBOX)

    def select(self, ctx, callback=None):
        if not self.__mapboxController.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(MapboxEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class MapboxEntity(PreQueueEntity):

    def __init__(self):
        super(MapboxEntity, self).__init__(FUNCTIONAL_FLAG.MAPBOX, QUEUE_TYPE.MAPBOX, PreQueueSubscriber())
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.MAPBOX)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = MapboxVehiclesWatcher()
        self.__watcher.start()
        result = super(MapboxEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        return super(MapboxEntity, self).fini(ctx, woEvents)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(MapboxEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.MAPBOX else super(MapboxEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        return MapboxPermissions(self.isInQueue())

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return MapboxActionsValidator(self)

    def _createScheduler(self):
        return MapboxScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueMapbox(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to Mapbox', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueMapbox()
        LOG_DEBUG('Sends request on dequeuing from Mapbox')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
