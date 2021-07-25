# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/factories/PreQueueFactory.py
import inspect
import gui.prb_control.prb_getters
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.prb_control.entities.battle_royale.pre_queue import entity as br_entity
from gui.prb_control.entities.battle_royale_tournament.pre_queue import entity as br_tournament
from gui.prb_control.entities.maps_training.pre_queue.entity import MapsTrainingEntryPoint, MapsTrainingEntity
from gui.prb_control.factories.ControlFactory import ControlFactory
from gui.prb_control.entities.base.pre_queue.ctx import LeavePreQueueCtx
from gui.prb_control.entities.random.pre_queue.entity import RandomEntity, RandomEntryPoint
from gui.prb_control.entities.sandbox.pre_queue.entity import SandboxEntity, SandboxEntryPoint
from gui.prb_control.entities.bootcamp.pre_queue.entity import BootcampEntity, BootcampEntryPoint
from gui.prb_control.entities.tutorial.pre_queue.entity import TutorialEntity, TutorialEntryPoint
from gui.prb_control.entities.ranked.pre_queue.entity import RankedEntity, RankedEntryPoint
from gui.prb_control.entities.epic.pre_queue.entity import EpicEntity, EpicEntryPoint, EpicForcedEntryPoint
from gui.prb_control.entities.mapbox.pre_queue.entity import MapboxEntity, MapboxEntryPoint
from gui.prb_control.items import FunctionalState
from gui.prb_control.settings import FUNCTIONAL_FLAG as _FLAG
from gui.prb_control.settings import PREBATTLE_ACTION_NAME, CTRL_ENTITY_TYPE
from gui.prb_control.storages import prequeue_storage_getter
__all__ = ('PreQueueFactory',)
_SUPPORTED_QUEUES = {QUEUE_TYPE.RANDOMS: RandomEntity,
 QUEUE_TYPE.TUTORIAL: TutorialEntity,
 QUEUE_TYPE.SANDBOX: SandboxEntity,
 QUEUE_TYPE.RANKED: RankedEntity,
 QUEUE_TYPE.BOOTCAMP: BootcampEntity,
 QUEUE_TYPE.EPIC: EpicEntity,
 QUEUE_TYPE.BATTLE_ROYALE: br_entity.BattleRoyaleEntity,
 QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT: br_tournament.BattleRoyaleTournamentEntity,
 QUEUE_TYPE.MAPBOX: MapboxEntity,
 QUEUE_TYPE.MAPS_TRAINING: MapsTrainingEntity}
_SUPPORTED_ENTRY_BY_ACTION = {PREBATTLE_ACTION_NAME.RANDOM: RandomEntryPoint,
 PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL: TutorialEntryPoint,
 PREBATTLE_ACTION_NAME.SANDBOX: SandboxEntryPoint,
 PREBATTLE_ACTION_NAME.RANKED: RankedEntryPoint,
 PREBATTLE_ACTION_NAME.BOOTCAMP: BootcampEntryPoint,
 PREBATTLE_ACTION_NAME.EPIC: EpicEntryPoint,
 PREBATTLE_ACTION_NAME.EPIC_FORCED: EpicForcedEntryPoint,
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE: br_entity.BattleRoyaleEntryPoint,
 PREBATTLE_ACTION_NAME.BATTLE_ROYALE_TOURNAMENT: br_tournament.BattleRoyaleTournamentEntryPoint,
 PREBATTLE_ACTION_NAME.MAPBOX: MapboxEntryPoint,
 PREBATTLE_ACTION_NAME.MAPS_TRAINING: MapsTrainingEntryPoint}

class PreQueueFactory(ControlFactory):

    @prequeue_storage_getter(QUEUE_TYPE.SANDBOX)
    def pveStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.RANKED)
    def rankedStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.EPIC)
    def epicStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.BATTLE_ROYALE)
    def battleRoyaleStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.MAPBOX)
    def mapboxStorage(self):
        return None

    @prequeue_storage_getter(QUEUE_TYPE.MAPS_TRAINING)
    def mapsTrainingStorage(self):
        return None

    def createEntry(self, ctx):
        LOG_ERROR('preQueue functional has not any entries')
        return None

    def createEntryByAction(self, action):
        return self._createEntryByAction(action, _SUPPORTED_ENTRY_BY_ACTION)

    def createEntity(self, ctx):
        if ctx.getCtrlType() == CTRL_ENTITY_TYPE.PREQUEUE:
            queueType = ctx.getEntityType()
            if queueType:
                created = self.__createByQueueType(queueType, ctx)
            else:
                created = self.__createDefaultEntity(ctx)
        else:
            created = self.__createByAccountState(ctx)
        return created

    def createStateEntity(self, entity):
        return FunctionalState(CTRL_ENTITY_TYPE.PREQUEUE, entity.getEntityType(), True, entity.isInQueue(), funcFlags=entity.getFunctionalFlags())

    def createLeaveCtx(self, flags=_FLAG.UNDEFINED, entityType=0):
        return LeavePreQueueCtx(waitingID='prebattle/leave', flags=flags, entityType=entityType)

    def __createByAccountState(self, ctx):
        queueType = gui.prb_control.prb_getters.getQueueType()
        return self.__createByQueueType(queueType, ctx) if queueType else self.__createDefaultEntity(ctx)

    def __createByQueueType(self, queueType, ctx):
        if ctx.getCtrlType() != CTRL_ENTITY_TYPE.PREQUEUE:
            return self.__createDefaultEntity(ctx)
        elif queueType in _SUPPORTED_QUEUES:
            clazz = _SUPPORTED_QUEUES[queueType]
            created = clazz()
            return created
        else:
            return None

    def __createDefaultEntity(self, ctx):
        if gui.prb_control.prb_getters.isInBootcampAccount():
            return BootcampEntity()
        else:
            created = self.__createDefaultByStorage(ctx)
            if created is None:
                created = RandomEntity()
            return created

    def __createDefaultByStorage(self, ctx):
        if self.pveStorage.isModeSelected():
            return SandboxEntity()
        elif self.rankedStorage.isModeSelected():
            return RankedEntity()
        elif self.epicStorage.isModeSelected():
            return EpicEntity()
        elif self.battleRoyaleStorage.isModeSelected():
            return br_entity.BattleRoyaleEntity()
        elif self.mapboxStorage.isModeSelected():
            return MapboxEntity()
        else:
            return MapsTrainingEntity() if self.mapsTrainingStorage.isModeSelected() else None
