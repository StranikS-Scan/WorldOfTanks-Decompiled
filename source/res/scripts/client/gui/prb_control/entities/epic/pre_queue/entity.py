# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/pre_queue/entity.py
import BigWorld
import constants
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.entities.base.unit.ctx import LeaveUnitCtx
from gui.prb_control.entities.epic.pre_queue.actions_validator import EpicActionsValidator
from gui.prb_control.entities.epic.pre_queue.ctx import EpicQueueCtx
from gui.prb_control.entities.epic.pre_queue.vehicles_watcher import EpicVehiclesWatcher
from gui.prb_control.entities.epic.squad.entity import EpicSquadEntryPoint
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import event_dispatcher
from helpers import dependency, i18n
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IEpicBattleMetaGameController
from predefined_hosts import g_preDefinedHosts

class EpicSubscriber(PreQueueSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedEpic += entity.onEnqueued
        g_playerEvents.onDequeuedEpic += entity.onDequeued
        g_playerEvents.onEnqueuedEpicFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromEpicQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedEpic -= entity.onEnqueued
        g_playerEvents.onDequeuedEpic -= entity.onDequeued
        g_playerEvents.onEnqueuedEpicFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromEpicQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure


class EpicEntryPoint(PreQueueEntryPoint):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        super(EpicEntryPoint, self).__init__(FUNCTIONAL_FLAG.EPIC, QUEUE_TYPE.EPIC)

    def select(self, ctx, callback=None):
        status, _, _ = self.__epicController.getPrimeTimeStatus()
        if status in (PRIME_TIME_STATUS.DISABLED, PRIME_TIME_STATUS.FROZEN, PRIME_TIME_STATUS.NO_SEASON):
            SystemMessages.pushMessage(i18n.makeString(SYSTEM_MESSAGES.EPICBATTLES_NOTIFICATION_NOTAVAILABLE), type=SystemMessages.SM_TYPE.Error)
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        elif status in self._getFilterStates() and not constants.IS_CHINA and self.__isFrontlineAvailableOnDifferentPeriphery():
            event_dispatcher.showEpicBattlesPrimeTimeWindow()
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.NOT_AVAILABLE)
            return
        else:
            super(EpicEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PRIME_TIME_STATUS.NOT_SET, PRIME_TIME_STATUS.NOT_AVAILABLE)

    def __isFrontlineAvailableOnDifferentPeriphery(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        for _, _, _, peripheryID in hostsList:
            if peripheryID == self.__connectionMgr.peripheryID:
                continue
            primeTimeStatus, _, primeTimeNow = self.__epicController.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus != PRIME_TIME_STATUS.NOT_SET and primeTimeNow:
                return True

        return False


class EpicForcedEntryPoint(EpicEntryPoint):

    def _getFilterStates(self):
        return (PRIME_TIME_STATUS.NOT_SET,)


class EpicEntity(PreQueueEntity):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self):
        super(EpicEntity, self).__init__(FUNCTIONAL_FLAG.EPIC, QUEUE_TYPE.EPIC, EpicSubscriber())
        self.__watcher = None
        return

    def init(self, ctx=None):
        self.__epicController.onUpdated += self.__onEpicUpdated
        self.storage.release()
        self.__watcher = EpicVehiclesWatcher()
        self.__watcher.start()
        result = super(EpicEntity, self).init(ctx)
        return result

    @prequeue_storage_getter(QUEUE_TYPE.EPIC)
    def storage(self):
        return None

    def fini(self, ctx=None, woEvents=False):
        self.__epicController.onUpdated -= self.__onEpicUpdated
        if not woEvents:
            if not self.canSwitch(ctx):
                g_eventDispatcher.loadHangar()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(EpicEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        self.storage.suspend()
        super(EpicEntity, self).leave(ctx, callback)

    def isInQueue(self):
        return prb_getters.isInEpicQueue()

    def getQueueType(self):
        return QUEUE_TYPE.EPIC

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(EpicEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.EPIC, PREBATTLE_ACTION_NAME.EPIC_FORCED):
            return SelectResult(True)
        return SelectResult(True, EpicSquadEntryPoint(accountsToInvite=action.accountsToInvite)) if name == PREBATTLE_ACTION_NAME.SQUAD else super(EpicEntity, self).doSelectAction(action)

    def _createActionsValidator(self):
        return EpicActionsValidator(self)

    def _doQueue(self, ctx):
        BigWorld.player().enqueueEpic(ctx.getVehicleInventoryID())
        LOG_DEBUG('Sends request on queuing to the epic battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueEpic()
        LOG_DEBUG('Sends request on dequeuing from the epic battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return EpicQueueCtx(invID, waitingID='prebattle/join')

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()

    def __processWelcome(self):
        if not self.__epicController.isWelcomeScreenUpToDate(self.__settingsCore.serverSettings):
            g_eventDispatcher.loadEpicWelcome()
            return FUNCTIONAL_FLAG.LOAD_PAGE
        return FUNCTIONAL_FLAG.UNDEFINED

    def __onEpicUpdated(self, diff):
        if 'epic_config' not in diff:
            return
        status, _, _ = self.__epicController.getPrimeTimeStatus()
        isPlayable = self.__epicController.isEnabled() and not self.__epicController.isFrozen()
        if not isPlayable or not self.__epicController.hasAnySeason() or status is not PRIME_TIME_STATUS.AVAILABLE:
            ctx = LeaveUnitCtx(waitingID='prebattle/leave', flags=FUNCTIONAL_FLAG.EXIT, entityType=self.getEntityType())

            def showPrimeTime(_):
                if isPlayable:
                    event_dispatcher.showEpicBattlesPrimeTimeWindow()

            self.leave(ctx, callback=showPrimeTime)
