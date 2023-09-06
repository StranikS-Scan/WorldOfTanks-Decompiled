# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/tournament/pre_queue/entity.py
import logging
from constants import PREBATTLE_TYPE
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from constants import QUEUE_TYPE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import g_eventBus
from gui.shared import events
from gui.impl.gen import R
from helpers import dependency
from gui.periodic_battles.models import PrimeTimeStatus
from skeletons.gui.game_control import IBattleRoyaleTournamentController
from skeletons.gui.impl import IGuiLoader
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity, PreQueueEntryPoint, PreQueueSubscriber
from battle_royale.gui.prb_control.entities.tournament.pre_queue.action_validator import BattleRoyaleTournamentActionsValidator
from battle_royale.gui.prb_control.entities.regular.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from battle_royale.gui.prb_control.entities.tournament.pre_queue.permissions import BattleRoyaleTournamentPermissions
from gui.prb_control.entities.special_mode.pre_queue.ctx import SpecialModeQueueCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PRE_QUEUE_JOIN_ERRORS
from gui.prb_control.storages import prequeue_storage_getter
_logger = logging.getLogger(__name__)

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
        super(BattleRoyaleTournamentEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT, PreQueueSubscriber())
        self.__watcher = None
        self.__prebatleWindow = False
        self.storage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        result = super(BattleRoyaleTournamentEntity, self).init(ctx)
        return result

    def isPlayerJoined(self, ctx):
        return False if ctx.getEntityType() != PREBATTLE_TYPE.BATTLE_ROYALE_TOURNAMENT else True

    def canInvite(self, prbType):
        return prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES

    def resetPlayerState(self):
        super(BattleRoyaleTournamentEntity, self).resetPlayerState()
        g_eventDispatcher.loadHangar()

    def showGUI(self, ctx=None):
        self.__battleRoyaleTournamentController.leaveCurrentAndJoinToAnotherTournament(ctx.getID())

    def fini(self, ctx=None, woEvents=False):
        self.__battleRoyaleTournamentController.resetReady()
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
            from battle_royale.gui.impl.lobby.views.pre_battle import PreBattleView
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.battle_royale.lobby.views.PreBattleView(), PreBattleView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
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
