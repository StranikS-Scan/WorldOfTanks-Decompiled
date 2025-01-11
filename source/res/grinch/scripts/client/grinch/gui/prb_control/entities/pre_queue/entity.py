# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from grinch.gui.grinch_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from grinch.gui.prb_control.entities.pre_queue.actions_validator import GrinchActionsValidator
from grinch.gui.prb_control.entities.pre_queue.ctx import GrinchQueueCtx
from grinch.gui.prb_control.entities.pre_queue.permissions import GrinchPermissions
from grinch.gui.prb_control.entities.pre_queue.scheduler import GrinchScheduler
from grinch.overrides.hangar_override import showHangar
from grinch_common.grinch_constants import QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from grinch.skeletons.battle_controller import IGrinchController

class GrinchEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(GrinchEntryPoint, self).__init__(FUNCTIONAL_FLAG.GRINCH, QUEUE_TYPE.GRINCH)


@dependency.replace_none_kwargs(ctrl=IGrinchController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class GrinchEntity(PreQueueEntity):
    __grinchCtrl = dependency.descriptor(IGrinchController)

    def __init__(self):
        super(GrinchEntity, self).__init__(FUNCTIONAL_FLAG.GRINCH, QUEUE_TYPE.GRINCH, PreQueueSubscriber())

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def getPermissions(self, pID=None, **kwargs):
        return GrinchPermissions(self.isInQueue())

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        if not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.GRINCH):
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.GRINCH)
        return super(GrinchEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(GrinchEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.GRINCH else super(GrinchEntity, self).doSelectAction(action)

    def canInvite(self, prbType):
        return self.__grinchCtrl.isAvailable()

    @property
    def _accountComponent(self):
        return BigWorld.player().GrinchAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(ctx.getVehicleInventoryID())

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle()

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        showHangar()

    def _goToHangar(self):
        showHangar()

    def _makeQueueCtxByAction(self, action=None):
        return GrinchQueueCtx(g_currentVehicle.item.invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return GrinchActionsValidator(self)

    def _createScheduler(self):
        return GrinchScheduler(self)
