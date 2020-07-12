# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/battle_royale/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.battle_royale.pre_queue.vehicles_watcher import BattleRoyaleVehiclesWatcher
from gui.prb_control.entities.battle_royale.scheduler import RoyaleScheduler
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, UNIT_RESTRICTION
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.battle_royale.squad.actions_validator import BattleRoyaleSquadActionsValidator
from gui.prb_control.entities.battle_royale.squad.action_handler import BattleRoyaleSquadActionsHandler
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
        return

    def init(self, ctx=None):
        self.storage.release()
        self.__watcher = BattleRoyaleVehiclesWatcher()
        self.__watcher.start()
        result = super(BattleRoyaleSquadEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(BattleRoyaleSquadEntity, self).fini(ctx, woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH):
            self.storage.suspend()
        super(BattleRoyaleSquadEntity, self).leave(ctx, callback)

    def getQueueType(self):
        return QUEUE_TYPE.BATTLE_ROYALE

    def getConfirmDialogMeta(self, ctx):
        return None if not self.__battleRoyaleController.isEnabled() else super(BattleRoyaleSquadEntity, self).getConfirmDialogMeta(ctx)

    @prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)
    def storage(self):
        return None

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.BATTLE_ROYALE_SQUAD, PREBATTLE_ACTION_NAME.BATTLE_ROYALE):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return super(BattleRoyaleSquadEntity, self).doSelectAction(action)

    def isVehiclesReadyToBattle(self):
        result = self._actionsValidator.getVehiclesValidator().canPlayerDoAction()
        return result is None or result.isValid or result.restriction in self._VALID_RESTRICTIONS

    def _createActionsValidator(self):
        return BattleRoyaleSquadActionsValidator(self)

    def _createScheduler(self):
        return RoyaleScheduler(self)

    def _createActionsHandler(self):
        return BattleRoyaleSquadActionsHandler(self)
