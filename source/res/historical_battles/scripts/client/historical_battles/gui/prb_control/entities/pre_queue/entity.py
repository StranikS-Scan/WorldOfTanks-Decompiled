# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/prb_control/entities/pre_queue/entity.py
import BigWorld
from historical_battles_common.hb_constants_extension import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.settings import PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.items import SelectResult
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from helpers import dependency
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from historical_battles.gui.prb_control.entities.pre_queue.ctx import HistoricalBattlesQueueCtx
from historical_battles.gui.prb_control.entities.pre_queue.actions_validator import HistoricalBattlesActionsValidator
from historical_battles.gui.shared.event_dispatcher import showHistoricalBattleQueueView, showHBHangar
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HistoricalBattlesEntryPoint(PreQueueEntryPoint):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        front = self.gameEventController.frontController.getSelectedFront()
        super(HistoricalBattlesEntryPoint, self).__init__(FUNCTIONAL_FLAG.HISTORICAL_BATTLES, front.getFrontQueueType())

    def select(self, ctx, callback=None):
        if not self.gameEventController.isEnabled():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(HistoricalBattlesEntryPoint, self).select(ctx, callback)
            return


class HistoricalBattlesEntity(PreQueueEntity):
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        front = self.gameEventController.frontController.getSelectedFront()
        super(HistoricalBattlesEntity, self).__init__(FUNCTIONAL_FLAG.HISTORICAL_BATTLES, front.getFrontQueueType(), PreQueueSubscriber())

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        showHBHangar()
        return super(HistoricalBattlesEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx and ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.queueType = QUEUE_TYPE.UNKNOWN
        return super(HistoricalBattlesEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        if action.actionName == PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES:
            showHBHangar()
            return SelectResult(True)
        return super(HistoricalBattlesEntity, self).doSelectAction(action)

    def updateEntityType(self):
        front = self.gameEventController.frontController.getSelectedFront()
        self._queueType = front.getFrontQueueType()

    @property
    def _accountComponent(self):
        return BigWorld.player().HBAccountComponent

    def _makeQueueCtxByAction(self, action=None):
        frontman = self.gameEventController.frontController.getSelectedFrontman()
        return HistoricalBattlesQueueCtx(frontman.getID(), frontman.getSelectedVehicle().intCD)

    def _doQueue(self, ctx):
        self._accountComponent.enqueueBattle(self._queueType, ctx.frontmanID, ctx.vehTypeCD)
        LOG_DEBUG('Sends request on queuing to historical battles', self._queueType, ctx)

    def _doDequeue(self, ctx):
        self._accountComponent.dequeueBattle(self._queueType)
        LOG_DEBUG('Sends request on dequeuing from historical battles', self._queueType)

    def _goToQueueUI(self):
        showHistoricalBattleQueueView()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if self.gameEventController.isEnabled():
            showHBHangar()
        else:
            closeEvent()

    def _createActionsValidator(self):
        return HistoricalBattlesActionsValidator(self)

    @property
    def needsCheckVehicleForBattle(self):
        return False
