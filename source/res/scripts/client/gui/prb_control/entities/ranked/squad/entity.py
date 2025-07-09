# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/ranked/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.ranked.pre_queue.scheduler import RankedScheduler
from gui.prb_control.entities.ranked.pre_queue.vehicles_watcher import RankedVehiclesWatcher
from gui.prb_control.entities.ranked.squad.action_handler import RankedSquadActionsHandler
from gui.prb_control.entities.ranked.squad.actions_validator import RankedSquadActionsValidator
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from skeletons.gui.shared import IItemsCache

class RankedSquadEntryPoint(SquadEntryPoint):
    __rankedCtrl = dependency.descriptor(IRankedBattlesController)

    def __init__(self, accountsToInvite=None):
        super(RankedSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANKED, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.RANKED, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createRankedSquad()


class RankedSquadEntity(SquadEntity):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RankedSquadEntity, self).__init__(FUNCTIONAL_FLAG.RANKED, PREBATTLE_TYPE.RANKED)
        self.__watcher = None
        self.__validIntCDs = set()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.RANKED)()
        return

    def init(self, ctx=None):
        self.storage.release()
        result = super(RankedSquadEntity, self).init(ctx)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.__watcher = RankedVehiclesWatcher()
        self.__watcher.start()
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        return super(RankedSquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(RankedSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.RANKED

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__rankedController.isEnabled() else super(RankedSquadEntity, self).getConfirmDialogMeta(ctx)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.RANKED_SQUAD, PREBATTLE_ACTION_NAME.RANKED)

    def _createActionsValidator(self):
        return RankedSquadActionsValidator(self)

    def _createScheduler(self):
        return RankedScheduler(self)

    def _createActionsHandler(self):
        return RankedSquadActionsHandler(self)

    def __onVehicleClientStateChanged(self, intCDs):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        allIntCDs = set((vehicle.intCD for vehicle in vehs))
        validIntCDs = allIntCDs - intCDs
        isReady = self.getPlayerInfo().isReady
        if isReady and self.__validIntCDs != validIntCDs:
            self.togglePlayerReadyAction(True)
        self.__validIntCDs = validIntCDs
