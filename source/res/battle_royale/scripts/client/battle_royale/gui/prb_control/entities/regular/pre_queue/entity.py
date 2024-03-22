# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/regular/pre_queue/entity.py
import logging
import BigWorld
import typing
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getRoyaleFightBtnTooltipData
from gui.Scaleform.settings import TOOLTIP_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.pre_queue.ctx import JoinPreQueueModeCtx
from skeletons.gui.game_control import IBattleRoyaleController
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from battle_royale.gui.prb_control.entities.regular.pre_queue.actions_validator import BattleRoyaleActionsValidator
from battle_royale.gui.prb_control.entities.regular.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from battle_royale.gui.prb_control.entities.regular.pre_queue.permissions import BattleRoyalePermissions
from battle_royale.gui.prb_control.entities.regular.scheduler import RoyaleScheduler
from battle_royale.gui.constants import SUB_MODE_ID_KEY, BattleRoyaleSubMode
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
_logger = logging.getLogger(__name__)

class JoinBRPreQueueModeCtx(JoinPreQueueModeCtx):
    __slots__ = ('__selectedSubModeID',)

    def __init__(self, queueType, selectedSubModeID, flags=FUNCTIONAL_FLAG.UNDEFINED, waitingID=''):
        super(JoinBRPreQueueModeCtx, self).__init__(queueType=queueType, flags=flags, waitingID=waitingID)
        self.__selectedSubModeID = selectedSubModeID

    def getSelectedSubModeID(self):
        return self.__selectedSubModeID


class BRQueueCtx(SpecialModeQueueCtx):

    def __init__(self, entityType, vInventoryID, currentSubModeID, waitingID=''):
        super(BRQueueCtx, self).__init__(entityType, vInventoryID, waitingID)
        self.__currentSubModeID = currentSubModeID

    def getCurrentSubModeID(self):
        return self.__currentSubModeID


class BattleRoyaleEntryPoint(PreQueueEntryPoint):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BattleRoyaleEntryPoint, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE)
        self.__selectedSubModeID = BattleRoyaleSubMode.SOLO_MODE_ID

    def setExtData(self, extData):
        self.__selectedSubModeID = extData.get(SUB_MODE_ID_KEY, BattleRoyaleSubMode.SOLO_MODE_ID)

    def select(self, ctx, callback=None):
        neededSubModeID = ctx.getSelectedSubModeID()
        if not self.__battleRoyaleController.isEnabled():
            _logger.error('Battle Royale Controller is Disabled')
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif neededSubModeID is None or neededSubModeID not in BattleRoyaleSubMode.ALL_RANGE:
            _logger.error('Trying select sub mode not in BattleRoyaleSubMode.ALL_RANGE %s.', neededSubModeID)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            self.__battleRoyaleController.setCurrentSubModeID(neededSubModeID)
            super(BattleRoyaleEntryPoint, self).select(ctx, callback)
            return

    def makeDefCtx(self):
        return JoinBRPreQueueModeCtx(self._queueType, self.__selectedSubModeID, flags=self.getFunctionalFlags())

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class BattleRoyaleEntity(PreQueueEntity):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    def __init__(self):
        super(BattleRoyaleEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE, PreQueueSubscriber())
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        result = super(BattleRoyaleEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        g_eventDispatcher.loadHangar()
        return super(BattleRoyaleEntity, self).fini(ctx, woEvents)

    def resetPlayerState(self):
        super(BattleRoyaleEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        currentSubModeID = self.__battleRoyaleController.getCurrentSubModeID()
        return BRQueueCtx(self._queueType, invID, currentSubModeID, waitingID='prebattle/join')

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.BATTLE_ROYALE:
            self.__battleRoyaleController.setCurrentSubModeID(action.extData.get(SUB_MODE_ID_KEY, BattleRoyaleSubMode.SOLO_MODE_ID))
            return SelectResult(True, None)
        else:
            return super(BattleRoyaleEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        return BattleRoyalePermissions(self.isInQueue())

    def getFightBtnTooltipData(self, isStateDisabled):
        if isStateDisabled:
            return (getRoyaleFightBtnTooltipData(self.canPlayerDoAction()), False)
        return (TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_ADVANCED, True) if g_currentVehicle.isOnlyForBattleRoyaleBattles() else super(BattleRoyaleEntity, self).getFightBtnTooltipData(isStateDisabled)

    def getSquadBtnTooltipData(self):
        if self.getPermissions().canCreateSquad():
            header = backport.text(R.strings.platoon.headerButton.tooltips.battleRoyaleSquad.header())
            body = backport.text(R.strings.platoon.headerButton.tooltips.battleRoyaleSquad.body())
            return (makeTooltip(header, body), TOOLTIP_TYPES.COMPLEX)
        return super(BattleRoyaleEntity, self).getSquadBtnTooltipData()

    def _createActionsValidator(self):
        return BattleRoyaleActionsValidator(self)

    def _createScheduler(self):
        return RoyaleScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().AccountBattleRoyaleComponent.enqueueBattleRoyale(ctx)
        _logger.debug('Sends request on queuing to the Battle Royale - %r', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().AccountBattleRoyaleComponent.dequeueBattleRoyale()
        _logger.debug('Sends request on dequeuing from the Battle Royale')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
