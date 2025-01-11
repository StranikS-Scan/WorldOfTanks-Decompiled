# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/bob/squad/entity.py
from constants import PREBATTLE_TYPE, QUEUE_TYPE
from gui.prb_control.entities.bob.pre_queue.vehicles_watcher import BobVehiclesWatcher
from gui.prb_control.entities.bob.scheduler import BobScheduler
from gui.prb_control.entities.base.squad.ctx import SquadSettingsCtx
from gui.prb_control.entities.base.squad.entity import SquadEntryPoint, SquadEntity
from gui.prb_control.entities.bob.squad.action_handler import BobSquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, UNIT_RESTRICTION
from gui.prb_control.entities.bob.squad.actions_validator import BobSquadActionsValidator
from gui.prb_control.storages import prequeue_storage_getter
from gui.prb_control.entities.base.squad.components import RestrictedSPGDataProvider, RestrictedScoutDataProvider
from helpers import dependency
from skeletons.gui.game_control import IBobController

class BobSquadEntryPoint(SquadEntryPoint):

    def __init__(self, accountsToInvite=None):
        super(BobSquadEntryPoint, self).__init__(FUNCTIONAL_FLAG.BOB, accountsToInvite)

    def makeDefCtx(self):
        return SquadSettingsCtx(PREBATTLE_TYPE.BOB, waitingID='prebattle/create', accountsToInvite=self._accountsToInvite)

    def _doCreate(self, unitMgr, ctx):
        unitMgr.createBobSquad()


class BobSquadEntity(SquadEntity):
    bobController = dependency.descriptor(IBobController)
    _VALID_RESTRICTIONS = (UNIT_RESTRICTION.NOT_READY_IN_SLOTS,)

    def __init__(self):
        super(BobSquadEntity, self).__init__(FUNCTIONAL_FLAG.BOB, PREBATTLE_TYPE.BOB)
        self.__restrictedSPGDataProvider = RestrictedSPGDataProvider()
        self.__restrictedScoutDataProvider = RestrictedScoutDataProvider()

    def init(self, ctx=None):
        self.__restrictedSPGDataProvider.init(self)
        self.__restrictedScoutDataProvider.init(self)
        self.storage.release()
        result = super(BobSquadEntity, self).init(ctx)
        return result

    def fini(self, ctx=None, woEvents=False):
        self.__restrictedSPGDataProvider.fini()
        self.__restrictedScoutDataProvider.fini()
        return super(BobSquadEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def leave(self, ctx, callback=None):
        if ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH) or not self.bobController.isModeActive():
            self.storage.suspend()
        super(BobSquadEntity, self).leave(ctx, callback)

    @prequeue_storage_getter(QUEUE_TYPE.BOB)
    def storage(self):
        return None

    def getQueueType(self):
        return QUEUE_TYPE.BOB

    def getConfirmDialogMeta(self, ctx):
        return None if not self.bobController.isModeActive() else super(BobSquadEntity, self).getConfirmDialogMeta(ctx)

    def doSelectAction(self, action):
        name = action.actionName
        if name in (PREBATTLE_ACTION_NAME.BOB_SQUAD, PREBATTLE_ACTION_NAME.BOB):
            g_eventDispatcher.showUnitWindow(self._prbType)
            if action.accountsToInvite:
                self._actionsHandler.processInvites(action.accountsToInvite)
            return SelectResult(True)
        return SelectResult()

    def isVehiclesReadyToBattle(self):
        result = self._actionsValidator.getVehiclesValidator().canPlayerDoAction()
        return result is None or result.isValid or result.restriction in self._VALID_RESTRICTIONS

    def getMaxSPGCount(self):
        return self.__restrictedSPGDataProvider.getMaxPossibleVehicles()

    def getMaxScoutCount(self):
        return self.__restrictedScoutDataProvider.getMaxPossibleVehicles()

    def hasSlotForSPG(self):
        return self.__restrictedSPGDataProvider.hasSlotForVehicle()

    def hasSlotForScout(self):
        return self.__restrictedScoutDataProvider.hasSlotForVehicle()

    def getCurrentSPGCount(self):
        return self.__restrictedSPGDataProvider.getCurrentVehiclesCount()

    def getCurrentScoutCount(self):
        return self.__restrictedScoutDataProvider.getCurrentVehiclesCount()

    def getMaxScoutLevels(self):
        return self.__restrictedScoutDataProvider.getRestrictionLevels()

    def _createVehiclesWatcher(self):
        return BobVehiclesWatcher()

    def _createActionsValidator(self):
        return BobSquadActionsValidator(self)

    def _createScheduler(self):
        return BobScheduler(self)

    def _createActionsHandler(self):
        return BobSquadActionsHandler(self)
