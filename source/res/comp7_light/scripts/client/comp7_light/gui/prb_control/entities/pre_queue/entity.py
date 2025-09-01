# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
import typing
from CurrentVehicle import g_currentVehicle
from comp7_light.gui.comp7_light_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from comp7_light.gui.prb_control.entities.comp7_light_prb_helpers import Comp7LightViewPresenter
from comp7_light.gui.prb_control.entities.pre_queue.actions_validator import Comp7LightActionsValidator
from comp7_light.gui.prb_control.entities.pre_queue.ctx import Comp7LightQueueCtx
from comp7_light.gui.prb_control.entities.pre_queue.permissions import Comp7LightPermissions
from comp7_light.gui.prb_control.entities.pre_queue.vehicles_watcher import Comp7LightVehiclesWatcher
from comp7_light.gui.prb_control.entities.scheduler import Comp7LightScheduler
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from comp7_light.gui.prb_control.storages.comp7_light_storage import Comp7LightStorage

class Comp7LightEntryPoint(PreQueueEntryPoint):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        super(Comp7LightEntryPoint, self).__init__(FUNCTIONAL_FLAG.COMP7_LIGHT, QUEUE_TYPE.COMP7_LIGHT)

    def select(self, ctx, callback=None):
        if not self.__comp7LightController.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            status, _, _ = self.__comp7LightController.getPrimeTimeStatus()
            if status in self._getUnavailableStates():
                if callback is not None:
                    callback(False)
                g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
                return
            super(Comp7LightEntryPoint, self).select(ctx, callback)
            return

    @staticmethod
    def _getUnavailableStates():
        return (PrimeTimeStatus.FROZEN,)


class Comp7LightEntity(PreQueueEntity):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def __init__(self):
        super(Comp7LightEntity, self).__init__(FUNCTIONAL_FLAG.COMP7_LIGHT, QUEUE_TYPE.COMP7_LIGHT, PreQueueSubscriber())
        self.__watcher = None
        self.__introPresenter = Comp7LightViewPresenter()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.COMP7_LIGHT)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = Comp7LightVehiclesWatcher()
        self.__watcher.start()
        self.__introPresenter.init()
        result = super(Comp7LightEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.__introPresenter.fini()
        self.__introPresenter = None
        return super(Comp7LightEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(Comp7LightEntity, self).leave(ctx, callback)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName in (PREBATTLE_ACTION_NAME.COMP7_LIGHT,) else super(Comp7LightEntity, self).doSelectAction(action)

    def getPermissions(self, *_):
        return Comp7LightPermissions(self.isInQueue())

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(Comp7LightEntity, self).queue(ctx, callback=callback)

    def _createActionsValidator(self):
        return Comp7LightActionsValidator(self)

    def _createScheduler(self):
        return Comp7LightScheduler(self)

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return Comp7LightQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def _doQueue(self, ctx):
        BigWorld.player().AccountComp7LightComponent.enqueueComp7Light(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the Competitive7x7 tier VIII', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountComp7LightComponent.dequeueComp7Light()
        LOG_DEBUG('Sends request on dequeuing from the Competitive7x7 tier VIII')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
