# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from last_stand.gui.prb_control.entities.pre_queue.actions_validator import LastStandActionsValidator
from last_stand.gui.prb_control.entities.pre_queue.ctx import LastStandQueueCtx
from last_stand.gui.prb_control.entities.pre_queue.scheduler import LastStandBattleScheduler
from last_stand.gui.ls_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from last_stand.gui.prb_control.entities.vehicle_switcher import VehicleSwitcher
from last_stand.gui.prb_control.entities.vehicles_watcher import VehiclesWatcher
from last_stand.gui.shared.event_dispatcher import showHangar
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand_common.last_stand_constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from last_stand.skeletons.ls_controller import ILSController

class LastStandEntryPoint(PreQueueEntryPoint):
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(LastStandEntryPoint, self).__init__(FUNCTIONAL_FLAG.LAST_STAND, self.__difficultyLevelCtrl.getCurrentQueueType())


@dependency.replace_none_kwargs(ctrl=ILSController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class LastStandEntity(PreQueueEntity, VehicleSwitcher):
    lsCtrl = dependency.descriptor(ILSController)
    __difficultyLevelCtrl = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(LastStandEntity, self).__init__(FUNCTIONAL_FLAG.LAST_STAND, self.currentQueueType, PreQueueSubscriber())
        self.__watcher = None
        return

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
        self._updateVehiclesWatcher()
        return super(LastStandEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        self.__difficultyLevelCtrl.onChangeDifficultyLevel -= self._updateEntityType
        self.stopSwitcher()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(LastStandEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.LAST_STAND else super(LastStandEntity, self).doSelectAction(action)

    @property
    def _accountComponent(self):
        return BigWorld.player().LSAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(self.currentQueueType, ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the  LastStand battles', self.currentQueueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(self.currentQueueType)
        LOG_DEBUG('Sends request on dequeuing from the LastStand battles', self.currentQueueType)

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if not self.lsCtrl.isAvailable():
            self.lsCtrl.selectRandomMode()
        else:
            showHangar()

    def _goToHangar(self):
        showHangar()

    def _makeQueueCtxByAction(self, action=None):
        return LastStandQueueCtx(g_currentVehicle.item.invID, entityType=self.currentQueueType, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return LastStandActionsValidator(self)

    def _createScheduler(self):
        return LastStandBattleScheduler(self)

    def _updateEntityType(self, *args, **kwargs):
        self._queueType = self.currentQueueType
        self.storage.queueType = self._queueType
        self._updateVehiclesWatcher()
        self.selectModeVehicle()

    def _updateVehiclesWatcher(self):
        watcherType = VehiclesWatcher
        if isinstance(self.__watcher, watcherType):
            return
        else:
            if self.__watcher is not None:
                self.__watcher.stop()
            self.__watcher = watcherType()
            self.__watcher.start()
            return
