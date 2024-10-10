# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/prb_control/entities/squad/entity.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import EVENT_SAVED_VEHICLE
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.utils.SelectorBattleTypesUtils import setBattleTypeAsKnown
from white_tiger.gui.gui_constants import SELECTOR_BATTLE_TYPES, PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from white_tiger.gui.prb_control.entities import isHangarShallBeLoaded
from white_tiger.gui.prb_control.entities.squad.actions_handler import WhiteTigerBattleSquadActionsHandler
from white_tiger.gui.prb_control.entities.squad.actions_validator import WhiteTigerBattleSquadActionsValidator
from white_tiger.gui.prb_control.entities.squad.requester import WhiteTigerUnitRequestProcessor
from white_tiger.gui.prb_control.entities.squad.scheduler import WhiteTigerSquadScheduler
from white_tiger.gui.prb_control.entities.squad.vehicles_watcher import WhiteTigerBattlesSquadVehiclesWatcher
from white_tiger_common.wt_constants import PREBATTLE_TYPE, QUEUE_TYPE
from helpers import dependency
from skeletons.gui.game_control import IWhiteTigerController
from skeletons.prebattle_vehicle import IPrebattleVehicle

class WhiteTigerBattleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(WhiteTigerBattleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.WHITE_TIGER, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createWhiteTigerSquad()

    def select(self, ctx, callback=None):
        super(WhiteTigerBattleSquadEntryPoint, self).select(ctx, callback)
        setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.WHITE_TIGER)


class WhiteTigerBattleSquadEntity(SquadEntity):
    __gameEventController = dependency.descriptor(IWhiteTigerController)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)

    def __init__(self):
        super(WhiteTigerBattleSquadEntity, self).__init__(FUNCTIONAL_FLAG.WHITE_TIGER, PREBATTLE_TYPE.WHITE_TIGER)
        self.storage = prequeue_storage_getter(QUEUE_TYPE.WHITE_TIGER)()
        self.__watcher = None
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = WhiteTigerBattlesSquadVehiclesWatcher()
        self.__watcher.start()
        g_eventDispatcher.loadHangar()
        return super(WhiteTigerBattleSquadEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and isHangarShallBeLoaded(ctx):
            g_eventDispatcher.loadHangar()
        return super(WhiteTigerBattleSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        AccountSettings.setFavorites(EVENT_SAVED_VEHICLE, self.__prebattleVehicle.invID)
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(WhiteTigerBattleSquadEntity, self).leave(ctx=ctx, callback=callback)

    def getQueueType(self):
        return QUEUE_TYPE.WHITE_TIGER

    def getConfirmDialogMeta(self, ctx):
        ctrl = self.__gameEventController
        return None if not ctrl.isModeActive() or not ctrl.isHangarAvailable() or ctrl.isFrozen() else super(WhiteTigerBattleSquadEntity, self).getConfirmDialogMeta(ctx=ctx)

    def _createActionsHandler(self):
        return WhiteTigerBattleSquadActionsHandler(self)

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.WHITE_TIGER_SQUAD, PREBATTLE_ACTION_NAME.WHITE_TIGER)

    def _createActionsValidator(self):
        return WhiteTigerBattleSquadActionsValidator(self)

    def _createScheduler(self):
        return WhiteTigerSquadScheduler(self)

    def _createRequestProcessor(self):
        return WhiteTigerUnitRequestProcessor(self)

    def _getSelectedVehCD(self):
        vehicle = self.__prebattleVehicle.item
        return vehicle.intCD if vehicle is not None else None

    def _selectVehicle(self, vehID):
        pass
