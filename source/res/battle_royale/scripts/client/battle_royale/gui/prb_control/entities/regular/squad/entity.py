# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/prb_control/entities/regular/squad/entity.py
from CurrentVehicle import g_currentVehicle
from battle_royale.gui.constants import BattleRoyaleSubMode
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from battle_royale.gui.prb_control.entities.regular.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from battle_royale.gui.prb_control.entities.regular.scheduler import RoyaleScheduler
from battle_royale.gui.prb_control.entities.regular.squad.actions_validator import BattleRoyaleSquadActionsValidator
from battle_royale.gui.prb_control.entities.regular.squad.action_handler import BattleRoyaleSquadActionsHandler
from gui.Scaleform.daapi.view.lobby.header.fight_btn_tooltips import getRoyaleFightBtnTooltipData
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import BattleRoyalePlatoonEvent
from helpers import dependency
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(BattleRoyaleSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.BATTLE_ROYALE, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createBattleRoyaleSquad()


class BattleRoyaleSquadEntity(SquadEntity):
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _VALID_RESTRICTIONS = (UNIT_RESTRICTION.UNIT_NOT_FULL, UNIT_RESTRICTION.NOT_READY_IN_SLOTS)

    def __init__(self):
        super(BattleRoyaleSquadEntity, self).__init__(FUNCTIONAL_FLAG.BATTLE_ROYALE, PREBATTLE_TYPE.BATTLE_ROYALE)
        self.__watcher = None
        self.storage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        self.__battleRoyaleController.setCurrentSubModeID(BattleRoyaleSubMode.SQUAD_MODE_ID)
        result = super(BattleRoyaleSquadEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        g_eventDispatcher.loadHangar()
        return super(BattleRoyaleSquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        updateNeeded = True
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
            updateNeeded = False
        self.__battleRoyaleController.setCurrentSubModeID(BattleRoyaleSubMode.SOLO_MODE_ID, updateNeeded)
        g_eventBus.handleEvent(BattleRoyalePlatoonEvent(BattleRoyalePlatoonEvent.LEAVED_PLATOON), scope=EVENT_BUS_SCOPE.LOBBY)
        super(BattleRoyaleSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.BATTLE_ROYALE

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__battleRoyaleController.isEnabled() else super(BattleRoyaleSquadEntity, self).getConfirmDialogMeta(ctx)

    def getFightBtnTooltipData(self, isStateDisabled):
        if isStateDisabled:
            return (getRoyaleFightBtnTooltipData(self.canPlayerDoAction()), False)
        return (TOOLTIPS_CONSTANTS.BATTLE_ROYALE_PERF_ADVANCED, True) if g_currentVehicle.isOnlyForBattleRoyaleBattles() else super(BattleRoyaleSquadEntity, self).getFightBtnTooltipData(isStateDisabled)

    def isVehiclesReadyToBattle(self):
        result = self._actionsValidator.getVehiclesValidator().canPlayerDoAction()
        return result is None or result.isValid or result.restriction in self._VALID_RESTRICTIONS

    @property
    def _showUnitActionNames(self):
        return (PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD,)

    def _createActionsValidator(self):
        return BattleRoyaleSquadActionsValidator(self)

    def _createScheduler(self):
        return RoyaleScheduler(self)

    def _createActionsHandler(self):
        return BattleRoyaleSquadActionsHandler(self)
