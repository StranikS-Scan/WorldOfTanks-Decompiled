# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/entity.py
import logging
import typing
import BigWorld
import constants
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl import backport
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.ranked.pre_queue.actions_validator import RankedActionsValidator
from gui.prb_control.entities.ranked.pre_queue.ctx import RankedQueueCtx
from gui.prb_control.entities.ranked.pre_queue.permissions import RankedPermissions
from gui.prb_control.entities.ranked.pre_queue.scheduler import RankedScheduler
from gui.prb_control.entities.ranked.pre_queue.vehicles_watcher import RankedVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, PRE_QUEUE_JOIN_ERRORS
from account_helpers.AccountSettings import AccountSettings, GUI_START_BEHAVIOR
from gui.prb_control.storages import prequeue_storage_getter
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared.event_dispatcher import showRankedPrimeTimeWindow
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.connection_mgr import IConnectionManager
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.prb_control.storages.local_storage import LocalStorage
_logger = logging.getLogger(__name__)

class RankedSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedRanked += entity.onEnqueued
        g_playerEvents.onDequeuedRanked += entity.onDequeued
        g_playerEvents.onEnqueuedRankedFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromRankedQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedRanked -= entity.onEnqueued
        g_playerEvents.onDequeuedRanked -= entity.onDequeued
        g_playerEvents.onEnqueuedRankedFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromRankedQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class RankedEntryPoint(PreQueueEntryPoint):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(RankedEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANKED, QUEUE_TYPE.RANKED)

    def select(self, ctx, callback=None):
        status, _, _ = self.__rankedController.getPrimeTimeStatus()
        if status in (PrimeTimeStatus.DISABLED, PrimeTimeStatus.FROZEN, PrimeTimeStatus.NO_SEASON):
            SystemMessages.pushMessage(backport.text(R.strings.system_messages.ranked.notification.notAvailable()), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif not self.__isFirstEnter() and status in self._getFilterStates() and not constants.IS_CHINA:
            showRankedPrimeTimeWindow()
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(RankedEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET, PrimeTimeStatus.NOT_AVAILABLE)

    def __isFirstEnter(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        return not filters['isRankedWelcomeViewShowed']


class RankedForcedEntryPoint(RankedEntryPoint):

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class RankedEntity(PreQueueEntity):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedEntity, self).__init__(FUNCTIONAL_FLAG.RANKED, QUEUE_TYPE.RANKED, RankedSubscriber())
        self.__watcher = None
        return

    @prequeue_storage_getter(QUEUE_TYPE.RANKED)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = RankedVehiclesWatcher()
        self.__watcher.start()
        result = super(RankedEntity, self).init(ctx)
        if not result & FUNCTIONAL_FLAG.LOAD_PAGE:
            result |= self.__processWelcome()
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents:
            if not self.canSwitch(ctx):
                if ctx is None or not ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE):
                    g_eventDispatcher.loadHangar()
        return super(RankedEntity, self).fini(ctx, woEvents)

    def invalidate(self):
        self.__processWelcome()

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(RankedEntity, self).leave(ctx, callback)

    def isInQueue(self):
        return prb_getters.isInRankedQueue()

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(RankedEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name in (PREBATTLE_ACTION_NAME.RANKED, PREBATTLE_ACTION_NAME.RANKED_FORCED) else super(RankedEntity, self).doSelectAction(action)

    def getPermissions(self, pID=None, **kwargs):
        return RankedPermissions(self.isInQueue())

    def _createActionsValidator(self):
        return RankedActionsValidator(self)

    def _createScheduler(self):
        return RankedScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueRanked(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the ranked battle %s', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueRanked()
        _logger.debug('Sends request on dequeuing from the ranked battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        return RankedQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def __processWelcome(self):
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.__settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        rankedWelcomeCallback = self.__rankedController.getRankedWelcomeCallback()
        if rankedWelcomeCallback is None:
            if not filters['isRankedWelcomeViewShowed']:
                g_eventDispatcher.loadRanked()
                return FUNCTIONAL_FLAG.LOAD_PAGE
            return FUNCTIONAL_FLAG.UNDEFINED
        else:
            rankedWelcomeCallback()
            self.__rankedController.clearRankedWelcomeCallback()
            return FUNCTIONAL_FLAG.LOAD_PAGE
