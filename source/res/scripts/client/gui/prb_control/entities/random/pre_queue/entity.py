# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/random/pre_queue/entity.py
import BigWorld
import ArenaType
from CurrentVehicle import g_currentVehicle
from account_helpers import gameplay_ctx
from constants import QUEUE_TYPE
from debug_utils import LOG_DEBUG
from gui.prb_control.entities.stronghold.unit.entity import StrongholdBrowserEntity
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntryPoint, PreQueueEntity, PreQueueSubscriber
from gui.prb_control.entities.base.pre_queue.vehicles_watcher import RandomRestrictedVehiclesWatcher
from gui.prb_control.entities.random.pre_queue.ctx import RandomQueueCtx
from gui.prb_control.items import SelectResult
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, FUNCTIONAL_FLAG
from soft_exception import SoftException

class RandomEntryPoint(PreQueueEntryPoint):

    def __init__(self):
        super(RandomEntryPoint, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS)


class RandomEntity(PreQueueEntity):

    def __init__(self):
        super(RandomEntity, self).__init__(FUNCTIONAL_FLAG.RANDOM, QUEUE_TYPE.RANDOMS, PreQueueSubscriber())
        self.__watcher = None
        return

    def init(self, ctx=None):
        self.__watcher = RandomRestrictedVehiclesWatcher()
        self.__watcher.start()
        return super(RandomEntity, self).init(ctx)

    def fini(self, ctx=None, woEvents=False):
        if self.__watcher is not None:
            self.__watcher.stop()
            self.__watcher = None
        if not woEvents and g_eventDispatcher.needToLoadHangar(ctx, self.getModeFlags(), []):
            g_eventDispatcher.loadHangar()
        return super(RandomEntity, self).fini(ctx, woEvents)

    @vehicleAmmoCheck
    def queue(self, ctx, callback=None):
        super(RandomEntity, self).queue(ctx, callback=callback)

    def doSelectAction(self, action):
        name = action.actionName
        return SelectResult(True) if name == PREBATTLE_ACTION_NAME.RANDOM else super(RandomEntity, self).doSelectAction(action)

    def _doQueue(self, ctx):
        mmData = ctx.getDemoArenaTypeID()
        if mmData:
            team = mmData >> 28 & 15
            levelType = mmData >> 24 & 15
            arenaTypeID = mmData & 16777215
            LOG_DEBUG('Demonstrator gameplay selected: ', ArenaType.g_cache[arenaTypeID].gameplayName)
            LOG_DEBUG('Demonstrator map selected: ', ArenaType.g_cache[arenaTypeID].geometryName)
            LOG_DEBUG('Demonstrator level selected: ', levelType)
            LOG_DEBUG('Demonstrator spawn selected: ', team)
        BigWorld.player().enqueueRandom(ctx.getVehicleInventoryID(), gameplaysMask=ctx.getGamePlayMask(), randomFlags=ctx.getRandomFlags(), arenaTypeID=mmData)
        LOG_DEBUG('Sends request on queuing to the random battle', ctx)

    def _doDequeue(self, ctx):
        BigWorld.player().dequeueRandom()
        LOG_DEBUG('Sends request on dequeuing from the random battle')

    def _makeQueueCtxByAction(self, action=None):
        invID = g_currentVehicle.invID
        if not invID:
            raise SoftException('Inventory ID of vehicle can not be zero')
        if action is not None:
            arenaTypeID = action.mmData
        else:
            arenaTypeID = 0
        return RandomQueueCtx(invID, arenaTypeID=arenaTypeID, gamePlayMask=gameplay_ctx.getMask(), randomFlags=gameplay_ctx.getRandomFlags(), waitingID='prebattle/join')

    def _goToHangar(self):
        if isinstance(self._previous, StrongholdBrowserEntity):
            return
        super(RandomEntity, self)._goToHangar()

    def _goToQueueUI(self):
        g_eventDispatcher.loadBattleQueue()
        return FUNCTIONAL_FLAG.LOAD_PAGE

    def _exitFromQueueUI(self):
        g_eventDispatcher.loadHangar()
