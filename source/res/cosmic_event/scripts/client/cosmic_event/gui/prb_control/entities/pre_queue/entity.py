# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
import typing
from adisp import adisp_process
from cosmic_event.gui.prb_control.entities.pre_queue.actions_validator import CosmicEventBattleActionsValidator
from cosmic_event.gui.prb_control.entities.pre_queue.ctx import CosmicEventBattleQueueCtx
from cosmic_event.gui.prb_control.entities.pre_queue.scheduler import CosmicEventBattleScheduler
from cosmic_event.gui.prb_control.prb_config import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event_common.cosmic_constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import prbDispatcherProperty
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.prb_control.entities.base.permissions import IPrbPermissions
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import REQUEST_TYPE
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
    from typing import Optional

@dependency.replace_none_kwargs(ctrl=ICosmicEventBattleController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class CosmicPermissions(IPrbPermissions):
    pass


class CosmicEventBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(CosmicEventBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.COSMIC_EVENT, QUEUE_TYPE.COSMIC_EVENT)


class CosmicEventBattleEntity(PreQueueEntity):
    __cosmicEventBattleCtrl = dependency.descriptor(ICosmicEventBattleController)
    _QUEUE_TIMEOUT_MSG_KEY = ''

    def __init__(self):
        super(CosmicEventBattleEntity, self).__init__(FUNCTIONAL_FLAG.COSMIC_EVENT, QUEUE_TYPE.COSMIC_EVENT, PreQueueSubscriber())

    @prbDispatcherProperty
    def _prbDispatcher(self):
        return None

    def init(self, ctx=None):
        self.__cosmicEventBattleCtrl.onPrbEnter()
        self._loadHangar()
        return super(CosmicEventBattleEntity, self).init(ctx=ctx)

    def leave(self, ctx, callback=None):
        super(CosmicEventBattleEntity, self).leave(ctx=ctx, callback=callback)
        self.__cosmicEventBattleCtrl.onPrbLeave()

    def fini(self, ctx=None, woEvents=False):
        return super(CosmicEventBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.COSMIC_EVENT else super(CosmicEventBattleEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        return CosmicPermissions()

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__cosmicEventBattleCtrl.isEnabled else super(CosmicEventBattleEntity, self).getConfirmDialogMeta(ctx)

    @property
    def needsCheckVehicleForBattle(self):
        return False

    def _loadHangar(self):
        if self.__cosmicEventBattleCtrl.isEnabled:
            self.__cosmicEventBattleCtrl.openEventLobby()
        else:
            g_eventDispatcher.loadHangar()

    def _doQueue(self, ctx):
        BigWorld.player().AccountCosmicEventComponent.enqueue(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the cosmic event battles', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountCosmicEventComponent.dequeue()
        LOG_DEBUG('Sends request on dequeuing from the cosmic event battles')

    def _goToQueueUI(self):
        self.__cosmicEventBattleCtrl.openQueueView()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        uiLoader = dependency.instance(IGuiLoader)
        contentID = R.views.cosmic_event.lobby.queue_view.QueueView()
        view = uiLoader.windowsManager.getViewByLayoutID(contentID)
        if view:
            view.destroy()
        self._loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        vehicle = self.__cosmicEventBattleCtrl.getEventVehicle()
        return CosmicEventBattleQueueCtx(vehicle.invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return CosmicEventBattleActionsValidator(self)

    def _createScheduler(self):
        return CosmicEventBattleScheduler(self)

    def onKickedFromQueue(self, queueType, *args):
        if queueType != self._queueType:
            return
        if self._requestCtx.getRequestType() in (REQUEST_TYPE.QUEUE, REQUEST_TYPE.DEQUEUE):
            self._requestCtx.stopProcessing(True)
        self._invokeListeners('onKickedFromQueue', self.getQueueType(), *args)
        self._exitFromQueueUI()
        if self._isNeedToShowSystemMessage():
            SystemMessages.pushI18nMessage(backport.text(R.strings.cosmicEvent.arena_start_errors.prb.kick.timeout()), type=SystemMessages.SM_TYPE.Warning)
        if not self.__cosmicEventBattleCtrl.isEnabled:
            self._doLeave()

    @adisp_process
    def _doLeave(self, isExit=True):
        yield self._prbDispatcher.doLeaveAction(LeavePrbAction(isExit))
