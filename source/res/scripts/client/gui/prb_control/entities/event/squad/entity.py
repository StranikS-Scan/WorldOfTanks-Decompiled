# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
import BigWorld
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import rally_dialog_meta
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.event.squad.requester import EventUnitRequestProcessor
from gui.prb_control.entities.event.squad.scheduler import EventSquadScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from gui.prb_control import settings as prb_settings
from gui.shared.utils.decorators import ReprInjector
from skeletons.gui.game_event_controller import IGameEventController

@ReprInjector.withParent()
class EventSquadSettingsCtx(SquadSettingsCtx):
    __slots__ = ('_keepCurrentView',)

    def __init__(self, waitingID='', accountsToInvite=None, keepCurrentView=False):
        super(EventSquadSettingsCtx, self).__init__(PREBATTLE_TYPE.EVENT, waitingID, prb_settings.FUNCTIONAL_FLAG.UNDEFINED, accountsToInvite, False)
        self._keepCurrentView = keepCurrentView

    def getKeepCurrentView(self):
        return self._keepCurrentView


class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, accountsToInvite)
        self._keepCurrentView = False

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()

    def setKeepCurrentView(self, keepCurrentView):
        self._keepCurrentView = keepCurrentView

    def makeDefCtx(self):
        return EventSquadSettingsCtx(waitingID='prebattle/create', accountsToInvite=self._accountsToInvite, keepCurrentView=self._keepCurrentView)


class EventBattleSquadEntity(SquadEntity):
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.release()
        if ctx is not None:
            initCtx = ctx.getInitCtx()
            inBattleQueue = False
            fromEventSquad = isinstance(initCtx, EventSquadSettingsCtx)
            if not fromEventSquad or not initCtx.getKeepCurrentView():
                if self.getPlayerInfo().isReady and self.getFlags().isInQueue():
                    g_eventDispatcher.loadEventBattleQueue()
                    inBattleQueue = True
            if not inBattleQueue:
                g_eventDispatcher.loadEventHangar()
            ctx.addFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
        return super(EventBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx is not None:
            isEventSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH_FROM_EVENT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isEventSwitch or isSwitch and not isLoadPage:
                self.storage.suspend()
                g_eventDispatcher.loadHangar()
        return super(EventBattleSquadEntity, self).fini(ctx, woEvents)

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.EVENT_SQUAD, PREBATTLE_ACTION_NAME.EVENT_BATTLE):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def doBattleQueue(self, ctx, callback=None):
        if not self.getPlayerInfo().isReady:
            BigWorld.player().changeSelectedGeneral(self.gameEventController.getSelectedCommanderID())
        super(EventBattleSquadEntity, self).doBattleQueue(ctx, callback)

    def canPlayerDoAction(self):
        commander = self.gameEventController.getSelectedCommander()
        if commander is not None:
            if commander.getID() not in self.gameEventController.getCommanders():
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_COMMANDER_INACTIVE)
            if commander.isLocked():
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_COMMANDER_IS_LOCKED)
            if commander.isBlockedByEnergy():
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_NOT_ENOUGH_ENERGY)
        return self._actionsValidator.canPlayerDoAction() or ValidationResult()

    def getConfirmDialogMeta(self, ctx):
        if not self.eventsCache.isEventEnabled():
            self.__showDialog(ctx)
            return None
        else:
            return super(EventBattleSquadEntity, self).getConfirmDialogMeta(ctx)

    def togglePlayerReadyAction(self, launchChain=False):
        self._togglePlayerReadyAction(launchChain)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createScheduler(self):
        return EventSquadScheduler(self)

    def _createRequestProcessor(self):
        return EventUnitRequestProcessor(self)

    def __showDialog(self, ctx):
        DialogsInterface.showDialog(rally_dialog_meta.createLeaveInfoMeta(ctx, 'eventDisabled'), lambda _: None)
