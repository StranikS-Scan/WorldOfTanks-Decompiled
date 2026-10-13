# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/prb_control/entities/pre_queue/entity.py
from __future__ import absolute_import
import BigWorld
import AccountCommands
from fort_rush.gui.fort_rush_gui_constants import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME, SELECTOR_BATTLE_TYPES
from fort_rush.gui.prb_control.entities.pre_queue.actions_validator import FortRushBattleActionsValidator
from fort_rush.gui.prb_control.entities.pre_queue.ctx import FortRushBattleQueueCtx
from gui.prb_control.entities.base.scheduler import BaseScheduler
from gui.shared.event_dispatcher import showHangar
from fort_rush_common.fort_rush_constants import QUEUE_TYPE
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.storages import storage_getter, RECENT_PRB_STORAGE
from gui.prb_control.entities.base.pre_queue.entity import PreQueueSubscriber, PreQueueEntryPoint, PreQueueEntity
from gui.prb_control.items import SelectResult
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from CurrentVehicle import g_currentVehicle
from helpers import dependency
from fort_rush.gui.prb_control.entities.pre_queue.vehicles_watcher import FortRushVehicleWatcher
from fort_rush.skeletons.battle_controller import IFortRushBattleController

class FortRushBattleEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(FortRushBattleEntryPoint, self).__init__(FUNCTIONAL_FLAG.FORT_RUSH, QUEUE_TYPE.FORT_RUSH)


@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def canSelectPrbEntity(ctrl=None):
    return ctrl.isAvailable()


class FortRushBattleEntity(PreQueueEntity):
    __battleController = dependency.descriptor(IFortRushBattleController)

    def __init__(self):
        super(FortRushBattleEntity, self).__init__(FUNCTIONAL_FLAG.FORT_RUSH, QUEUE_TYPE.FORT_RUSH, PreQueueSubscriber())
        self.__watcher = None
        return

    @storage_getter(RECENT_PRB_STORAGE)
    def storage(self):
        return None

    def init(self, ctx=None):
        self.storage.queueType = self.getQueueType()
        if not selectorUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.FORT_RUSH):
            selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.FORT_RUSH)
        self.__watcher = FortRushVehicleWatcher()
        self.__watcher.start()
        return super(FortRushBattleEntity, self).init(ctx=ctx)

    def fini(self, ctx=None, woEvents=False):
        if ctx:
            isExit = ctx.hasFlags(FUNCTIONAL_FLAG.EXIT)
            isSwitch = ctx.hasFlags(FUNCTIONAL_FLAG.SWITCH)
            isLoadPage = ctx.hasFlags(FUNCTIONAL_FLAG.LOAD_PAGE)
            if isExit or isSwitch and not isLoadPage:
                self.storage.queueType = QUEUE_TYPE.UNKNOWN
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        return super(FortRushBattleEntity, self).fini(ctx=ctx, woEvents=woEvents)

    def doSelectAction(self, action):
        return SelectResult(True) if action.actionName == PREBATTLE_ACTION_NAME.FORT_RUSH else super(FortRushBattleEntity, self).doSelectAction(action)

    def canInvite(self, prbType):
        return self.__battleController.isAvailable()

    @property
    def _accountComponent(self):
        player = BigWorld.player()
        if player:
            component = getattr(player, 'FortRushAccountComponent', None)
            return component
        else:
            return

    def _doQueue(self, ctx):
        vehID = ctx.getVehicleInventoryID()
        BigWorld.player().base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (self._queueType, vehID))

    def _doDequeue(self, ctx):
        BigWorld.player().base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, self._queueType)

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        if not self.__battleController.isAvailable():
            self.__battleController.selectRandomBattle()
        else:
            showHangar()

    def _goToHangar(self):
        showHangar()

    def _makeQueueCtxByAction(self, action=None):
        return FortRushBattleQueueCtx(g_currentVehicle.item.invID, waitingID='prebattle/join')

    def _createActionsValidator(self):
        return FortRushBattleActionsValidator(self)

    def _createScheduler(self):
        return BaseScheduler(self)
