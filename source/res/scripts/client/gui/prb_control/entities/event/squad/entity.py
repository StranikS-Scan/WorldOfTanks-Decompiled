# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.entities.event.squad.requester import EventUnitRequestProcessor
from gui.prb_control.entities.event.squad.scheduler import EventSquadScheduler
from gui.prb_control.entities.event.squad.vehicles_watcher import EventBattlesSquadVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, UNIT_RESTRICTION, SELECTOR_BATTLE_TYPES
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.gui_items.Vehicle import VEHICLE_EVENT_TYPE
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsKnown
from helpers import dependency
from skeletons.gui.game_control import IGameEventController

class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.EVENT, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()

    def select(self, ctx, callback=None):
        super(EventBattleSquadEntryPoint, self).select(ctx, callback)
        setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT_BATTLE)


class EventBattleSquadEntity(SquadEntity):
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self):
        self.__watcher = None
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = EventBattlesSquadVehiclesWatcher()
        self.__watcher.start()
        return super(EventBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(EventBattleSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(EventBattleSquadEntity, self).leave(ctx=ctx, callback=callback)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__gameEventController.isEnabled() else super(EventBattleSquadEntity, self).getConfirmDialogMeta(ctx=ctx)

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.EVENT_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def canPlayerDoAction(self):
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            if not vehicle.isEvent:
                return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_VALID_FOR_EVENT)
            if vehicle.eventType in (VEHICLE_EVENT_TYPE.EVENT_BOSS, VEHICLE_EVENT_TYPE.EVENT_SPECIAL_BOSS):
                return ValidationResult(False, UNIT_RESTRICTION.WHITE_TIGER_IS_FORBIDDEN)
        return super(EventBattleSquadEntity, self).canPlayerDoAction()

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createScheduler(self):
        return EventSquadScheduler(self)

    def _createRequestProcessor(self):
        return EventUnitRequestProcessor(self)
