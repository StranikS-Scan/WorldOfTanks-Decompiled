# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/prb_control/entities/pre_queue/entity.py
from __future__ import absolute_import
import BigWorld
from halloween.gui.prb_control.entities import vehicleAbilitiesCheck
from halloween.gui.prb_control.entities.pre_queue.actions_validator import HalloweenActionsValidator
from halloween.gui.prb_control.entities.pre_queue.ctx import HalloweenQueueCtx
from halloween.gui.prb_control.entities.pre_queue.scheduler import HalloweenBattleScheduler
from halloween.gui.halloween_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from halloween.gui.prb_control.entities.vehicle_switcher import VehicleSwitcher
from halloween.gui.prb_control.entities.vehicles_watcher import HalloweenVehiclesWatcher
from halloween.gui.shared.event_dispatcher import showHangar
from halloween.skeletons.difficulty_level_controller import IDifficultyLevelController
from halloween_common.halloween_constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from halloween.skeletons.halloween_controller import IHalloweenController

class HalloweenEntryPoint(PreQueueEntryPoint):
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(HalloweenEntryPoint, self).__init__(FUNCTIONAL_FLAG.HALLOWEEN, self.__difficultyLevelCtrl.getCurrentQueueType())


@dependency.replace_none_kwargs(ctrl=IHalloweenController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class HalloweenEntity(PreQueueEntity, VehicleSwitcher):
    __halloweenCtrl = dependency.descriptor(IHalloweenController)
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(HalloweenEntity, self).__init__(FUNCTIONAL_FLAG.HALLOWEEN, self.currentQueueType, PreQueueSubscriber())

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    @property
    def currentQueueType(self):
        return self.__difficultyLevelCtrl.getCurrentQueueType()

    def init(self, ctx=None):
        self.__difficultyLevelCtrl.onChangeDifficultyLevel += self._updateEntityType
        self.storage.queueType = self.currentQueueType
        self.startSwitcher()
        self.__watcher = HalloweenVehiclesWatcher()
        self.__watcher.start()
        return super(HalloweenEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        self.__difficultyLevelCtrl.onChangeDifficultyLevel -= self._updateEntityType
        self.stopSwitcher()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(HalloweenEntity, self).fini(ctx=ctx, woEvents=woEvents)

    @vehicleAbilitiesCheck
    def queue(self, ctx, callback=None):
        super(HalloweenEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.HALLOWEEN else super(HalloweenEntity, self).doSelectAction(action)

    @property
    def _accountComponent(self):
        return BigWorld.player().HalloweenAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(self.currentQueueType, ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the  Halloween battles', self.currentQueueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(self.currentQueueType)
        LOG_DEBUG('Sends request on dequeuing from the Halloween battles', self.currentQueueType)

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if not self.__halloweenCtrl.isAvailable():
            self.__halloweenCtrl.selectRandomMode()
        else:
            showHangar()

    def _goToHangar(self):
        showHangar()

    def _makeQueueCtxByAction(self, action=None):
        return HalloweenQueueCtx(g_currentVehicle.item.invID, entityType=self.currentQueueType, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return HalloweenActionsValidator(self)

    def _createScheduler(self):
        return HalloweenBattleScheduler(self)

    def _updateEntityType(self, *args, **kwargs):
        self._queueType = self.currentQueueType
        self.storage.queueType = self._queueType
