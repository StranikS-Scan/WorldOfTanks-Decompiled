# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.event.squad.scheduler import EventBattleSquadScheduler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG

class EventBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad()


class EventBattleSquadEntity(SquadEntity):

    def __init__(self):
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)

    def getQueueType(self):
        return QUEUE_TYPE.EVENT_BATTLES

    def doSelectAction(self, action):
        name = action.actionName
        if name == PREBATTLE_ACTION_NAME.EVENT_SQUAD:
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        if name == PREBATTLE_ACTION_NAME.RANDOM:
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createScheduler(self):
        return EventBattleSquadScheduler(self)
