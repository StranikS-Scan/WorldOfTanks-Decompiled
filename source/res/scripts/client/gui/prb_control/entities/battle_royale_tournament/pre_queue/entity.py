# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale_tournament/pre_queue/entity.py
import logging
from constants import PREBATTLE_TYPE
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from constants import QUEUE_TYPE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import g_eventBus
from gui.shared import events
from gui.prb_control import prb_getters
from gui.impl.gen import R
from helpers import dependency
from gui.ranked_battles.constants import PrimeTimeStatus
from skeletons.gui.game_control import IBattleRoyaleTournamentController
from skeletons.gui.impl import IGuiLoader
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint
from gui.prb_control.entities.battle_royale_tournament.pre_queue.action_validator import BattleRoyaleTournamentActionsValidator
from gui.prb_control.entities.battle_royale.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from gui.prb_control.entities.battle_royale_tournament.pre_queue.permissions import BattleRoyaleTournamentPermissions
from gui.prb_control.entities.special_mode.pre_queue import entity as spec_entry
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
_logger = logging.getLogger(__name__)

class _BattleRoyaleTournamentSubscriber(spec_entry.SpecialModeSubscriber):

    def subscribe(self, entity):
        g_playerEvents.onEnqueuedBattleRoyaleTournament += entity.onEnqueued
        g_playerEvents.onDequeuedBattleRoyaleTournament += entity.onDequeued
        g_playerEvents.onEnqueuedBattleRoyaleTournamentFailure += entity.onEnqueueError
        g_playerEvents.onKickedFromBattleRoyaleTournamentQueue += entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena += entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure += entity.onArenaJoinFailure
        super(_BattleRoyaleTournamentSubscriber, self).subscribe(entity)

    def unsubscribe(self, entity):
        g_playerEvents.onEnqueuedBattleRoyaleTournament -= entity.onEnqueued
        g_playerEvents.onDequeuedBattleRoyaleTournament -= entity.onDequeued
        g_playerEvents.onEnqueuedBattleRoyaleTournamentFailure -= entity.onEnqueueError
        g_playerEvents.onKickedFromBattleRoyaleTournamentQueue -= entity.onKickedFromQueue
        g_playerEvents.onKickedFromArena -= entity.onKickedFromArena
        g_playerEvents.onArenaJoinFailure -= entity.onArenaJoinFailure
        super(_BattleRoyaleTournamentSubscriber, self).unsubscribe(entity)


class BattleRoyaleTournamentEntryPoint(PreQueueEntryPoint):
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)

    def __init__(self):
        super(BattleRoyaleTournamentEntryPoint, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT)

    def select(self, ctx, callback=None):
        if not self.__battleRoyaleTournamentController.isAvailable():
            if callback is not None:
                callback(False)
            g_prbCtrlEvents.onPreQueueJoinFailure(PRE_QUEUE_JOIN_ERRORS.DISABLED)
            return
        else:
            super(BattleRoyaleTournamentEntryPoint, self).select(ctx, callback)
            return

    def _getFilterStates(self):
        return (PrimeTimeStatus.NOT_SET,)


class BattleRoyaleTournamentEntity(PreQueueEntity):
    __battleRoyaleTournamentController = dependency.descriptor(IBattleRoyaleTournamentController)
    __gui = dependency.descriptor(IGuiLoader)

    def __init__(self):
        super(BattleRoyaleTournamentEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT, _BattleRoyaleTournamentSubscriber())
        self.__watcher = None
        self.__prebatleWindow = False
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        result = super(BattleRoyaleTournamentEntity, self).init(ctx)
        return result

    def isPlayerJoined(self, ctx):
        if ctx.getEntityType() != PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT:
            return False
        if ctx.getID() != self.__battleRoyaleTournamentController.getTournamentID():
            self.__battleRoyaleTournamentController.leaveCurrentAndJoinToAnotherTournament(ctx.getID())
        return True

    def canInvite(self, prbType):
        return prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES

    def resetPlayerState(self):
        super(BattleRoyaleTournamentEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def isInQueue(self):
        return prb_getters.isInBattleRoyaleTournamentQueue()

    def showGUI(self, ctx=None):
        pass

    def fini(self, ctx=None, woEvents=False):
        if ctx and self.__battleRoyaleTournamentController.isSelected():
            self.__battleRoyaleTournamentController.leaveBattleRoyaleTournament()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        self.storage.suspend()
        if g_currentPreviewVehicle.isPresent():
            reqFlags = FUNCTIONAL_FLAG.LOAD_PAGE | FUNCTIONAL_FLAG.SWITCH | FUNCTIONAL_FLAG.TRAINING
            if ctx and not ctx.hasFlags(reqFlags):
                g_eventDispatcher.loadHangar()
        return super(BattleRoyaleTournamentEntity, self).fini(ctx, woEvents)

    @prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)
    def storage(self):
        return None

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        return SpecialModeQueueCtx(self._queueType, invID, waitingID='prebattle/join')

    def getPermissions(self, pID=None, **kwargs):
        return BattleRoyaleTournamentPermissions(self.isInQueue())

    def _createActionsValidator(self):
        return BattleRoyaleTournamentActionsValidator(self)

    def _doQueue(self, ctx):
        self.__battleRoyaleTournamentController.ready(ctx.getVehicleInventoryID())
        _logger.debug('Sends request on queuing to the Battle Royale - %r', ctx)

    def _doDequeue(self, ctx):
        self.__battleRoyaleTournamentController.notReady()
        _logger.debug('Sends request on dequeuing from the Battle Royale')

    def _goToQueueUI(self):
        if not self.__prebatleWindow:
            from gui.impl.lobby.battle_royale.pre_battle import PreBattleView
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.battle_royale.PreBattleView(), PreBattleView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__prebatleWindow = True
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if self.__prebatleWindow:
            self.__prebatleWindow = False
            views = self.__gui.windowsManager.findViews(self.__findSpectatorPreBattleView)
            if views:
                views[0].destroyWindow()

    @staticmethod
    def __findSpectatorPreBattleView(view):
        return str(view).find('PreBattleView') != -1
