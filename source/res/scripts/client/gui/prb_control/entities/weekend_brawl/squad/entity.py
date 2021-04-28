# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/weekend_brawl/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.weekend_brawl.pre_queue.vehicles_watcher import WeekendBrawlVehiclesWatcher
from gui.prb_control.entities.weekend_brawl.scheduler import WeekendBrawlScheduler
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint
from gui.prb_control.entities.random.squad.entity import RandomSquadEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, UNIT_RESTRICTION
from gui.prb_control.entities.weekend_brawl.squad.actions_validator import WeekendBrawlSquadActionsValidator
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.game_control import IWeekendBrawlController

class WeekendBrawlSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(WeekendBrawlSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.WEEKEND_BRAWL, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.WEEKEND_BRAWL, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createWeekendBrawlSquad()


class WeekendBrawlSquadEntity(RandomSquadEntity):
    __wBrawlController = dependency.descriptor(IWeekendBrawlController)
    _VALID_RESTRICTIONS = (UNIT_RESTRICTION.NOT_READY_IN_SLOTS,)

    def __init__(self):
        super(WeekendBrawlSquadEntity, self).__init__(FUNCTIONAL_FLAG.WEEKEND_BRAWL, PREBATTLE_TYPE.WEEKEND_BRAWL)

    def init(self, ctx=None):
        self.storage.release()
        result = super(WeekendBrawlSquadEntity, self).init(ctx)
        return result

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH) or not self.__wBrawlController.isModeActive():
            self.storage.suspend()
        super(WeekendBrawlSquadEntity, self).leave(ctx, callback)

    @prequeue_storage_getter(QUEUE_TYPE.WEEKEND_BRAWL)
    def storage(self):
        return None

    def getQueueType(self):
        return QUEUE_TYPE.WEEKEND_BRAWL

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__wBrawlController.isModeActive() else super(WeekendBrawlSquadEntity, self).getConfirmDialogMeta(ctx)

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.WEEKEND_BRAWL_SQUAD, PREBATTLE_ACTION_NAME.WEEKEND_BRAWL):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return SelectResult()

    def isVehiclesReadyToBattle(self):
        result = self._actionsValidator.getVehiclesValidator().canPlayerDoAction()
        return result is None or result.isValid or result.restriction in self._VALID_RESTRICTIONS

    def _createVehiclesWatcher(self):
        return WeekendBrawlVehiclesWatcher()

    def _createActionsValidator(self):
        return WeekendBrawlSquadActionsValidator(self)

    def _createScheduler(self):
        return WeekendBrawlScheduler(self)
