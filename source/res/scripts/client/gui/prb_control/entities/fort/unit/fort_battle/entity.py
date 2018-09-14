# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fort/unit/fort_battle/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control import prb_getters
from gui.prb_control.entities.fort.unit.fort_battle.actions_validator import FortBattleActionsValidator
from gui.prb_control.entities.fort.unit.fort_battle.scheduler import FortBattleScheduler
from gui.prb_control.entities.fort.unit.entity import FortBrowserEntity, FortEntity, FortBrowserEntryPoint, FortEntryPoint
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.fortifications import getClientFortMgr

class FortBattleBrowserEntryPoint(FortBrowserEntryPoint):
    """
    Fort battles list entry point
    """

    def __init__(self):
        super(FortBattleBrowserEntryPoint, self).__init__(PREBATTLE_TYPE.FORT_BATTLE)


class FortBattleEntryPoint(FortEntryPoint):
    """
    Fort battles entry point
    """

    def create(self, ctx, callback=None):
        self.__createOrJoin(ctx, callback)

    def join(self, ctx, callback=None):
        self.__createOrJoin(ctx, callback)

    def __createOrJoin(self, ctx, callback):
        """
        Request to create or join fort battle.
        Args:
            ctx: create or join request context
            callback: operation callback
        """
        if not prb_getters.hasModalEntity() or ctx.isForced():
            fortMgr = getClientFortMgr()
            if fortMgr:
                ctx.startProcessing(callback=callback)
                fortMgr.createOrJoinFortBattle(ctx.getID(), slotIdx=ctx.getSlotIdx())
            else:
                LOG_ERROR('Fort provider is not defined')
        else:
            LOG_ERROR('First, player has to confirm exit from the current prebattle/unit')
            if callback is not None:
                callback(False)
        return


class FortBattleBrowserEntity(FortBrowserEntity):
    """
    Fort battles list entity
    """

    def __init__(self):
        super(FortBattleBrowserEntity, self).__init__(PREBATTLE_TYPE.FORT_BATTLE)

    def fini(self, ctx=None, woEvents=False):
        if self.fortCtrl:
            self.fortCtrl.removeFortBattlesCache()
        return super(FortBattleBrowserEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def getBrowser(self):
        return self.fortCtrl.getFortBattlesCache() if self.fortCtrl else None

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.FORT:
            g_eventDispatcher.showFortWindow()
            return SelectResult(True)
        return super(FortBattleBrowserEntity, self).doSelectAction(action)


class FortBattleEntity(FortEntity):
    """
    Fort battle entity
    """

    def __init__(self):
        super(FortBattleEntity, self).__init__(PREBATTLE_TYPE.FORT_BATTLE)

    def getQueueType(self):
        return QUEUE_TYPE.FORT_BATTLE

    def doSelectAction(self, action):
        actionName = action.actionName
        if actionName == PREBATTLE_ACTION_NAME.FORT:
            g_eventDispatcher.showFortWindow()
            return SelectResult(True)
        return super(FortBattleEntity, self).doSelectAction(action)

    def _createActionsValidator(self):
        return FortBattleActionsValidator(self)

    def _createScheduler(self):
        return FortBattleScheduler(self)
