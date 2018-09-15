# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR, LOG_DEBUG_DEV
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.event.squad.actions_handler import EventBattleSquadActionsHandler
from gui.prb_control.entities.event.squad.actions_validator import EventBattleSquadActionsValidator
from gui.prb_control.items import SelectResult
from skeletons.gui.game_control import IEventBattlesController
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG, REQUEST_TYPE
from helpers import dependency
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS

class EventBattleSquadEntryPoint(SquadEntryPoint):
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, accountsToInvite=None):
        super(EventBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.EVENT, accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createEventSquad(self.eventBattlesCtrl.getBattleType())


class EventBattleSquadEntity(SquadEntity):
    eventBattlesCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self):
        super(EventBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.EVENT, PREBATTLE_TYPE.EVENT)
        extras = self.getUnit(None)[1]._extras
        gameMode = extras.get('gameMode', None) if extras is not None else None
        self._battleSelection = gameMode if gameMode is not None else self.eventBattlesCtrl.getBattleType()
        LOG_DEBUG_DEV('[EventBattle] Creating event squad entity', self._prbType)
        return

    def getQueueType(self):
        return self._battleSelection

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.RANDOM, PREBATTLE_ACTION_NAME.EVENT_SQUAD):
            g_eventDispatcher.showUnitWindow(self._prbType)
            return SelectResult(True)
        if name == PREBATTLE_ACTION_NAME.EVENT_BATTLES and self._battleSelection != QUEUE_TYPE.EVENT_BATTLES:
            self._battleSelection = QUEUE_TYPE.EVENT_BATTLES
            return SelectResult(True)
        if name == PREBATTLE_ACTION_NAME.EVENT_BATTLES_2 and self._battleSelection != QUEUE_TYPE.EVENT_BATTLES_2:
            self._battleSelection = QUEUE_TYPE.EVENT_BATTLES_2
            return SelectResult(True)
        return super(EventBattleSquadEntity, self).doSelectAction(action)

    def unit_onUnitExtraChanged(self, extras):
        super(EventBattleSquadEntity, self).unit_onUnitExtraChanged(extras)
        gameMode = extras['gameMode']
        if gameMode is not None:
            self._battleSelection = gameMode
            LOG_DEBUG_DEV('EventBattle Unit Game Mode Has Changed To', gameMode)
        return

    def canChangeBattleType(self):
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            return False
        if not self.isCommander():
            return False
        return False if self._cooldown.isInProcess(REQUEST_TYPE.CHANGE_EVENT_QUEUE_TYPE) else True

    def changeEventQueueType(self, ctx, callback=None):
        battleType = ctx.getBattleType()
        if battleType not in QUEUE_TYPE.EVENT:
            LOG_ERROR('Incorrect value of battle type', battleType)
            if callback:
                callback(False)
            return
        if self._isInCoolDown(REQUEST_TYPE.CHANGE_EVENT_QUEUE_TYPE, coolDown=ctx.getCooldown()):
            return
        pPermissions = self.getPermissions()
        if not pPermissions.canChangeRosters():
            LOG_ERROR('Player can not change battle type', pPermissions)
            if callback:
                callback(False)
            return
        self._requestsProcessor.doRequest(ctx, 'changeEventType', newQueueType=battleType)
        self._cooldown.process(REQUEST_TYPE.CHANGE_EVENT_QUEUE_TYPE, coolDown=ctx.getCooldown())

    def _getRequestHandlers(self):
        handlers = super(EventBattleSquadEntity, self)._getRequestHandlers()
        handlers.update({REQUEST_TYPE.CHANGE_EVENT_QUEUE_TYPE: self.changeEventQueueType})
        return handlers

    def _createActionsHandler(self):
        return EventBattleSquadActionsHandler(self)

    def _createActionsValidator(self):
        return EventBattleSquadActionsValidator(self)

    def _vehicleStateCondition(self, vehicle):
        return False if VEHICLE_TAGS.EVENT not in vehicle.tags else super(EventBattleSquadEntity, self)._vehicleStateCondition(vehicle)
