# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/comp7/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.items.unit_items import DynamicRosterSettings
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.prb_control.entities.comp7.comp7_prb_helpers import Comp7IntroPresenter
from gui.prb_control.entities.comp7.pre_queue.vehicles_watcher import Comp7VehiclesWatcher
from gui.prb_control.entities.base.ctx import Comp7PrbAction
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.comp7.scheduler import Comp7Scheduler
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.comp7.squad.actions_validator import Comp7SquadActionsValidator
from gui.prb_control.entities.comp7.squad.action_handler import Comp7SquadActionsHandler
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from skeletons.gui.shared import IItemsCache

class Comp7SquadEntryPoint(SquadEntryPoint):
    __comp7Ctrl = dependency.descriptor(IComp7Controller)

    def __init__(self, accountsToInvite=None):
        super(Comp7SquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.COMP7, accountsToInvite)
        self.__squadSize = self.__comp7Ctrl.getModeSettings().numPlayers

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.COMP7, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def configure(self, action):
        super(Comp7SquadEntryPoint, self).configure(action)
        if isinstance(action, Comp7PrbAction):
            self.__squadSize = action.getSquadSize()

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createComp7Squad(self.__squadSize)


class Comp7SquadEntity(SquadEntity):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(Comp7SquadEntity, self).__init__(FUNCTIONAL_FLAG.COMP7, PREBATTLE_TYPE.COMP7)
        self.__watcher = None
        self.__introPresenter = Comp7IntroPresenter()
        self.__validIntCDs = set()
        self.storage = prequeue_storage_getter(QUEUE_TYPE.COMP7)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__introPresenter.init()
        result = super(Comp7SquadEntity, self).init(ctx)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.__watcher = Comp7VehiclesWatcher()
        self.__watcher.start()
        return result

    def fini(self, ctx=None, woEvents=False):
        self.__introPresenter.fini()
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        return super(Comp7SquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(Comp7SquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.COMP7

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__comp7Controller.isEnabled() else super(Comp7SquadEntity, self).getConfirmDialogMeta(ctx)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.COMP7_SQUAD, PREBATTLE_ACTION_NAME.COMP7)

    def _createActionsValidator(self):
        return Comp7SquadActionsValidator(self)

    def _createScheduler(self):
        return Comp7Scheduler(self)

    def _createActionsHandler(self):
        return Comp7SquadActionsHandler(self)

    def _createRosterSettings(self):
        _, unit = self.getUnit(safe=True)
        return Comp7RosterSettings(unit)

    def _buildStats(self, unitMgrID, unit):
        self._rosterSettings.updateSettings(unit)
        return super(Comp7SquadEntity, self)._buildStats(unitMgrID, unit)

    def __onVehicleClientStateChanged(self, intCDs):
        vehs = self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).itervalues()
        allIntCDs = set((vehicle.intCD for vehicle in vehs))
        validIntCDs = allIntCDs - intCDs
        isReady = self.getPlayerInfo().isReady
        if isReady and self.__validIntCDs != validIntCDs:
            self.togglePlayerReadyAction(True)
        self.__validIntCDs = validIntCDs


class Comp7RosterSettings(DynamicRosterSettings):

    def updateSettings(self, unit):
        self._maxSlots = unit.getSquadSize()

    def _extractSettings(self, unit):
        settings = super(Comp7RosterSettings, self)._extractSettings(unit)
        settings['maxSlots'] = unit.getSquadSize()
        return settings
