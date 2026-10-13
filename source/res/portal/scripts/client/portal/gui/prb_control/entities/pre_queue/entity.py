# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from helpers import dependency
from portal_common.portal_constants import QUEUE_TYPE
from portal.gui.portal_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from portal.gui.shared.event_dispatcher import showPortalBattleQueueView
from portal.gui.prb_control.entities.pre_queue.actions_validator import PortalBattleActionsValidator
from portal.gui.prb_control.entities.pre_queue.ctx import PortalBattleQueueCtx
from portal.gui.prb_control.entities.pre_queue.scheduler import PortalBattleScheduler
from portal.skeletons.portal_event_controller import IPortalEventController

class PortalBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(PortalBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.PORTAL, QUEUE_TYPE.PORTAL)


@dependency.replace_none_kwargs(ctrl=IPortalEventController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class PortalBattleEntity(PreQueueEntity):
    __portalBattlesCtrl = dependency.descriptor(IPortalEventController)

    def __init__(self):
        super(PortalBattleEntity, self).__init__(FUNCTIONAL_FLAG.PORTAL, QUEUE_TYPE.PORTAL, PreQueueSubscriber())
        self.__portalBattlesCtrl.onPrbEnter()

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        if not self.__portalBattlesCtrl.isAvailable():
            self.__portalBattlesCtrl.selectRandomBattle()
        return super(PortalBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(PortalBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.PORTAL_BATTLE else super(PortalBattleEntity, self).doSelectAction(action)

    def canInvite(self, prbType):
        return self.__portalBattlesCtrl.isAvailable()

    @property
    def _accountComponent(self):
        return BigWorld.player().PortalAccountComponent

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(self._queueType, ctx.getVehicleInventoryID(), ctx.battleLevel)
        LOG_DEBUG('Sends request on queuing to the Portal battles', self._queueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(self._queueType)
        LOG_DEBUG('Sends request on dequeuing from the  Portal battles', self._queueType)

    def _goToQueueUI(self):
        showPortalBattleQueueView()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if self.__portalBattlesCtrl.isAvailable():
            g_eventDispatcher.loadHangar()
        else:
            self.__portalBattlesCtrl.selectRandomBattle()

    def _makeQueueCtxByAction(self, action=None):
        battleLevel = self.__portalBattlesCtrl.battleLevel
        return PortalBattleQueueCtx(g_currentVehicle.item.invID, battleLevel, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return PortalBattleActionsValidator(self)

    def _createScheduler(self):
        return PortalBattleScheduler(self)

    def leave(self, ctx, callback=None):
        super(PortalBattleEntity, self).leave(ctx=ctx, callback=callback)
        self.__portalBattlesCtrl.onPrbLeave()
