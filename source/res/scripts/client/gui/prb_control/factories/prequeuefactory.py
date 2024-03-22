# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
from gui.prb_control import prb_getters
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.shared.system_factory import registerQueueEntity, collectQueueEntity
from gui.shared.system_factory import registerEntryPoint, collectEntryPoint
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntryPoint, MapsTrainingEntity
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.entities.winback.pre_queue.entity import WinbackEntryPoint, WinbackEntity
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.random.pre_queue.entity import RandomEntity, RandomEntryPoint
from gui.prb_control.entities.ranked.pre_queue.entity import RankedEntity, RankedEntryPoint
from gui.prb_control.entities.mapbox.pre_queue.entity import MapboxEntity, MapboxEntryPoint
from gui.prb_control.entities.event.pre_queue.entity import EventBattleEntity, EventBattleEntryPoint
from gui.prb_control.entities.comp7.pre_queue.entity import Comp7Entity, Comp7EntryPoint
from gui.prb_control.items import FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG as _FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.storages import prequeue_storage_getter, storage_getter, RECENT_PRB_STORAGE
__all__ = ('PreQueueFactory',)
registerQueueEntity(QUEUE_TYPE.RANDOMS, RandomEntity)
registerQueueEntity(QUEUE_TYPE.RANKED, RankedEntity)
registerQueueEntity(QUEUE_TYPE.MAPBOX, MapboxEntity)
registerQueueEntity(QUEUE_TYPE.MAPS_TRAINING, MapsTrainingEntity)
registerQueueEntity(QUEUE_TYPE.EVENT_BATTLES, EventBattleEntity)
registerQueueEntity(QUEUE_TYPE.COMP7, Comp7Entity)
registerQueueEntity(QUEUE_TYPE.WINBACK, WinbackEntity)
registerEntryPoint(PREBATTLE_ACTION_NAME.RANDOM, RandomEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.RANKED, RankedEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.MAPBOX, MapboxEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.MAPS_TRAINING, MapsTrainingEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.EVENT_BATTLE, EventBattleEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.COMP7, Comp7EntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.WINBACK, WinbackEntryPoint)

class PreQueueFactory(ControlFactory):

    def __init__(self):
        self.rankedStorage = prequeue_storage_getter(QUEUE_TYPE.RANKED)()
        self.frontlineStorage = prequeue_storage_getter(QUEUE_TYPE.EPIC)()
        self.battleRoyaleStorage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
        self.mapboxStorage = prequeue_storage_getter(QUEUE_TYPE.MAPBOX)()
        self.mapsTrainingStorage = prequeue_storage_getter(QUEUE_TYPE.MAPS_TRAINING)()
        self.eventBattlesStorage = prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)()
        self.funRandomStorage = prequeue_storage_getter(QUEUE_TYPE.FUN_RANDOM)()
        self.comp7Storage = prequeue_storage_getter(QUEUE_TYPE.COMP7)()
        self.recentPrbStorage = storage_getter(RECENT_PRB_STORAGE)()
        self.winbackStorage = prequeue_storage_getter(QUEUE_TYPE.WINBACK)()

    def createEntry(self, ctx):
        LOG_ERROR('preQueue functional has not any entries')
        return None

    def createEntryByAction(self, action):
        result = collectEntryPoint(action.actionName)
        if result:
            result.setAccountsToInvite(action.accountsToInvite)
            result.setExtData(action.extData)
        return result

    def createEntity(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.PREQUEUE:
            queueType = ctx.getEntityType()
        else:
            queueType = prb_getters.getQueueType()
        if queueType == QUEUE_TYPE.RANDOMS and self.winbackStorage.isModeAvailable():
            queueType = QUEUE_TYPE.WINBACK
        prbEntity = self.__createByQueueType(queueType)
        return prbEntity if prbEntity else self.__createDefaultEntity()

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, entity.getEntityType(), True, entity.isInQueue(), funcFlags=entity.getFunctionalFlags())

    def createLeaveCtx(self, flags=_FLAG.UNDEFINED, entityType=0):
        return LeavePreQueueCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByQueueType(self, queueType):
        return collectQueueEntity(queueType)

    def __createDefaultEntity(self):
        if self.rankedStorage.isModeSelected():
            return RankedEntity()
        elif self.frontlineStorage.isModeSelected():
            return self.__createByQueueType(QUEUE_TYPE.EPIC)
        elif self.battleRoyaleStorage.isModeSelected():
            return self.__createByQueueType(QUEUE_TYPE.BATTLE_ROYALE)
        elif self.mapboxStorage.isModeSelected():
            return MapboxEntity()
        elif self.mapsTrainingStorage.isModeSelected():
            return MapsTrainingEntity()
        elif self.eventBattlesStorage.isModeSelected():
            return EventBattleEntity()
        elif self.funRandomStorage is not None and self.funRandomStorage.isModeSelected():
            return self.__createByQueueType(QUEUE_TYPE.FUN_RANDOM)
        elif self.comp7Storage.isModeSelected():
            return Comp7Entity()
        else:
            lastBattleQueueType = self.recentPrbStorage.queueType
            if lastBattleQueueType == QUEUE_TYPE.WINBACK and not self.winbackStorage.isModeAvailable():
                lastBattleQueueType = QUEUE_TYPE.RANDOMS
            if lastBattleQueueType and self.recentPrbStorage.isModeSelected():
                prbEntity = self.__createByQueueType(lastBattleQueueType)
                if prbEntity:
                    return prbEntity
            return WinbackEntity() if self.winbackStorage.isModeAvailable() else RandomEntity()
