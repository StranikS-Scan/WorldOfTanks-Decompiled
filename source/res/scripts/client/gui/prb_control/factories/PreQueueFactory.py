# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
from gui.prb_control import prb_getters
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.shared.system_factory import registerQueueEntity, collectQueueEntity
from gui.shared.system_factory import registerEntryPoint, collectEntryPoint
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntryPoint, MapsTrainingEntity
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.entities.base.pre_queue.entity import PreQueueEntity
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.random.pre_queue.entity import RandomEntity, RandomEntryPoint
from gui.prb_control.entities.sandbox.pre_queue.entity import SandboxEntity, SandboxEntryPoint
from gui.prb_control.entities.bootcamp.pre_queue.entity import BootcampEntity, BootcampEntryPoint
from gui.prb_control.entities.tutorial.pre_queue.entity import TutorialEntity, TutorialEntryPoint
from gui.prb_control.entities.ranked.pre_queue.entity import RankedEntity, RankedEntryPoint
from gui.prb_control.entities.epic.pre_queue.entity import EpicEntity, EpicEntryPoint
from gui.prb_control.entities.mapbox.pre_queue.entity import MapboxEntity, MapboxEntryPoint
from gui.prb_control.entities.event.pre_queue.entity import EventBattleEntity, EventBattleEntryPoint
from gui.prb_control.entities.comp7.pre_queue.entity import Comp7Entity, Comp7EntryPoint
from gui.prb_control.items import FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG as _FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.storages import prequeue_storage_getter, storage_getter, RECENT_ARENA_STORAGE
__all__ = ('PreQueueFactory',)
registerQueueEntity(QUEUE_TYPE.RANDOMS, RandomEntity)
registerQueueEntity(QUEUE_TYPE.TUTORIAL, TutorialEntity)
registerQueueEntity(QUEUE_TYPE.SANDBOX, SandboxEntity)
registerQueueEntity(QUEUE_TYPE.RANKED, RankedEntity)
registerQueueEntity(QUEUE_TYPE.BOOTCAMP, BootcampEntity)
registerQueueEntity(QUEUE_TYPE.EPIC, EpicEntity)
registerQueueEntity(QUEUE_TYPE.MAPBOX, MapboxEntity)
registerQueueEntity(QUEUE_TYPE.MAPS_TRAINING, MapsTrainingEntity)
registerQueueEntity(QUEUE_TYPE.EVENT_BATTLES, EventBattleEntity)
registerQueueEntity(QUEUE_TYPE.COMP7, Comp7Entity)
registerEntryPoint(PREBATTLE_ACTION_NAME.RANDOM, RandomEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL, TutorialEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.SANDBOX, SandboxEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.RANKED, RankedEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.BOOTCAMP, BootcampEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.EPIC, EpicEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.MAPBOX, MapboxEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.MAPS_TRAINING, MapsTrainingEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.EVENT_BATTLE, EventBattleEntryPoint)
registerEntryPoint(PREBATTLE_ACTION_NAME.COMP7, Comp7EntryPoint)

class PreQueueFactory(ControlFactory):

    def __init__(self):
        self.pveStorage = prequeue_storage_getter(QUEUE_TYPE.SANDBOX)()
        self.rankedStorage = prequeue_storage_getter(QUEUE_TYPE.RANKED)()
        self.epicStorage = prequeue_storage_getter(QUEUE_TYPE.EPIC)()
        self.battleRoyaleStorage = prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)()
        self.mapboxStorage = prequeue_storage_getter(QUEUE_TYPE.MAPBOX)()
        self.mapsTrainingStorage = prequeue_storage_getter(QUEUE_TYPE.MAPS_TRAINING)()
        self.eventBattlesStorage = prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)()
        self.funRandomStorage = prequeue_storage_getter(QUEUE_TYPE.FUN_RANDOM)()
        self.comp7Storage = prequeue_storage_getter(QUEUE_TYPE.COMP7)()
        self.recentArenaStorage = storage_getter(RECENT_ARENA_STORAGE)()

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
        prbEntity = self.__createByQueueType(queueType)
        return prbEntity if prbEntity else self.__createDefaultEntity()

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, entity.getEntityType(), True, entity.isInQueue(), funcFlags=entity.getFunctionalFlags())

    def createLeaveCtx(self, flags=_FLAG.UNDEFINED, entityType=0):
        return LeavePreQueueCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByQueueType(self, queueType):
        return collectQueueEntity(queueType)

    def __createDefaultEntity(self):
        if prb_getters.isInBootcampAccount():
            return BootcampEntity()
        elif self.pveStorage.isModeSelected():
            return SandboxEntity()
        elif self.rankedStorage.isModeSelected():
            return RankedEntity()
        elif self.epicStorage.isModeSelected():
            return EpicEntity()
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
            prbEntity = self.__createByQueueType(self.recentArenaStorage.queueType)
            return prbEntity if prbEntity else RandomEntity()
