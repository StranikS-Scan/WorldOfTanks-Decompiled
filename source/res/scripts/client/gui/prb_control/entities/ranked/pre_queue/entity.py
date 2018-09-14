# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/pre_queue/entity.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
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
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared.event_dispatcher import showRankedPrimeTimeWindow
from helpers import dependency, i18n, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.connection_mgr import IConnectionManager

class RankedSubscriber(PreQueueSubscriber):
    """
    Ranked battles events subscriber
    """

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
    """
    Ranked battle entry point
    """
    connectionMgr = dependency.descriptor(IConnectionManager)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANKED, QUEUE_TYPE.RANKED)

    def select(self, ctx, callback=None):
        status, _ = self.rankedController.getPrimeTimeStatus()
        if status in (PRIME_TIME_STATUS.DISABLED, PRIME_TIME_STATUS.FROZEN, PRIME_TIME_STATUS.NO_SEASON):
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.RANKED_NOTIFICATION_NOTAVAILABLE), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif status in self._getFilterStates():
            showRankedPrimeTimeWindow()
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(RankedEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PRIME_TIME_STATUS.NOT_SET, PRIME_TIME_STATUS.NOT_AVAILABLE)


class RankedForcedEntryPoint(RankedEntryPoint):
    """
    Ranked battle forced entry point
    """

    def _getFilterStates(self):
        return (PRIME_TIME_STATUS.NOT_SET,)


class RankedEntity(PreQueueEntity):
    """
    Ranked battle entity
    """
    settingsCore = dependency.descriptor(ISettingsCore)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self):
        super(RankedEntity, self).__init__(FUNCTIONAL_FLAG.RANKED, QUEUE_TYPE.RANKED, RankedSubscriber())
        self.__watcher = None
        self.__isPrimeTime = False
        return

    @prequeue_storage_getter(QUEUE_TYPE.RANKED)
    def storage(self):
        """
        Prebattle storage getter property
        """
        return None

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = RankedVehiclesWatcher()
        self.__watcher.start()
        result = super(RankedEntity, self).init(ctx)
        if not result & FUNCTIONAL_FLAG.LOAD_PAGE:
            result |= self.__processWelcome()
        SoundGroups.g_instance.playSound2D('gui_rb_rank_Entrance')
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

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        SoundGroups.g_instance.playSound2D('gui_rb_rank_Exit')
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
        assert pID is None, 'Current player has no any player in that mode'
        return RankedPermissions(self.isInQueue())

    def _createActionsValidator(self):
        return RankedActionsValidator(self)

    def _createScheduler(self):
        return RankedScheduler(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueRanked(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the ranked battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueRanked()
        LOG_DEBUG('Sends request on dequeuing from the ranked battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        assert invID, 'Inventory ID of vehicle can not be zero'
        return RankedQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def __processWelcome(self):
        """
        Processes state and display welcome view if wasn't shown before
        :return: process functional flag result
        """
        defaults = AccountSettings.getFilterDefault(GUI_START_BEHAVIOR)
        filters = self.settingsCore.serverSettings.getSection(GUI_START_BEHAVIOR, defaults)
        if not filters['isRankedWelcomeViewShowed']:
            g_eventDispatcher.loadRanked()
            return FUNCTIONAL_FLAG.LOAD_PAGE
        return FUNCTIONAL_FLAG.UNDEFINED
