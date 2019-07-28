# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
import BigWorld
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.items import SelectResult, ValidationResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.utils import getPlayerDatabaseID
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache

class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT | FUNCTIONAL_FLAG.LOAD_PAGE, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()


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
        g_eventDispatcher.loadEventHangar()
        return super(EventBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isSwitch and not isLoadPage:
                self.storage.suspend()
                g_eventDispatcher.loadHangar()
        super(EventBattleSquadEntity, self).fini(ctx, woEvents)

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
            general = self.gameEventController.getSelectedGeneral()
            BigWorld.player().changeSelectedGeneral(general.getID(), general.getCurrentProgressLevel(), general.getFrontID())
        super(EventBattleSquadEntity, self).doBattleQueue(ctx, callback)

    def canPlayerDoAction(self):
        general = self.gameEventController.getSelectedGeneral()
        if general is not None:
            if general.getID() not in self.gameEventController.getGenerals():
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_GENERAL_INACTIVE)
            if general.isLocked():
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_GENERAL_IS_LOCKED)
            requireFront = self.getRequireFront()
            selectedFront = general.getFrontID()
            if requireFront is not None and requireFront is not selectedFront:
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_GENERAL_NOT_VALID)
            if self.gameEventController.getEnergy().getCurrentCount() <= 0:
                return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_NOT_ENOUGHT_ENERGY)
        return self._actionsValidator.canPlayerDoAction() or ValidationResult()

    def getRequireFront(self):
        selfDBID = getPlayerDatabaseID()
        if self.isCommander(dbID=selfDBID):
            return
        else:
            unitId, unit = self.getUnit()
            for slot in self.getSlotsIterator(unitId, unit):
                if not slot.player or slot.player.dbID == selfDBID:
                    continue
                ready = unit.getVehicles().get(slot.player.dbID) is not None
                if not ready:
                    continue
                pInfo = self.getPlayerInfo(dbID=slot.player.dbID)
                _, _, frontID = pInfo.eventData
                return frontID

            return

    def getConfirmDialogMeta(self, ctx):
        return None if not self.eventsCache.isEventEnabled() else super(EventBattleSquadEntity, self).getConfirmDialogMeta(ctx)

    def togglePlayerReadyAction(self, launchChain=False):
        self._togglePlayerReadyAction(launchChain)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)
