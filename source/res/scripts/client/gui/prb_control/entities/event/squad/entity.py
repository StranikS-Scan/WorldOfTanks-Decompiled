# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_SAVED_VEHICLE
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event import isHangarShallBeLoaded
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.entities.event.squad.requester import EventUnitRequestProcessor
from gui.prb_control.entities.event.squad.scheduler import EventSquadScheduler
from gui.prb_control.entities.event.squad.vehicles_watcher import EventBattlesSquadVehiclesWatcher
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, SELECTOR_BATTLE_TYPES
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsKnown
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.prebattle_vehicle import IPrebattleVehicle

class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.EVENT, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()

    def select(self, ctx, callback=None):
        super(EventBattleSquadEntryPoint, self).select(ctx, callback)
        setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.EVENT)


class EventBattleSquadEntity(SquadEntity):
    __gameEventController = dependency.descriptor(IGameEventController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        self.__watcher = None
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = EventBattlesSquadVehiclesWatcher()
        self.__watcher.start()
        g_eventDispatcher.loadHangar()
        return super(EventBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and isHangarShallBeLoaded(ctx):
            g_eventDispatcher.loadHangar()
        return super(EventBattleSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        AccountSettings.setFavorites(EVENT_SAVED_VEHICLE, self.__prebattleVehicle.invID)
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(EventBattleSquadEntity, self).leave(ctx=ctx, callback=callback)

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def getConfirmDialogMeta(self, ctx):
        ctrl = self.__gameEventController
        return None if not ctrl.isModeActive() or not ctrl.isHangarAvailable() else super(EventBattleSquadEntity, self).getConfirmDialogMeta(ctx=ctx)

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.EVENT_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createScheduler(self):
        return EventSquadScheduler(self)

    def _createRequestProcessor(self):
        return EventUnitRequestProcessor(self)

    def _getSelectedVehCD(self):
        vehicle = self.__prebattleVehicle.item
        return vehicle.intCD if vehicle is not None else None

    def _selectVehicle(self, vehID):
        pass
